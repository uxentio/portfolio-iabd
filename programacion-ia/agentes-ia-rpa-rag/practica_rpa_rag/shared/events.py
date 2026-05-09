# Tipos de eventos que la API emite por SSE y que los middlewares
# publican en el UIEventBus. Centralizados aquí para que ningún punto
# del código emita un literal y se cuelen typos como "toolcall" en
# vez de "tool_call". El equivalente C# vive en
# ui_maui/Services/LLMService.cs::AgentEventType.


class AgentEventType:
    META = "meta"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ANSWER = "answer"
    ERROR = "error"
    DONE = "done"
