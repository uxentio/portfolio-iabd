namespace RpaChatApp.Models;

// Config persistible de la app. POCO simple.
public class AppSettings
{
    // URL base de la FastAPI del agente. /chat lo añade el servicio.
    public string ApiBaseUrl { get; set; } = "http://localhost:8001";

    // thread_id que agrupa los turnos de una conversación.
    public string ThreadId { get; set; } = "default";

    // Backend del agente que se envía en cada petición a /chat. Permite
    // alternar entre los dos agentes que la API tiene cargados sin
    // reiniciar nada. Valores soportados: "langgraph" (default,
    // StateGraph custom con HITL) o "langchain" (create_agent con
    // middlewares). Si está vacío, la API usa su default.
    public string Backend { get; set; } = "langgraph";

    // Pausa sintética en ms entre eventos SSE consecutivos. Sirve para
    // ver la cadena tool_call -> tool_result -> answer paso a paso en la
    // demo aunque la API responda muy rápido. 0 = sin pausa. La API
    // limita a 5000 ms.
    public int DelayMs { get; set; } = 0;

    // Modelo de LM Studio que se envía en cada petición a /chat. La
    // lista de modelos disponibles la rellena la SettingsPage llamando
    // a GET /models de la API (que a su vez es proxy de /v1/models de
    // LM Studio). Si está vacío, la API mantiene el modelo activo.
    public string ModelName { get; set; } = "";

    // Lectura por voz (TTS) de la respuesta final del agente. Usa
    // TextToSpeech.Default.SpeakAsync de MAUI Essentials.
    public bool TtsEnabled { get; set; } = false;
}
