namespace LucesIoT.MAUI.Models;

// Un mensaje del chat (del usuario o del bot)
public class ChatMessage
{
    public string Text { get; set; } = string.Empty;
    public bool IsUser { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.Now;
}
