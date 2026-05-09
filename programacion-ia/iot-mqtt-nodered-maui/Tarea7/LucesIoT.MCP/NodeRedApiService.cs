using System.Text;
using System.Text.Json;

namespace LucesIoT.MCP;

// Version del servicio de Node-RED para el servidor MCP. La logica es basicamente
// la misma que en LucesIoT.MAUI pero la he duplicado aposta para que este proyecto
// sea independiente y pueda compilarse/ejecutarse sin tener que arrastrar la app
// MAUI completa (que tiene un monton de dependencias de plataforma).
public class NodeRedApiService
{
    private readonly HttpClient _httpClient;
    private readonly string _nodeRedUrl;

    // la URL se puede pasar por variable de entorno NODERED_URL
    // si no, tira del default, asi no hay que recompilar para cambiarla
    public NodeRedApiService(HttpClient httpClient)
    {
        _httpClient = httpClient;
        _nodeRedUrl = Environment.GetEnvironmentVariable("NODERED_URL")
                      ?? "http://127.0.0.1:1880/encender";
    }

    // manda el JSON con los 3 estados a Node-RED
    public async Task<bool> SendLedStatesAsync(string verde, string roja, string azul)
    {
        try
        {
            var payload = new { verde, roja, azul };
            string json = JsonSerializer.Serialize(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(_nodeRedUrl, content);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    // activa un preset en el ESP32 (semaforo, ola, ninguno)
    public async Task<bool> SendPresetAsync(string nombre)
    {
        try
        {
            string json = JsonSerializer.Serialize(new { preset = nombre });
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync(_nodeRedUrl, content);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    // emite un texto en morse por el LED indicado
    public async Task<bool> SendMorseAsync(string texto, string color)
    {
        try
        {
            string json = JsonSerializer.Serialize(new { morse = texto, color });
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync(_nodeRedUrl, content);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }
}
