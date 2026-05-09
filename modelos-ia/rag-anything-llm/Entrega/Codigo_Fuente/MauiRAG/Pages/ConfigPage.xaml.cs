using MauiRAG.ViewModels;

namespace MauiRAG.Pages
{
    public partial class ConfigPage : ContentPage
    {
        private ConfigViewModel viewModel;

        public ConfigPage()
        {
            InitializeComponent();
            viewModel = new ConfigViewModel();
            BindingContext = viewModel;
        }

        protected override void OnAppearing()
        {
            base.OnAppearing();
            viewModel.CargarPreferencias();
        }
    }
}
