namespace MauiRAG.Modelos
{
    // mensaje del chat
    public class MensajeChat
    {
        public string Texto { get; set; }
        public bool EsUsuario { get; set; }
        public string Hora { get; set; }

        // para el binding en la vista
        public string Remitente => EsUsuario ? "Tu" : "Asistente";
        public Color ColorFondo => EsUsuario ? Color.FromArgb("#DCF8C6") : Color.FromArgb("#E8E8E8");
        public Thickness Margen => EsUsuario ? new Thickness(60, 2, 5, 2) : new Thickness(5, 2, 60, 2);
    }
}
