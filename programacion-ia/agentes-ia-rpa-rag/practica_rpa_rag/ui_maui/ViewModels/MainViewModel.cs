using System.Collections.ObjectModel;
using System.Windows.Input;
using RpaChatApp.Models;
using RpaChatApp.Services;

namespace RpaChatApp.ViewModels;

// VM del chat: mantiene los mensajes y pinta los eventos SSE del agente.
public class MainViewModel : BaseViewModel
{
    private readonly AgentApiService _api;
    private AppSettings _settings;

    private string _messageText = "";
    private string _statusText = "";
    private string _chatTitle = "Agente RPA";

    // ObservableCollection: cada Add notifica al CollectionView sin recrear las burbujas.
    public ObservableCollection<ChatMessage> Messages { get; } = new();

    public string ChatTitle
    {
        get => _chatTitle;
        set => SetProperty(ref _chatTitle, value);
    }

    public string MessageText
    {
        get => _messageText;
        set => SetProperty(ref _messageText, value);
    }

    public string StatusText
    {
        get => _statusText;
        set
        {
            if (SetProperty(ref _statusText, value))
                OnPropertyChanged(nameof(IsBusy));
        }
    }

    public bool IsBusy => !string.IsNullOrEmpty(_statusText);

    public AppSettings Settings => _settings;

    // Expongo el servicio para que la SettingsPage lo reuse al consultar
    // /models. Evita crear un AgentApiService duplicado cada vez que se
    // abre la pantalla de configuración.
    public AgentApiService Api => _api;

    public ICommand SendCommand { get; }
    public ICommand ResetCommand { get; }

    // Evento para pedir scroll a la View, sin acoplar VM al CollectionView.
    public event Action? ScrollRequested;

    public MainViewModel()
    {
        // El VM monta sus dependencias con `new` porque no hay DI.
        _settings = new AppSettings();
        _api = new AgentApiService(_settings);

        SendCommand = new RelayCommand(OnSend);
        ResetCommand = new RelayCommand(OnReset);

        AddMessage(ChatRole.Agent, "agente",
            $"Hola. Estoy conectado a {_settings.ApiBaseUrl}. Cuéntame qué quieres hacer " +
            "(p. ej. \"añade al catálogo Cien años de soledad a 18,50 con 5 ejemplares\" " +
            "o \"encarga un libro en formato tapa dura a la tienda externa\").");
    }

    private async void OnSend()
    {
        var text = MessageText?.Trim() ?? "";
        // IsBusy hace de guard contra reentrada.
        if (string.IsNullOrEmpty(text) || IsBusy) return;

        MessageText = "";
        AddMessage(ChatRole.User, "tú", text);

        StatusText = "pensando...";

        try
        {
            await _api.SendMessageAsync(text, HandleAgentEvent);
        }
        catch (Exception ex)
        {
            AddMessage(ChatRole.Error, "error", ex.Message);
        }
        finally
        {
            StatusText = "";
        }
    }

    // Callback del SSE. Llega en el hilo del HttpClient, así que marshallo
    // al hilo de UI para tocar la ObservableCollection sin cross-thread.
    private void HandleAgentEvent(AgentApiService.AgentEvent evt)
    {
        MainThread.BeginInvokeOnMainThread(() =>
        {
            switch (evt.Type)
            {
                case AgentEventType.Meta:
                    var backendUsado = evt.RawArgs?["backend"]?.ToString();
                    if (!string.IsNullOrEmpty(backendUsado))
                    {
                        ChatTitle = $"Agente RPA · {_settings.ThreadId} · {backendUsado}";
                    }
                    break;

                case AgentEventType.ToolCall:
                    AddMessage(ChatRole.ToolCall, $"tool · {evt.ToolName}", evt.Content);
                    StatusText = $"ejecutando {evt.ToolName}...";
                    break;

                case AgentEventType.ToolResult:
                    AddMessage(ChatRole.ToolResult, $"result · {evt.ToolName}", Truncate(evt.Content, 300));
                    break;

                case AgentEventType.Answer:
                    AddMessage(ChatRole.Agent, "agente", evt.Content);
                    // TTS sin await: dispara la lectura en background para no
                    // bloquear el repaint del chat mientras MAUI Essentials
                    // arranca el motor de voz.
                    if (_settings.TtsEnabled && !string.IsNullOrWhiteSpace(evt.Content))
                    {
                        _ = SpeakAsync(evt.Content);
                    }
                    break;

                case AgentEventType.Error:
                    AddMessage(ChatRole.Error, "error", evt.Content);
                    break;

                case AgentEventType.Done:
                    StatusText = "";
                    break;
            }
        });
    }

    private void AddMessage(ChatRole role, string sender, string content)
    {
        Messages.Add(new ChatMessage
        {
            Role = role,
            Sender = sender,
            Content = content,
            Timestamp = DateTime.Now,
        });
        ScrollRequested?.Invoke();
    }

    private void OnReset()
    {
        Messages.Clear();
        AddMessage(ChatRole.Agent, "agente",
            $"Conversación reiniciada. thread_id actual: {_settings.ThreadId}.");
    }

    private async Task SpeakAsync(string texto)
    {
        try
        {
            // Recorte porque TextToSpeech corta textos largos en algunas
            // plataformas; la primera frase basta para acompañar el chat.
            await TextToSpeech.Default.SpeakAsync(Truncate(texto, 600));
        }
        catch
        {
            // TTS opcional: si falta voz instalada, no rompo el chat.
        }
    }

    private static string Truncate(string s, int max) =>
        string.IsNullOrEmpty(s) || s.Length <= max ? s : s.Substring(0, max) + "...";

    public Task ApplySettings(AppSettings newSettings)
    {
        _settings = newSettings;
        _api.UpdateSettings(_settings);
        var backend = string.IsNullOrWhiteSpace(_settings.Backend) ? "default" : _settings.Backend;
        ChatTitle = $"Agente RPA · {_settings.ThreadId} · {backend}";
        return Task.CompletedTask;
    }
}
