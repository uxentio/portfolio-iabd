using MauiRAG.ViewModels;

namespace MauiRAG.Modelos
{
    // chunk del RAG para trazabilidad
    public class ChunkInfo : BaseViewModel
    {
        public string Titulo { get; set; }
        public string TextoCompleto { get; set; }
        public string Score { get; set; }

        public string TextoCorto => TextoCompleto?.Length > 150
            ? TextoCompleto.Substring(0, 150) + "..."
            : TextoCompleto;

        private bool _expandido;
        public bool Expandido
        {
            get => _expandido;
            set
            {
                SetProperty(ref _expandido, value);
                OnPropertyChanged(nameof(TextoMostrado));
                OnPropertyChanged(nameof(ColorBorde));
                OnPropertyChanged(nameof(ColorFondo));
            }
        }

        public string TextoMostrado => Expandido ? TextoCompleto : TextoCorto;
        public Color ColorBorde => Expandido ? Color.FromArgb("#66BBFF") : Color.FromArgb("#444466");
        public Color ColorFondo => Expandido ? Color.FromArgb("#333355") : Color.FromArgb("#2A2A40");

        public string TituloDisplay => $"Doc: {Titulo}";
        public string ScoreDisplay => $"Score: {Score}";
    }
}
