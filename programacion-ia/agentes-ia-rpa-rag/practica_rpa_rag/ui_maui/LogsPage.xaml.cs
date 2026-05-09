using RpaChatApp.ViewModels;

namespace RpaChatApp;

public partial class LogsPage : ContentPage
{
    private readonly LogsViewModel _viewModel;

    public LogsPage(LogsViewModel viewModel)
    {
        InitializeComponent();
        _viewModel = viewModel;
        BindingContext = _viewModel;
    }

    protected override async void OnAppearing()
    {
        // Carga inicial al abrir la pantalla. Si la API no está, el VM se
        // queda con StatusText="Error: ..." pero la pantalla no rompe.
        base.OnAppearing();
        await _viewModel.RefreshAsync();
    }
}
