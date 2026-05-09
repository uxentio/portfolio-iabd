namespace LucesIoT.MAUI;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();
        // Registrar la ruta de settings para poder navegar con GoToAsync
        Routing.RegisterRoute("Settings", typeof(Views.SettingsPage));
    }
}
