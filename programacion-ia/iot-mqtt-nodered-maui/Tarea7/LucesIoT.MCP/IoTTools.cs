using ModelContextProtocol.Server;
using System.ComponentModel;

namespace LucesIoT.MCP;

// Extra opcional: un servidor MCP para controlar las luces desde Claude Desktop sin
// pasar por la app. La estructura la saque de un ejemplo llamado MovieTools que hay
// en los repos de MCP.
//    Model Context Protocol: https://modelcontextprotocol.io/
// Uso STDIO porque es lo mas simple y Claude Desktop lo pilla solo.
[McpServerToolType]
public class IoTTools
{
    private readonly NodeRedApiService _nodeRedService;

    public IoTTools(NodeRedApiService nodeRedService)
    {
        _nodeRedService = nodeRedService;
    }

    // una sola tool con parametros, asi puedo combinar cosas (LEDs, presets, morse)
    // sin tener que declarar mil funciones distintas
    [McpServerTool, Description(
        "Controla las 3 luces del dispositivo IoT. Estados por luz: off, on, dim, blink, fast, slow, fade. " +
        "Si modo_especial no es 'ninguno', se ignoran verde/roja/azul y se activa el modo " +
        "(semaforo, ola, morse). Para morse rellena tambien texto_morse y color_morse.")]
    public async Task<string> ControlarLuces(
        [Description("Estado de la luz verde: off, on, dim, blink, fast, slow, fade")] string verde = "off",
        [Description("Estado de la luz roja: off, on, dim, blink, fast, slow, fade")] string roja = "off",
        [Description("Estado de la luz azul: off, on, dim, blink, fast, slow, fade")] string azul = "off",
        [Description("Modo automatico: ninguno, semaforo, ola, morse")] string modo_especial = "ninguno",
        [Description("Texto a emitir en morse (solo si modo_especial=morse)")] string texto_morse = "",
        [Description("LED donde emitir morse: verde, roja, azul")] string color_morse = "verde")
    {
        bool ok;
        string resumen;

        if (modo_especial == "semaforo" || modo_especial == "ola")
        {
            ok = await _nodeRedService.SendPresetAsync(modo_especial);
            resumen = $"Modo {modo_especial.ToUpper()} activado.";
        }
        else if (modo_especial == "morse" && !string.IsNullOrWhiteSpace(texto_morse))
        {
            ok = await _nodeRedService.SendMorseAsync(texto_morse, color_morse);
            resumen = $"Emitiendo '{texto_morse}' en morse por la luz {color_morse}.";
        }
        else
        {
            ok = await _nodeRedService.SendLedStatesAsync(verde, roja, azul);
            resumen = $"Luces: verde={verde}, roja={roja}, azul={azul}.";
        }

        return ok ? resumen : "Error al conectar con Node-RED.";
    }

    [McpServerTool, Description("Info del sistema IoT: luces disponibles, modos, broker y topic")]
    public Task<string> EstadoSistema()
    {
        return Task.FromResult(
            "Sistema IoT activo.\n" +
            "Luces: verde, roja, azul.\n" +
            "Modos por luz: off, on, dim (tenue), blink (400ms), fast (150ms), slow (1s), fade (suave).\n" +
            "Modos especiales: semaforo, ola, morse.\n" +
            "Broker: test.mosquitto.org:1883\n" +
            "Topic comandos: iabd2425/esp32/led\n" +
            "Topic ACK (confirmaciones): iabd2425/esp32/ack");
    }
}
