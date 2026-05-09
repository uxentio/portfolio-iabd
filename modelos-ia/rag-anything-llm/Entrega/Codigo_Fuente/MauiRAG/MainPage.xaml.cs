using MauiRAG.Modelos;
using MauiRAG.ViewModels;

namespace MauiRAG
{
    public partial class MainPage : ContentPage
    {
        private ChatViewModel viewModel;
        private double alturaTrazabilidad = 180;

        public MainPage()
        {
            InitializeComponent();

            viewModel = new ChatViewModel();
            BindingContext = viewModel;

            // drag para redimensionar la trazabilidad
            var panGesture = new PanGestureRecognizer();
            panGesture.PanUpdated += (s, args) =>
            {
                if (args.StatusType == GestureStatus.Running)
                {
                    double nuevaAltura = alturaTrazabilidad - args.TotalY;
                    nuevaAltura = Math.Clamp(nuevaAltura, 80, 500);
                    frameTrazabilidad.HeightRequest = nuevaAltura;
                }
                else if (args.StatusType == GestureStatus.Completed)
                {
                    alturaTrazabilidad = frameTrazabilidad.HeightRequest;
                }
            };
            handleTrazabilidad.GestureRecognizers.Add(panGesture);

            // scroll al ultimo mensaje
            viewModel.Mensajes.CollectionChanged += (s, args) =>
            {
                if (viewModel.Mensajes.Count > 0)
                {
                    listaMensajes.ScrollTo(viewModel.Mensajes.Count - 1, position: ScrollToPosition.End, animate: true);
                }
            };
        }

        protected override async void OnAppearing()
        {
            base.OnAppearing();
            await viewModel.CargarWorkspaces();
        }

        // expandir/contraer chunk al tocar
        private void OnChunkTapped(object sender, EventArgs e)
        {
            if (sender is VisualElement element && element.BindingContext is ChunkInfo chunk)
            {
                viewModel.ToggleChunkCommand.Execute(chunk);
            }
        }

        // enter en el entry
        private async void btnEnviar_Click(object sender, EventArgs e)
        {
            if (viewModel.WorkspaceSeleccionado < 0)
            {
                await DisplayAlert("Aviso", "Selecciona un workspace primero", "OK");
                return;
            }
            await viewModel.EnviarMensaje();
        }
    }
}
