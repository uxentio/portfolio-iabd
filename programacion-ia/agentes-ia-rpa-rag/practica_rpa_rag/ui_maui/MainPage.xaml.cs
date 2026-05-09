using RpaChatApp.ViewModels;

namespace RpaChatApp;

public partial class MainPage : ContentPage
{
    private readonly MainViewModel _viewModel;

    public MainPage()
    {
        InitializeComponent();
        // El BindingContext lo crea el XAML; aquí guardo la referencia tipada.
        _viewModel = (MainViewModel)BindingContext;

        // ScrollTo es API de la View (CollectionView), por eso vive aquí.
        _viewModel.ScrollRequested += OnScrollRequested;
    }

    private async void OnScrollRequested()
    {
        // Delay corto para que CollectionChanged materialice la burbuja antes del ScrollTo.
        await Task.Delay(80);
        if (_viewModel.Messages.Count > 0)
        {
            chatCollectionView.ScrollTo(_viewModel.Messages.Count - 1);
        }
    }

    // Navegación: responsabilidad de la View.
    private async void OnLogsClicked(object sender, EventArgs e)
    {
        try
        {
            var logsVM = new LogsViewModel(_viewModel.Api);
            var logsPage = new LogsPage(logsVM);
            await Navigation.PushModalAsync(new NavigationPage(logsPage));
        }
        catch (Exception ex)
        {
            await DisplayAlert("Error", $"No se pudo abrir la pantalla de logs: {ex.Message}", "OK");
        }
    }

    private async void OnSettingsClicked(object sender, EventArgs e)
    {
        try
        {
            // Construyo el VM de ajustes y me suscribo a SettingsSaved para volcar al MainVM.
            // Le paso el AgentApiService del MainVM para que SettingsVM pueda
            // consultar /models al abrirse y rellenar el Picker dinámico.
            var settingsVM = new SettingsViewModel(_viewModel.Settings, _viewModel.Api);
            settingsVM.SettingsSaved += async (newSettings) =>
            {
                await _viewModel.ApplySettings(newSettings);
            };

            // NavigationPage envolviendo la modal: trae su propia barra.
            var settingsPage = new SettingsPage(settingsVM);
            await Navigation.PushModalAsync(new NavigationPage(settingsPage));
        }
        catch (Exception ex)
        {
            await DisplayAlert("Error", $"No se pudo abrir la configuración: {ex.Message}", "OK");
        }
    }
}
