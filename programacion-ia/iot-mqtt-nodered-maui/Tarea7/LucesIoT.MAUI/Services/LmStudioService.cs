using System.Text;
using System.Text.Json;

namespace LucesIoT.MAUI.Services;

// el resultado puede ser: estados de luces, un preset, o texto normal del LLM
public class LmStudioResult
{
    public Dictionary<string, string>? LedStates { get; set; }
    public string? Preset { get; set; }          // "semaforo", "ola", "ninguno"
    public string? MorseText { get; set; }       // texto a emitir en morse
    public string? MorseColor { get; set; }      // verde/roja/azul
    public string? TextResponse { get; set; }
    public bool IsToolCall => LedStates != null || Preset != null || MorseText != null;
}

// Esto habla con LM Studio. Lo he sacado del ejemplo de partida (MainWindow.xaml.cs)
// pero pasado a MAUI y puesto como servicio para poder inyectarlo en el ViewModel.
// Uso System.Text.Json porque ya viene con .NET y me ahorro un NuGet, y encima es
// el que usan ahora en los docs de Microsoft:
//    https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/overview
// La API de LM Studio es compatible con OpenAI (mismos endpoints):
//    https://lmstudio.ai/docs/api
public class LmStudioService
{
    private readonly HttpClient _httpClient;

    public string UrlBase { get; set; } = "http://127.0.0.1:1234";
    public string ModelName { get; set; } = "qwen3.5-0.8b";

    // NOTA: antes guardaba aqui un historial y lo mandaba al LLM en cada llamada, pero con
    // Qwen 0.8B se hacia la picha un lio y mezclaba respuestas viejas con nuevas. Lo quite
    // del prompt (ver SendAsync) y el historial ahora solo vive en el ViewModel para la UI.

    // con modelos pequeños hay que ser borde y poner REGLA OBLIGATORIA en mayusculas
    // o a veces pasa de ti y contesta con texto en vez de llamar a la tool, me paso mil veces
    private static readonly object SystemMessage = new
    {
        role = "system",
        content = "Eres un asistente IoT que controla 3 luces fisicas (verde, roja, azul). " +
                  "Tienes UNA SOLA herramienta: controlar_luces, con estos parametros:\n" +
                  "- verde, roja, azul: estado de cada luz, uno de: " +
                  "\"off\" (apagada), \"on\" (encendida fija), \"dim\" (brillo tenue), " +
                  "\"blink\" (parpadeo 400ms), \"fast\" (parpadeo rapido 150ms), " +
                  "\"slow\" (parpadeo lento 1s), \"fade\" (sube y baja suave).\n" +
                  "- modo_especial: opcional, uno de \"ninguno\" (por defecto), \"semaforo\", \"ola\", \"morse\". " +
                  "Si pones semaforo/ola/morse, los estados verde/roja/azul se ignoran.\n" +
                  "- texto_morse: solo si modo_especial=morse, el texto a emitir (ej. SOS, OK).\n" +
                  "- color_morse: solo si modo_especial=morse, en que LED emitir (verde/roja/azul).\n" +
                  "REGLA OBLIGATORIA: cuando el usuario pida tocar luces, SIEMPRE llama a controlar_luces. " +
                  "Mapeo de intenciones: 'tenue/suave/bajito' -> dim; 'rapido/deprisa' -> fast; " +
                  "'lento/despacio' -> slow; 'respira/pulsa/fade' -> fade; " +
                  "'parpadea/intermitente' -> blink; 'encendida/fija' -> on; 'apagada' -> off. " +
                  "Si solo mencionan una luz en modo normal, pon esa al estado pedido y las demas a off. " +
                  "Si dice 'semaforo' -> modo_especial=semaforo. Si dice 'la ola' -> modo_especial=ola. " +
                  "Si dice 'morse' o 'emite XXX en morse' -> modo_especial=morse, texto_morse=XXX. " +
                  "Si pregunta algo no relacionado con luces, responde en texto normal en español."
    };

