using MauiRAG.Modelos;
using MauiRAG.ViewModels;

namespace MauiRAG.Pages
{
    public partial class WorkspacesPage : ContentPage
    {
        private WorkspacesViewModel viewModel;

        public WorkspacesPage()
        {
            InitializeComponent();
            viewModel = new WorkspacesViewModel();
            BindingContext = viewModel;
        }

        protected override async void OnAppearing()
        {
            base.OnAppearing();
            await viewModel.CargarWorkspaces();
        }

        // renombrar (necesita prompt)
        private async void btnRenombrar_Click(object sender, EventArgs e)
        {
            var btn = sender as Button;
            var workspace = btn?.CommandParameter as WorkspaceItem;
            if (workspace == null) return;

            string nuevoNombre = await DisplayPromptAsync("Renombrar",
                $"Nuevo nombre para '{workspace.Nombre}':", "Aceptar", "Cancelar");
            if (string.IsNullOrWhiteSpace(nuevoNombre)) return;

            bool ok = await viewModel.RenombrarWorkspace(workspace.Slug, nuevoNombre);
            if (!ok)
                await DisplayAlert("Error", "No se pudo renombrar", "OK");
        }

        // eliminar (necesita confirmacion)
        private async void btnEliminar_Click(object sender, EventArgs e)
        {
            var btn = sender as Button;
            var workspace = btn?.CommandParameter as WorkspaceItem;
            if (workspace == null) return;

            bool confirmar = await DisplayAlert("Confirmar",
                $"Seguro que quieres eliminar '{workspace.Nombre}'?", "Si", "No");
            if (!confirmar) return;

            bool ok = await viewModel.EliminarWorkspace(workspace.Slug);
            if (!ok)
                await DisplayAlert("Error", "No se pudo eliminar", "OK");
        }
    }
}
