using System.Net.Http;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using RpaChatApp.Models;

namespace RpaChatApp.Services;

// Tipos de eventos que la API emite por SSE. Centralizados aquí para
// evitar que se cuelen typos (`"toolcall"` en vez de `"tool_call"`) y
// para tener un único punto donde añadir uno nuevo.
public static class AgentEventType
{
    public const string Meta = "meta";
    public const string ToolCall = "tool_call";
    public const string ToolResult = "tool_result";
    public const string Answer = "answer";
    public const string Error = "error";
    public const string Done = "done";
}

// Cliente HTTP que habla con la FastAPI del agente (POST /chat, SSE).
// El archivo se llama LLMService.cs por motivos históricos; la clase es AgentApiService.
public class AgentApiService
{
    private readonly HttpClient _httpClient;
    private AppSettings _settings;

    public AgentApiService(AppSettings settings)
    {
        // Timeout 5 min: un turno encadena RAG + extracción + Playwright con slow_mo.
        _httpClient = new HttpClient { Timeout = TimeSpan.FromMinutes(5) };
        _settings = settings;
    }

    public void UpdateSettings(AppSettings settings) => _settings = settings;

    // Helpers para construir URLs consistentes contra la API. Centralizar el
    // TrimEnd('/') aquí evita drift si el usuario configura la URL con o sin
    // slash final.
    private string BuildUrl(string path) =>
        $"{_settings.ApiBaseUrl.TrimEnd('/')}/{path.TrimStart('/')}";

    // GET genérico que devuelve JObject parseado o null si la API falla.
    // Centraliza el patrón GET → status check → ReadAsStringAsync → Parse.
    private async Task<JObject?> GetJsonAsync(string path, CancellationToken ct = default)
    {
        try
        {
            using var resp = await _httpClient.GetAsync(BuildUrl(path), ct);
            if (!resp.IsSuccessStatusCode) return null;
            var body = await resp.Content.ReadAsStringAsync(ct);
            return JObject.Parse(body);
        }
        catch { return null; }
    }

    // --- Endpoints de observabilidad: alimentan la pantalla de Logs ---

    public record LogSnapshot(string Path, long SizeBytes, IReadOnlyList<string> Lines);
    public record FileItem(string Name, long SizeBytes, double Mtime);

    public async Task<LogSnapshot?> GetLogsAsync(int tail = 200, CancellationToken ct = default)
    {
        var jo = await GetJsonAsync($"logs?tail={tail}", ct);
        if (jo == null) return null;
        var lines = (jo["lines"] as JArray)?.Select(t => t?.ToString() ?? "").ToList() ?? new();
        return new LogSnapshot(
            jo["path"]?.ToString() ?? "",
            jo["size_bytes"]?.Value<long>() ?? 0,
            lines
        );
    }

    public async Task<IReadOnlyList<FileItem>> GetFileListAsync(string endpoint, CancellationToken ct = default)
    {
        var jo = await GetJsonAsync(endpoint, ct);
        if (jo == null) return Array.Empty<FileItem>();
        var arr = jo["items"] as JArray;
        return arr?.Select(t => new FileItem(
            t["name"]?.ToString() ?? "",
            t["size_bytes"]?.Value<long>() ?? 0,
            t["mtime"]?.Value<double>() ?? 0
        )).ToList() ?? new List<FileItem>();
    }

    public string ScreenshotUrl(string name) => BuildUrl($"screenshots/{Uri.EscapeDataString(name)}");

    // Lista de modelos disponibles, consultada al endpoint /models de la API
    // (que a su vez hace proxy a /v1/models de LM Studio). Devuelve la
    // pareja (lista, modelo activo en el servidor) o lista vacía y null
    // si la API no responde.
    public async Task<(IReadOnlyList<string> Models, string? Current)> GetAvailableModelsAsync(
        CancellationToken ct = default)
    {
        var jo = await GetJsonAsync("models", ct);
        if (jo == null) return (Array.Empty<string>(), null);
        var available = jo["available"] as JArray;
        var lista = available?.Select(t => t?.ToString() ?? "").Where(s => !string.IsNullOrEmpty(s)).ToList()
                    ?? new List<string>();
        var current = jo["current"]?.ToString();
        return (lista, string.IsNullOrEmpty(current) ? null : current);
    }

