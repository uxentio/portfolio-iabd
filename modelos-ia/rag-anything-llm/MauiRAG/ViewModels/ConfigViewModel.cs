using System.Windows.Input;
using MauiRAG.Servicios;

namespace MauiRAG.ViewModels
{
    public class ConfigViewModel : BaseViewModel
    {
        private string _baseUrl;
        public string BaseUrl
        {
            get => _baseUrl;
            set => SetProperty(ref _baseUrl, value);
        }

        private string _apiKey;
        public string ApiKey
        {
            get => _apiKey;
            set => SetProperty(ref _apiKey, value);
        }

        private string _systemPrompt;
        public string SystemPrompt
        {
            get => _systemPrompt;
            set => SetProperty(ref _systemPrompt, value);
        }

        private string _lmStudioUrl;
        public string LmStudioUrl
        {
            get => _lmStudioUrl;
            set => SetProperty(ref _lmStudioUrl, value);
        }

        private string _scriptsPath;
        public string ScriptsPath
        {
            get => _scriptsPath;
            set => SetProperty(ref _scriptsPath, value);
        }

        private string _pythonExePath;
        public string PythonExePath
        {
            get => _pythonExePath;
            set => SetProperty(ref _pythonExePath, value);
        }

        private string _estado;
        public string Estado
        {
            get => _estado;
            set => SetProperty(ref _estado, value);
        }

        private Color _colorEstado = Colors.Green;
        public Color ColorEstado
        {
            get => _colorEstado;
            set => SetProperty(ref _colorEstado, value);
        }

        private bool _probando;
        public bool Probando
        {
            get => _probando;
            set => SetProperty(ref _probando, value);
        }

        public ICommand GuardarCommand { get; }
        public ICommand ProbarConexionCommand { get; }

        public ConfigViewModel()
        {
            GuardarCommand = new Command(Guardar);
            ProbarConexionCommand = new Command(async () => await ProbarConexion());
        }

        public void CargarPreferencias()
        {
            BaseUrl = Preferences.Get("base_url", "http://localhost:3001/api");
            ApiKey = Preferences.Get("api_key", "");
            SystemPrompt = Preferences.Get("system_prompt", "");
            LmStudioUrl = Preferences.Get("lm_studio_url", "http://localhost:1234");
            ScriptsPath = Preferences.Get("scripts_path", "");
            PythonExePath = Preferences.Get("python_exe_path", "python");
        }

        // guarda config y actualiza el servicio
        public void Guardar()
        {
            Preferences.Set("base_url", BaseUrl);
            Preferences.Set("api_key", ApiKey);
            Preferences.Set("system_prompt", SystemPrompt);
            Preferences.Set("lm_studio_url", LmStudioUrl);
            Preferences.Set("scripts_path", ScriptsPath ?? "");
            Preferences.Set("python_exe_path", PythonExePath ?? "python");

            ApiService.BaseUrl = BaseUrl;
            ApiService.ApiKey = ApiKey;
            ApiService.SystemPrompt = SystemPrompt;
            ApiService.LmStudioUrl = LmStudioUrl;
            PythonProcessorService.ScriptsPath = ScriptsPath ?? "";
            PythonProcessorService.PythonExePath = string.IsNullOrWhiteSpace(PythonExePath) ? "python" : PythonExePath;

            Estado = "Configuracion guardada correctamente!";
            ColorEstado = Colors.Green;
        }

        // test de conexion con anythingllm
        public async Task ProbarConexion()
        {
            Probando = true;
            Estado = "Probando conexion...";
            ColorEstado = Colors.Orange;

            try
            {
                string resultado = await ApiService.ObtenerWorkspaces();
                if (resultado != null)
                {
                    Estado = "Conexion exitosa! AnythingLLM responde correctamente.";
                    ColorEstado = Colors.Green;
                }
                else
                {
                    Estado = "Error: AnythingLLM no respondio. Revisa la URL y la API Key.";
                    ColorEstado = Colors.Red;
                }
            }
            catch (Exception ex)
            {
                Estado = "Error de conexion: " + ex.Message;
                ColorEstado = Colors.Red;
            }
            finally
            {
                Probando = false;
            }
        }
    }
}