    // al principio tenia 4 tools sueltas. Me pare a pensarlo: con 4 sueltas no podia
    // encender dos luces a la vez ni combinar modos. Lo refactorice a UNA sola herramienta
    // con parametros, mucho mas flexible. Despues le fui metiendo cosas: los 7 estados,
    // el modo_especial y los dos campos del morse.
    // ref: https://platform.openai.com/docs/guides/function-calling
    private static readonly string[] EstadosValidos = { "off", "on", "dim", "blink", "fast", "slow", "fade" };
    private static readonly string[] ModosEspeciales = { "ninguno", "semaforo", "ola", "morse" };
    private static readonly string[] ColoresMorse = { "verde", "roja", "azul" };

    private static readonly object[] Tools = new object[]
    {
        new {
            type = "function",
            function = new {
                name = "controlar_luces",
                description = "Controla las 3 luces del dispositivo IoT. Cada luz acepta: off, on, dim, blink, fast, slow, fade. " +
                              "Si pones modo_especial distinto de 'ninguno' se ignoran verde/roja/azul y se activa ese modo " +
                              "(semaforo = secuencia verde-ambar-rojo; ola = LEDs por turnos; morse = emite texto_morse en color_morse).",
                parameters = new {
                    type = "object",
                    properties = new {
                        verde = new {
                            type = "string",
                            description = "Estado de la luz verde",
                            @enum = EstadosValidos
                        },
                        roja = new {
                            type = "string",
                            description = "Estado de la luz roja",
                            @enum = EstadosValidos
                        },
                        azul = new {
                            type = "string",
                            description = "Estado de la luz azul",
                            @enum = EstadosValidos
                        },
                        modo_especial = new {
                            type = "string",
                            description = "Modo automatico. Si no es 'ninguno', ignora verde/roja/azul y activa el modo.",
                            @enum = ModosEspeciales
                        },
                        texto_morse = new {
                            type = "string",
                            description = "Solo si modo_especial=morse. Texto a emitir (letras A-Z, numeros, espacios, max 30)."
                        },
                        color_morse = new {
                            type = "string",
                            description = "Solo si modo_especial=morse. En que LED emitir el morse.",
                            @enum = ColoresMorse
                        }
                    },
                    required = new[] { "verde", "roja", "azul" }
                }
            }
        }
    };

