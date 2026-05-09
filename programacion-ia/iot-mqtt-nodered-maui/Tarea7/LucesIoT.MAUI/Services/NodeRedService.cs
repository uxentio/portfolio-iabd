using System.Text;
using System.Text.Json;

namespace LucesIoT.MAUI.Services;

// Esto habla con Node-RED por HTTP. Al principio mandaba un string tipo "encender_verde"
// y listo, pero cuando meti los 7 estados y los modos especiales se me quedo corto,
// asi que ahora va todo en JSON. Node-RED luego lo reempaqueta y lo publica por MQTT.
public class NodeRedService
{
    private readonly HttpClient _httpClient;

    // ojo: el ejemplo de partida usaba 1881, pero el default de Node-RED es 1880
    public string Url { get; set; } = "http://127.0.0.1:1880/encender";

    // estos no los usa este servicio, pero los guardo aqui para el panel SISTEMA de la UI
    public string MqttBroker { get; set; } = "test.mosquitto.org:1883";
    public string MqttTopic { get; set; } = "iabd2425/esp32/led";

    public NodeRedService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    // manda el JSON tipo {"verde":"on","roja":"off","azul":"blink"} a Node-RED
    public async Task<bool> SendCommandAsync(Dictionary<string, string> ledStates)
    {
        try
        {
            string json = JsonSerializer.Serialize(ledStates);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(Url, content);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            // pillo HttpRequestException (Node-RED caido) y TaskCanceledException (timeout)
            // si no capturo el timeout tambien, la app peta si Node-RED tarda mucho
            return false;
        }
    }

    // atajo para no montar el diccionario a mano, lo uso desde los botones manuales
    public async Task<bool> SendCommandAsync(string verde, string roja, string azul)
    {
        var states = new Dictionary<string, string>
        {
            ["verde"] = verde,
            ["roja"] = roja,
            ["azul"] = azul
        };
        return await SendCommandAsync(states);
    }

    // manda {"preset":"semaforo"} a Node-RED para activar secuencias automaticas en el ESP32
    public async Task<bool> SendPresetAsync(string nombre)
    {
        try
        {
            string json = JsonSerializer.Serialize(new { preset = nombre });
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync(Url, content);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    // manda {"morse":"SOS","color":"verde"} para emitir un texto en morse
    public async Task<bool> SendMorseAsync(string texto, string color)
    {
        try
        {
            string json = JsonSerializer.Serialize(new { morse = texto, color });
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _httpClient.PostAsync(Url, content);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }
}
