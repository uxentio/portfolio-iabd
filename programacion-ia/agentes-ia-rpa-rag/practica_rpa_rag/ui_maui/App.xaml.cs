namespace RpaChatApp;

public partial class App : Application
{
	public App()
	{
		InitializeComponent();
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
		// NavigationPage para poder abrir SettingsPage como modal con PushModalAsync.
		return new Window(new NavigationPage(new MainPage())
		{
			BarBackgroundColor = Colors.White,
			BarTextColor = Colors.Black
		});
	}
}
