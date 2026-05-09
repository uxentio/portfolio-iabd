using RpaChatApp.ViewModels;

namespace RpaChatApp;

public partial class SettingsPage : ContentPage
{
    private SettingsViewModel _viewModel;

    public SettingsPage(SettingsViewModel viewModel)
    {
        InitializeComponent();
        // El VM se recibe por constructor (no en XAML) porque necesita la AppSettings actual.
        _viewModel = viewModel;
        BindingContext = _viewModel;

        // El cierre real (PopModalAsync) lo hace la View; el VM solo emite el evento.
        _viewModel.CloseRequested += OnCloseRequested;
    }

    private async void OnCloseRequested()
    {
        await Navigation.PopModalAsync();
    }
}
