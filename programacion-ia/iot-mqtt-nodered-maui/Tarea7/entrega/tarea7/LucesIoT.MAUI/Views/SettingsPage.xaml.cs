using LucesIoT.MAUI.ViewModels;

namespace LucesIoT.MAUI.Views;

public partial class SettingsPage : ContentPage
{
    private readonly SettingsViewModel _viewModel;

    public SettingsPage(SettingsViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
        _viewModel = viewModel;
    }

    // Al abrir esta pagina cargamos los modelos de LM Studio
    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await _viewModel.CargarModelosCommand.ExecuteAsync(null);
    }
}
