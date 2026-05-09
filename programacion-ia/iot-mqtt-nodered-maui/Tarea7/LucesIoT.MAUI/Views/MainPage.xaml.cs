using LucesIoT.MAUI.ViewModels;

namespace LucesIoT.MAUI.Views;

public partial class MainPage : ContentPage
{
    public MainPage(MainViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }

    // Cuando vuelves de Settings refrescar el panel SISTEMA
    protected override void OnAppearing()
    {
        base.OnAppearing();
        if (BindingContext is MainViewModel vm)
            vm.RefreshSystemInfo();
    }

    // Navegacion a settings (esto va en code-behind porque es navegacion)
    private async void OnSettingsClicked(object sender, EventArgs e)
    {
        await Shell.Current.GoToAsync("Settings");
    }
}
