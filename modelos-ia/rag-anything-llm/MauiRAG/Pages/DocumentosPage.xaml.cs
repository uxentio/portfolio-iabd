using MauiRAG.Modelos;
using MauiRAG.Servicios;
using MauiRAG.ViewModels;

namespace MauiRAG.Pages
{
    public partial class DocumentosPage : ContentPage
    {
        private DocumentosViewModel viewModel;

        public DocumentosPage()
        {
            InitializeComponent();
            viewModel = new DocumentosViewModel();
            BindingContext = viewModel;
        }

        protected override async void OnAppearing()
        {
            base.OnAppearing();
            await viewModel.CargarWorkspaces();
            await viewModel.CargarDocumentos();
        }

        // file picker
        private async void btnSeleccionar_Click(object sender, EventArgs e)
        {
            try
            {
                var resultado = await FilePicker.Default.PickAsync(new PickOptions
                {
                    PickerTitle = "Selecciona un documento o imagen",
                    FileTypes = new FilePickerFileType(new Dictionary<DevicePlatform, IEnumerable<string>>
                    {
                        { DevicePlatform.WinUI, new[] { ".pdf", ".txt", ".csv", ".docx", ".md",
                            ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp" } }
                    })
                });

                if (resultado != null)
                    viewModel.ArchivoSeleccionado = resultado.FullPath;
            }
            catch (Exception ex)
            {
                await DisplayAlert("Error", "Error al seleccionar archivo: " + ex.Message, "OK");
            }
        }

        private async void btnSubir_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(viewModel.ArchivoSeleccionado))
            {
                await DisplayAlert("Aviso", "Primero selecciona un archivo", "OK");
                return;
            }

            if (viewModel.WorkspaceSeleccionado < 0)
            {
                await DisplayAlert("Aviso", "Selecciona un workspace", "OK");
                return;
            }

            await viewModel.SubirDocumento();
        }

        // eliminar doc individual
        private async void btnEliminarDoc_Click(object sender, EventArgs e)
        {
            var btn = sender as Button;
            var doc = btn?.CommandParameter as DocumentoItem;
            if (doc == null) return;

            bool confirmar = await DisplayAlert("Confirmar",
                $"Seguro que quieres eliminar '{doc.Nombre}'?", "Si", "No");
            if (!confirmar) return;

            bool ok = await viewModel.EliminarDocumento(doc);
            if (!ok)
                await DisplayAlert("Error", "No se pudo eliminar el documento", "OK");
        }

        // checkbox changed
        private void chkDoc_CheckedChanged(object sender, CheckedChangedEventArgs e)
        {
            var chk = sender as CheckBox;
            var doc = chk?.BindingContext as DocumentoItem;
            if (doc == null) return;

            viewModel.ToggleSeleccionDocumento(doc, e.Value);
        }

        // procesar URL de YouTube
        private async void btnProcesarYouTube_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(viewModel.UrlYouTube))
            {
                await DisplayAlert("Aviso", "Pega una URL de YouTube primero", "OK");
                return;
            }

            if (viewModel.WorkspaceSeleccionado < 0)
            {
                await DisplayAlert("Aviso", "Selecciona un workspace", "OK");
                return;
            }

            if (!PythonProcessorService.EsUrlYouTube(viewModel.UrlYouTube))
            {
                await DisplayAlert("Aviso", "La URL no parece ser de YouTube", "OK");
                return;
            }

            await viewModel.ProcesarYSubirYouTube();
        }

        // eliminar seleccionados
        private async void btnEliminarSeleccion_Click(object sender, EventArgs e)
        {
            int count = viewModel.DocumentosSeleccionados.Count;
            if (count == 0) return;

            bool confirmar = await DisplayAlert("Confirmar",
                $"Seguro que quieres eliminar {count} documento(s)?", "Si", "No");
            if (!confirmar) return;

            bool ok = await viewModel.EliminarSeleccionados();
            if (!ok)
                await DisplayAlert("Error", "No se pudieron eliminar los documentos", "OK");
        }
    }
}
