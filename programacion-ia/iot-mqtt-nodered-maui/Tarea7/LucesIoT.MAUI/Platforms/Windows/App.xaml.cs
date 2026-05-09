using Microsoft.UI.Xaml;

// Punto de entrada de la app en Windows (WinUI)

namespace LucesIoT.MAUI.WinUI;

/// <summary>
/// Clase principal de la aplicacion en Windows.
/// </summary>
public partial class App : MauiWinUIApplication
{
	/// <summary>
	/// Constructor - se ejecuta al iniciar la app.
	/// </summary>
	public App()
	{
		this.InitializeComponent();
	}

	protected override MauiApp CreateMauiApp() => MauiProgram.CreateMauiApp();
}

