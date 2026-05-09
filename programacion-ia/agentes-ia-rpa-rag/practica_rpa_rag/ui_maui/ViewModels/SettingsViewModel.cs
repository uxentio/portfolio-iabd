using System.Collections.ObjectModel;
using System.Windows.Input;
using RpaChatApp.Models;
using RpaChatApp.Services;

namespace RpaChatApp.ViewModels;

// VM de la pantalla de ajustes: edita ApiBaseUrl, ThreadId, backend,
// modelo (Picker rellenado desde GET /models), TTS y delay sintético.
public class SettingsViewModel : BaseViewModel
{
    private readonly AgentApiService _api;
    private AppSettings _settings;

    private string _apiBaseUrl = "";
    private string _threadId = "";
    private string _backend = "langgraph";
    private double _delayMs = 0;
    private string? _selectedModel;
    private bool _ttsEnabled;
    private bool _modelsLoading;
    private string _modelsHint = "Pulsa 'Refrescar modelos' para cargar la lista desde la API.";

    public string ApiBaseUrl
    {
        get => _apiBaseUrl;
        set => SetProperty(ref _apiBaseUrl, value);
    }

    public string ThreadId
    {
        get => _threadId;
        set => SetProperty(ref _threadId, value);
    }

    public string Backend
    {
        get => _backend;
        set => SetProperty(ref _backend, value);
    }

    // double para que ligue con el Slider sin convertidor.
    public double DelayMs
    {
        get => _delayMs;
        set => SetProperty(ref _delayMs, value);
    }

    // Lista de modelos rellenada dinámicamente desde GET /models de la API.
    public ObservableCollection<string> AvailableModels { get; } = new();

    public string? SelectedModel
    {
        get => _selectedModel;
        set => SetProperty(ref _selectedModel, value);
    }

    public bool TtsEnabled
    {
        get => _ttsEnabled;
        set => SetProperty(ref _ttsEnabled, value);
    }

    public bool ModelsLoading
    {
        get => _modelsLoading;
        set => SetProperty(ref _modelsLoading, value);
    }

    public string ModelsHint
    {
        get => _modelsHint;
        set => SetProperty(ref _modelsHint, value);
    }

    public ICommand SaveCommand { get; }
    public ICommand NewThreadCommand { get; }
    public ICommand DefaultsCommand { get; }
    public ICommand RefreshModelsCommand { get; }

    // Eventos VM -> View. El VM no llama directamente a Navigation.
    public event Action<AppSettings>? SettingsSaved;
    public event Action? CloseRequested;

    public SettingsViewModel(AppSettings settings, AgentApiService api)
    {
        _settings = settings;
        _api = api;
        ApiBaseUrl = settings.ApiBaseUrl;
        ThreadId = settings.ThreadId;
        Backend = string.IsNullOrWhiteSpace(settings.Backend) ? "langgraph" : settings.Backend;
        DelayMs = settings.DelayMs;
        TtsEnabled = settings.TtsEnabled;

        // Si ya teníamos un modelo guardado, lo añado a la lista para que
        // el Picker pueda preseleccionarlo aunque la carga remota falle.
        if (!string.IsNullOrWhiteSpace(settings.ModelName))
        {
            AvailableModels.Add(settings.ModelName);
            SelectedModel = settings.ModelName;
        }

        SaveCommand = new RelayCommand(OnSave);
        NewThreadCommand = new RelayCommand(OnNewThread);
        DefaultsCommand = new RelayCommand(OnDefaults);
        RefreshModelsCommand = new RelayCommand(async () => await LoadModelsAsync());

        // Carga inicial. No await en el ctor; lo dispara en background y
        // la UI se actualiza cuando llega la respuesta.
        _ = LoadModelsAsync();
    }

    public async Task LoadModelsAsync()
    {
        if (_modelsLoading) return;
        ModelsLoading = true;
        ModelsHint = "Consultando GET /models...";
        try
        {
            var (models, current) = await _api.GetAvailableModelsAsync();
            // Mantengo lo que ya hubiera para no perder el modelo seleccionado.
            var existentes = new HashSet<string>(AvailableModels);
            foreach (var m in models)
            {
                if (!existentes.Contains(m))
                {
                    AvailableModels.Add(m);
                }
            }

            if (models.Count == 0)
            {
                ModelsHint = "La API no devolvió modelos. ¿Está LM Studio arrancado en :1234?";
            }
            else
            {
                ModelsHint = $"{models.Count} modelos disponibles. Activo en API: {current ?? "(default)"}";
                // Si nada estaba seleccionado, preselecciona el activo del servidor.
                if (string.IsNullOrEmpty(SelectedModel))
                {
                    SelectedModel = current ?? models[0];
                }
            }
        }
        catch (Exception ex)
        {
            ModelsHint = $"Error al cargar /models: {ex.Message}";
        }
        finally
        {
            ModelsLoading = false;
        }
    }

    private void OnNewThread()
    {
        // Id corto tipo "thread-4af2": legible y suficiente para distinguir a ojo.
        ThreadId = $"thread-{Guid.NewGuid().ToString("N").Substring(0, 4)}";
    }

    private void OnDefaults()
    {
        ApiBaseUrl = "http://localhost:8001";
        ThreadId = "default";
        Backend = "langgraph";
        DelayMs = 0;
        TtsEnabled = false;
        // El modelo no se resetea para no quitarle al usuario el que ya tenía
        // bien configurado; si quiere otro, lo elige del Picker.
    }

    private void OnSave()
    {
        _settings.ApiBaseUrl = string.IsNullOrWhiteSpace(ApiBaseUrl) ? "http://localhost:8001" : ApiBaseUrl.Trim();
        _settings.ThreadId = string.IsNullOrWhiteSpace(ThreadId) ? "default" : ThreadId.Trim();
        _settings.Backend = string.IsNullOrWhiteSpace(Backend) ? "langgraph" : Backend.Trim();
        _settings.DelayMs = (int)Math.Round(DelayMs);
        _settings.ModelName = string.IsNullOrWhiteSpace(SelectedModel) ? "" : SelectedModel.Trim();
        _settings.TtsEnabled = TtsEnabled;

        SettingsSaved?.Invoke(_settings);
        CloseRequested?.Invoke();
    }
}
