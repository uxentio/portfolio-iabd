using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LucesIoT.MAUI.Services;

namespace LucesIoT.MAUI.ViewModels;

// Pagina de ajustes. Asi puedo cambiar URLs / modelo / broker sin tener que recompilar cada vez
public partial class SettingsViewModel : ObservableObject
{
    [ObservableProperty]
    private string _lmStudioUrl = "http://127.0.0.1:1234";

    [ObservableProperty]
    private string _nodeRedUrl = "http://127.0.0.1:1880/encender";

    [ObservableProperty]
    private string _modelName = "qwen3.5-0.8b";

    [ObservableProperty]
    private string _mqttBroker = "test.mosquitto.org:1883";

    [ObservableProperty]
    private string _mqttTopic = "iabd2425/esp32/led";

    [ObservableProperty]
    private string _testResult = "";

    [ObservableProperty]
    private bool _isTesting;

    [ObservableProperty]
    private bool _cargandoModelos;

    // se rellena al pulsar "Cargar modelos"
    public ObservableCollection<string> AvailableModels { get; } = new();

    // brokers publicos de prueba
    public ObservableCollection<string> AvailableBrokers { get; } = new()
    {
        "test.mosquitto.org:1883",
        "broker.hivemq.com:1883",
    };

    private readonly HttpClient _httpClient;
    private readonly LmStudioService _lmStudioService;
    private readonly NodeRedService _nodeRedService;

    public SettingsViewModel(HttpClient httpClient, LmStudioService lmStudioService, NodeRedService nodeRedService)
    {
        _httpClient = httpClient;
        _lmStudioService = lmStudioService;
        _nodeRedService = nodeRedService;

        // pillo lo que hay cargado en los servicios
        LmStudioUrl = lmStudioService.UrlBase;
        NodeRedUrl = nodeRedService.Url;
        ModelName = lmStudioService.ModelName;
        MqttBroker = nodeRedService.MqttBroker;
        MqttTopic = nodeRedService.MqttTopic;
    }

    // pregunta a LM Studio por sus modelos cargados
    [RelayCommand]
    private async Task CargarModelosAsync()
    {
        CargandoModelos = true;
        TestResult = "Consultando modelos en LM Studio...";

        var modelos = await _lmStudioService.ObtenerModelosDisponiblesAsync();

        AvailableModels.Clear();
        if (modelos.Count > 0)
        {
            foreach (var m in modelos)
                AvailableModels.Add(m);

            if (!modelos.Contains(ModelName))
                ModelName = modelos[0];

            TestResult = $"Encontrados {modelos.Count} modelo(s).";
        }
        else
        {
            // si no conecta, al menos que el Picker no salga vacio
            AvailableModels.Add("qwen2.5-7b-instruct");
            AvailableModels.Add("llama-3.2-3b-instruct");
            TestResult = "No se pudo conectar a LM Studio.";
        }
        CargandoModelos = false;
    }

    [RelayCommand]
    private async Task TestLmStudioAsync()
    {
        IsTesting = true;
        TestResult = "Probando LM Studio...";
        try
        {
            var response = await _httpClient.GetAsync($"{LmStudioUrl}/v1/models");
            TestResult = response.IsSuccessStatusCode
                ? "LM Studio: Conectado OK"
                : $"LM Studio: Error {response.StatusCode}";
        }
        catch (Exception ex)
        {
            TestResult = $"LM Studio: No responde - {ex.Message}";
        }
        IsTesting = false;
    }

    [RelayCommand]
    private async Task TestNodeRedAsync()
    {
        IsTesting = true;
        TestResult = "Probando Node-RED...";
        try
        {
            string baseUrl = NodeRedUrl.Replace("/encender", "");
            var response = await _httpClient.GetAsync(baseUrl);
            TestResult = response.IsSuccessStatusCode
                ? "Node-RED: Conectado OK"
                : $"Node-RED: Error {response.StatusCode}";
        }
        catch (Exception ex)
        {
            TestResult = $"Node-RED: No responde - {ex.Message}";
        }
        IsTesting = false;
    }

    // al volver atras vuelco los cambios en los servicios (son singleton asi que quedan vivos)
    [RelayCommand]
    private async Task GoBackAsync()
    {
        _lmStudioService.UrlBase = LmStudioUrl;
        _lmStudioService.ModelName = ModelName;
        _nodeRedService.Url = NodeRedUrl;
        _nodeRedService.MqttBroker = MqttBroker;
        _nodeRedService.MqttTopic = MqttTopic;

        await Shell.Current.GoToAsync("..");
    }
}