    // record por inmutabilidad e igualdad estructural sin escribir el boilerplate.
    public record AgentEvent(string Type, string Content, string? ToolName, JObject? RawArgs);

    public async Task SendMessageAsync(
        string userMessage,
        Action<AgentEvent> onEvent,
        CancellationToken ct = default)
    {
        var url = BuildUrl("chat");

        var payload = new
        {
            thread_id = _settings.ThreadId,
            message = userMessage,
            // backend opcional: si está vacío en settings, lo manda como
            // null y la API usa su default (AGENT_BACKEND env var).
            backend = string.IsNullOrWhiteSpace(_settings.Backend) ? null : _settings.Backend.Trim(),
            // ralentizador sintético entre eventos SSE para ver paso a
            // paso la cadena en la demo. La API trunca a [0, 5000].
            delay_ms = Math.Max(0, _settings.DelayMs),
            // modelo opcional: si difiere del actual en la API, se
            // reconstruyen los dos agentes con el nuevo. Si está vacío
            // se mantiene el modelo activo del servidor.
            model = string.IsNullOrWhiteSpace(_settings.ModelName) ? null : _settings.ModelName.Trim(),
        };

        using var req = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json"),
        };
        req.Headers.Accept.TryParseAdd("text/event-stream");

        HttpResponseMessage resp;
        try
        {
            // ResponseHeadersRead: el await termina al recibir cabeceras (imprescindible para SSE).
            resp = await _httpClient.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct);
        }
        catch (Exception ex)
        {
            onEvent(new AgentEvent("error", $"No he podido conectar con la API: {ex.Message}", null, null));
            return;
        }

        if (!resp.IsSuccessStatusCode)
        {
            string body = "";
            try { body = await resp.Content.ReadAsStringAsync(ct); } catch { }
            onEvent(new AgentEvent("error", $"La API respondió {(int)resp.StatusCode}: {body}", null, null));
            return;
        }

        await using var stream = await resp.Content.ReadAsStreamAsync(ct);
        using var reader = new StreamReader(stream, Encoding.UTF8);

        // Parser SSE manual: bloques separados por línea en blanco con líneas
        // "event: <tipo>" y "data: <payload>".
        string? currentEvent = null;
        var dataBuffer = new StringBuilder();

        while (!reader.EndOfStream && !ct.IsCancellationRequested)
        {
            var line = await reader.ReadLineAsync();
            if (line == null) break;

            if (line.Length == 0)
            {
                // fin del bloque: emito si hay algo acumulado
                if (currentEvent != null && dataBuffer.Length > 0)
                {
                    EmitEvent(currentEvent, dataBuffer.ToString(), onEvent);
                }
                currentEvent = null;
                dataBuffer.Clear();
                continue;
            }

            if (line.StartsWith("event:"))
            {
                currentEvent = line.Substring(6).Trim();
            }
            else if (line.StartsWith("data:"))
            {
                if (dataBuffer.Length > 0) dataBuffer.Append('\n');
                dataBuffer.Append(line.Substring(5).TrimStart());
            }
            // otros prefijos (id, retry, comentarios) los ignoro
        }
    }

    private static void EmitEvent(string evt, string rawData, Action<AgentEvent> onEvent)
    {
        JObject? data = null;
        try { data = JObject.Parse(rawData); } catch { /* no JSON */ }

        string content = "";
        string? toolName = null;

        switch (evt)
        {
            case AgentEventType.ToolCall:
                toolName = data?["name"]?.ToString();
                content = $"{toolName}({data?["args"]?.ToString(Formatting.None) ?? "{}"})";
                break;

            case AgentEventType.ToolResult:
                toolName = data?["name"]?.ToString();
                content = data?["content"]?.ToString() ?? rawData;
                break;

            case AgentEventType.Answer:
                content = data?["content"]?.ToString() ?? rawData;
                break;

            case AgentEventType.Done:
                content = "";
                break;

            default:
                content = rawData;
                break;
        }

        onEvent(new AgentEvent(evt, content, toolName, data));
    }
}
