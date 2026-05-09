using MauiRAG.Servicios;

namespace MauiRAG;

public partial class App : Application
{
	public App()
	{
		InitializeComponent();

		// cargo la configuracion guardada para que la app arranque con los datos del usuario
		ApiService.BaseUrl = Preferences.Get("base_url", "http://localhost:3001/api");
		ApiService.ApiKey = Preferences.Get("api_key", "");
		ApiService.SystemPrompt = Preferences.Get("system_prompt", "");
		ApiService.LmStudioUrl = Preferences.Get("lm_studio_url", "http://localhost:1234");

		// scripts de python: por defecto en la carpeta Scripts junto al ejecutable
		string defaultScripts = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Scripts");
		string scriptsPath = Preferences.Get("scripts_path", "");
		PythonProcessorService.ScriptsPath = string.IsNullOrWhiteSpace(scriptsPath) ? defaultScripts : scriptsPath;
		string pythonExe = Preferences.Get("python_exe_path", "python");
		PythonProcessorService.PythonExePath = string.IsNullOrWhiteSpace(pythonExe) ? "python" : pythonExe;
	}

	protected override Window CreateWindow(IActivationState activationState)
	{
		return new Window(new AppShell());
	}
}