    public LmStudioService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    // esto es lo que antes era SendInstructionToLLM, pero ya con tool_calls de verdad
    public async Task<LmStudioResult> SendAsync(string userMessage)
    {
        // Mando cada mensaje SIN historial previo. Con modelos pequenos (0.8B) si les
        // das contexto largo se lian y mezclan respuestas anteriores con la nueva. Asi
        // cada comando se interpreta limpio. El historial para la UI lo lleva el ViewModel.
        var messages = new List<object> {
            SystemMessage,
            new { role = "user", content = userMessage }
        };

        // si parece comando de luces fuerzo tool_choice = required
        // me paso que al preguntarle "que puedes hacer?" encendia una luz random, tarde en pillarlo
        string msgLower = userMessage.ToLower();
        bool tienePalabrasLuz = msgLower.Contains("encien") || msgLower.Contains("apaga") ||
                            msgLower.Contains("prende") || msgLower.Contains("luz") ||
                            msgLower.Contains("led") || msgLower.Contains("roj") ||
                            msgLower.Contains("verde") || msgLower.Contains("azul") ||
                            msgLower.Contains("intermiten") || msgLower.Contains("blink") ||
                            msgLower.Contains("parpadea") || msgLower.Contains("fij") ||
                            msgLower.Contains("tenue") || msgLower.Contains("suave") ||
                            msgLower.Contains("rapido") || msgLower.Contains("lento") ||
                            msgLower.Contains("respira") || msgLower.Contains("pulsa") ||
                            msgLower.Contains("fade") || msgLower.Contains("semaforo") ||
                            msgLower.Contains("semáforo") || msgLower.Contains("brillo") ||
                            msgLower.Contains(" ola") || msgLower.StartsWith("ola ") ||
                            msgLower.Contains("morse");
        bool esPregunta = msgLower.Contains("?") || msgLower.Contains("qué") ||
                          msgLower.Contains("que ") || msgLower.Contains("cuál") ||
                          msgLower.Contains("cuáles") || msgLower.Contains("puedes") ||
                          msgLower.Contains("cómo") || msgLower.Contains("cuantas");
        bool esComandoLuz = tienePalabrasLuz && !esPregunta;

        object requestData;
        if (esComandoLuz)
        {
            requestData = new
            {
                model = ModelName,
                messages,
                tools = Tools,
                tool_choice = "required"
            };
        }
        else
        {
            requestData = new
            {
                model = ModelName,
                messages,
                tools = Tools
            };
        }

        string json = JsonSerializer.Serialize(requestData);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync($"{UrlBase}/v1/chat/completions", content);
        string responseBody = await response.Content.ReadAsStringAsync();

        using var doc = JsonDocument.Parse(responseBody);
        var root = doc.RootElement;
        var message = root.GetProperty("choices")[0].GetProperty("message");

        // miro si vino tool_call, misma idea que el ejemplo pero parseando los argumentos
        if (message.TryGetProperty("tool_calls", out var toolCalls) &&
            toolCalls.GetArrayLength() > 0)
        {
            var firstCall = toolCalls[0];
            string argsJson = firstCall.GetProperty("function").GetProperty("arguments").GetString() ?? "{}";
            using var args = JsonDocument.Parse(argsJson);

            // miro si el LLM eligio un modo_especial (semaforo/ola/morse)
            string modo = LeerCampo(args.RootElement, "modo_especial", ModosEspeciales, "ninguno");

            if (modo == "semaforo" || modo == "ola")
            {
                return new LmStudioResult { Preset = modo };
            }

            if (modo == "morse")
            {
                string texto = args.RootElement.TryGetProperty("texto_morse", out var t)
                    ? (t.GetString() ?? "") : "";
                // si el LLM se olvida del texto o manda cadena vacia, emito SOS por defecto
                if (string.IsNullOrWhiteSpace(texto)) texto = "SOS";
                // limito a 30 chars por si se flipa y me manda una novela
                if (texto.Length > 30) texto = texto.Substring(0, 30);
                string color = LeerCampo(args.RootElement, "color_morse", ColoresMorse, "verde");
                return new LmStudioResult { MorseText = texto, MorseColor = color };
            }

            // modo normal: 3 estados por LED
            var ledStates = new Dictionary<string, string>
            {
                ["verde"] = LeerEstado(args.RootElement, "verde"),
                ["roja"]  = LeerEstado(args.RootElement, "roja"),
                ["azul"]  = LeerEstado(args.RootElement, "azul")
            };

            return new LmStudioResult { LedStates = ledStates };
        }

        // no hubo tool_call, devuelvo el texto tal cual
        string? textContent = message.TryGetProperty("content", out var contentProp)
            ? contentProp.GetString()
            : "Sin respuesta.";

        return new LmStudioResult { TextResponse = textContent };
    }

    // por si el LLM se inventa "encendido", "ON", "true" o algo raro, lo mando a off y listo
    // asi el ESP32 no recibe cosas que no sabe interpretar
    private static string LeerEstado(JsonElement args, string key)
        => LeerCampo(args, key, EstadosValidos, "off");

    // lo mismo que LeerEstado pero para cualquier campo enum
    private static string LeerCampo(JsonElement args, string key, string[] permitidos, string fallback)
    {
        if (!args.TryGetProperty(key, out var prop)) return fallback;
        string? val = prop.GetString();
        if (string.IsNullOrEmpty(val)) return fallback;
        val = val.ToLowerInvariant();
        // normalizo tildes comunes que se inventa el modelo
        val = val.Replace("á", "a").Replace("é", "e").Replace("í", "i")
                 .Replace("ó", "o").Replace("ú", "u");
        return permitidos.Contains(val) ? val : fallback;
    }

    // para rellenar el Picker de Settings con los modelos que tenga cargados LM Studio
    public async Task<List<string>> ObtenerModelosDisponiblesAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{UrlBase}/v1/models");
            if (!response.IsSuccessStatusCode)
                return new List<string>();

            string body = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(body);
            var data = doc.RootElement.GetProperty("data");

            var modelos = new List<string>();
            foreach (var item in data.EnumerateArray())
            {
                if (item.TryGetProperty("id", out var id))
                    modelos.Add(id.GetString()!);
            }
            return modelos;
        }
        catch
        {
            return new List<string>();
        }
    }
}
