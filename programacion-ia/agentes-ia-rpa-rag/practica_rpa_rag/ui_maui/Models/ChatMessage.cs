namespace RpaChatApp.Models;

// Tipos de mensaje que pinta el chat.
public enum ChatRole
{
    User,
    Agent,
    ToolCall,
    ToolResult,
    Error,
}

public class ChatMessage
{
    public ChatRole Role { get; set; } = ChatRole.User;
    public string Sender { get; set; } = "";
    public string Content { get; set; } = "";
    public DateTime Timestamp { get; set; } = DateTime.Now;

    public bool IsFromCurrentUser => Role == ChatRole.User;

    // Propiedades de presentación derivadas del Role (no notifican: Role se asigna una vez).

    // Margen asimétrico: las burbujas propias pegan a la derecha.
    public Thickness BubbleMargin => IsFromCurrentUser
        ? new Thickness(80, 5, 5, 5)
        : new Thickness(5, 5, 80, 5);

    public LayoutOptions BubbleAlignment => IsFromCurrentUser
        ? LayoutOptions.End
        : LayoutOptions.Start;

    // Color por rol para distinguir agente / tool_call / tool_result a ojo.
    public Color BubbleColor => Role switch
    {
        ChatRole.User       => Color.FromArgb("#005C4B"),   // verde (tú)
        ChatRole.Agent      => Color.FromArgb("#1F2C34"),   // gris oscuro (agente)
        ChatRole.ToolCall   => Color.FromArgb("#2D3E50"),   // azul apagado
        ChatRole.ToolResult => Color.FromArgb("#1B3A2B"),   // verde apagado
        ChatRole.Error      => Color.FromArgb("#5A1A1A"),   // rojo oscuro
        _                   => Color.FromArgb("#1F2C34"),
    };

    public Color SenderColor => Role switch
    {
        ChatRole.User       => Color.FromArgb("#7AE582"),
        ChatRole.Agent      => Color.FromArgb("#E191EB"),
        ChatRole.ToolCall   => Color.FromArgb("#82B1FF"),
        ChatRole.ToolResult => Color.FromArgb("#A5D6A7"),
        ChatRole.Error      => Color.FromArgb("#FF8A80"),
        _                   => Color.FromArgb("#E9EDEF"),
    };

    public string TimeText => Timestamp.ToString("HH:mm");
}
