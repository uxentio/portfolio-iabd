using System.Collections.ObjectModel;
using System.Globalization;
using CommunityToolkit.Maui.Media;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LucesIoT.MAUI.Models;
using LucesIoT.MAUI.Services;

namespace LucesIoT.MAUI.ViewModels;

// ViewModel gordo, aqui meto todo: chat, LEDs, botones, voz, presets (semaforo/ola),
// morse y el estado de la UI. En el ejemplo de partida todo esto estaba metido en el
// code-behind del WPF; yo lo he partido siguiendo MVVM como pide el enunciado.
//    MVVM con CommunityToolkit: https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/
// Los [ObservableProperty] y [RelayCommand] generan el boilerplate solos con source generators
// (generadores de codigo en tiempo de compilacion), asi no me toca escribirlo a mano.
public partial class MainViewModel : ObservableObject
{
    private readonly LmStudioService _lmStudioService;
    private readonly NodeRedService _nodeRedService;

    public ObservableCollection<ChatMessage> Messages { get; } = new();

    [ObservableProperty]
    private string _userInput = string.Empty;

    [ObservableProperty]
    private bool _isLoading;

    // colores de los circulos de la UI (gris = apagado)
    [ObservableProperty]
    private Color _luzVerdeColor = Colors.Gray;

    [ObservableProperty]
    private Color _luzRojaColor = Colors.Gray;

    [ObservableProperty]
    private Color _luzAzulColor = Colors.Gray;

    [ObservableProperty]
    private string _statusText = "Listo. Escribe un comando.";

    // panel SISTEMA (info de conexion)
    [ObservableProperty]
    private string _infoLlm = "";

    [ObservableProperty]
    private string _infoMqtt = "";

    [ObservableProperty]
    private string _infoTopic = "";

    [ObservableProperty]
    private string _infoNodeRed = "";

    [ObservableProperty]
    private bool _isListening;

    // opacidad del halo: 0.4 = apagado, 1.0 = encendido
    private const double OPACIDAD_OFF = 0.4;
    private const double OPACIDAD_ON = 1.0;
    private const int INTERVALO_BLINK_MS = 400;  // mismo que en el ESP32

    [ObservableProperty]
    private double _luzVerdeOpacity = OPACIDAD_OFF;

    [ObservableProperty]
    private double _luzRojaOpacity = OPACIDAD_OFF;

    [ObservableProperty]
    private double _luzAzulOpacity = OPACIDAD_OFF;

    // para el parpadeo visual en la UI (no es el del ESP32, solo para que se vea bonito)
    private IDispatcherTimer? _blinkTimer;
    private bool _blinkVisible = true;
    private Dictionary<string, string> _currentStates = new()
    {
        ["verde"] = "off", ["roja"] = "off", ["azul"] = "off"
    };

    public MainViewModel(LmStudioService lmStudioService, NodeRedService nodeRedService)
    {
        _lmStudioService = lmStudioService;
        _nodeRedService = nodeRedService;

        RefreshSystemInfo();

        Messages.Add(new ChatMessage
        {
            Text = "Hola! Soy tu asistente IoT. Puedo encender, apagar o poner en " +
                   "intermitente las luces verde, roja y azul. Combinaciones incluidas. " +
                   "Prueba: \"enciende la verde y pon la roja intermitente\"",
            IsUser = false
        });
    }

    // refresco el panel SISTEMA, lo llamo al arrancar y al volver de Settings
    public void RefreshSystemInfo()
    {
        InfoLlm = _lmStudioService.ModelName;
        InfoMqtt = _nodeRedService.MqttBroker;
        InfoTopic = _nodeRedService.MqttTopic;
        InfoNodeRed = _nodeRedService.Url.Replace("http://", "").Replace("/encender", "");
    }

    // boton enviar / enter
    [RelayCommand]
    private async Task SendAsync()
    {
        string input = UserInput?.Trim() ?? string.Empty;
        if (string.IsNullOrEmpty(input) || IsLoading)
            return;

        Messages.Add(new ChatMessage { Text = input, IsUser = true });
        UserInput = string.Empty;
        IsLoading = true;
        StatusText = "Procesando...";

        try
        {
            var result = await _lmStudioService.SendAsync(input);

            if (result.MorseText != null)
            {
                await ProcesarMorse(result.MorseText, result.MorseColor ?? "verde");
            }
            else if (result.Preset != null)
            {
                await ProcesarPreset(result.Preset);
            }
            else if (result.IsToolCall)
            {
                await ProcesarToolCall(result.LedStates!);
            }
            else
            {
                Messages.Add(new ChatMessage
                {
                    Text = result.TextResponse ?? "Sin respuesta.",
                    IsUser = false
                });
                StatusText = "Respuesta recibida (sin accion IoT).";
            }
        }
        catch (HttpRequestException)
        {
            Messages.Add(new ChatMessage
            {
                Text = "Error: no puedo conectar con LM Studio. " +
                       "Mira que este corriendo en localhost:1234.",
                IsUser = false
            });
            StatusText = "Error de conexion con LM Studio.";
        }
        catch (Exception ex)
        {
            Messages.Add(new ChatMessage
            {
                Text = $"Error: {ex.Message}",
                IsUser = false
            });
            StatusText = "Algo ha fallado...";
        }
        finally
        {
            IsLoading = false;
        }
    }

    // me llegan los 3 estados, pinto los circulitos y se lo paso a Node-RED
    private async Task ProcesarToolCall(Dictionary<string, string> ledStates)
    {
        _currentStates = new Dictionary<string, string>(ledStates);
        SetLedsFromStates(ledStates);

        bool ok = await _nodeRedService.SendCommandAsync(ledStates);

        // armo un texto legible para el chat en castellano
        var partes = new List<string>();
        foreach (var kv in ledStates)
        {
            if (kv.Value == "off") continue;
            partes.Add($"{kv.Key} {NombreEstado(kv.Value)}");
        }

        string mensaje = partes.Count > 0
            ? $"Luces: {string.Join(", ", partes)}."
            : "Todas las luces apagadas.";

        Messages.Add(new ChatMessage { Text = mensaje, IsUser = false });

        StatusText = ok
            ? $"Enviado a Node-RED. {mensaje}"
            : $"{mensaje} (Node-RED no respondio)";

        try { HapticFeedback.Default.Perform(HapticFeedbackType.Click); } catch { }
    }

    // activa un preset (semaforo, ola) en el ESP32
    private async Task ProcesarPreset(string nombre)
    {
        // valido lo que me llega del LLM por si se inventa algo raro tipo "semáforo" con tilde
        string nombreNormalizado = nombre switch
        {
            "semaforo" or "semáforo" or "traffic" or "traffic_light" => "semaforo",
            "ola" or "wave" or "wave_effect" => "ola",
            _ => "ninguno"
        };

        bool ok = await _nodeRedService.SendPresetAsync(nombreNormalizado);

        if (nombreNormalizado == "semaforo")
        {
            IniciarPresetVisual("semaforo");
            Messages.Add(new ChatMessage { Text = "Modo SEMAFORO activado.", IsUser = false });
            StatusText = ok ? "Semaforo en marcha." : "Semaforo enviado (sin respuesta de Node-RED).";
        }
        else if (nombreNormalizado == "ola")
        {
            IniciarPresetVisual("ola");
            Messages.Add(new ChatMessage { Text = "Modo OLA activado.", IsUser = false });
            StatusText = ok ? "La ola en marcha." : "Ola enviada (sin respuesta de Node-RED).";
        }
        else
        {
            PararPresetVisual();
            _currentStates = new Dictionary<string, string> { ["verde"] = "off", ["roja"] = "off", ["azul"] = "off" };
            SetLedsFromStates(_currentStates);
            Messages.Add(new ChatMessage { Text = "Preset desactivado.", IsUser = false });
            StatusText = "Preset apagado.";
        }
    }

    // timer del preset en la app (solo cosmetico, el ESP32 corre el suyo)
    private IDispatcherTimer? _presetTimer;
    private int _presetFase = 0;
    private string _presetActivo = "";

    private void IniciarPresetVisual(string nombre)
    {
        PararPresetVisual();
        _presetActivo = nombre;
        _presetFase = 0;
        _presetTimer = Application.Current!.Dispatcher.CreateTimer();
        // semaforo avanza cada 1s, ola cada 500 ms
        _presetTimer.Interval = TimeSpan.FromMilliseconds(nombre == "ola" ? 500 : 1000);
        _presetTimer.Tick += (s, e) =>
        {
            Dictionary<string, string> estados = _presetActivo switch
            {
                "semaforo" => (_presetFase % 7) switch
                {
                    < 3 => new() { ["verde"] = "on",  ["roja"] = "off", ["azul"] = "off" },
                    3   => new() { ["verde"] = "on",  ["roja"] = "on",  ["azul"] = "off" },
                    _   => new() { ["verde"] = "off", ["roja"] = "on",  ["azul"] = "off" }
                },
                "ola" => (_presetFase % 3) switch
                {
                    0 => new() { ["verde"] = "on",  ["roja"] = "off", ["azul"] = "off" },
                    1 => new() { ["verde"] = "off", ["roja"] = "on",  ["azul"] = "off" },
                    _ => new() { ["verde"] = "off", ["roja"] = "off", ["azul"] = "on"  }
                },
                _ => new() { ["verde"] = "off", ["roja"] = "off", ["azul"] = "off" }
            };
            _currentStates = estados;
            SetLedsFromStates(estados);
            _presetFase++;
        };
        _presetTimer.Start();
    }

    private void PararPresetVisual()
    {
        _presetTimer?.Stop();
        _presetTimer = null;
        _presetActivo = "";
    }

    // emite un texto en morse por el LED indicado (solo manda el comando, la emision la hace el ESP32)
    private async Task ProcesarMorse(string texto, string color)
    {
        PararPresetVisual();
        // dejo solo el LED del morse en blink en la UI como pista visual
        var estados = new Dictionary<string, string> { ["verde"] = "off", ["roja"] = "off", ["azul"] = "off" };
        estados[color] = "blink";
        _currentStates = estados;
        SetLedsFromStates(estados);

        bool ok = await _nodeRedService.SendMorseAsync(texto, color);

        Messages.Add(new ChatMessage { Text = $"Emitiendo en morse: {texto.ToUpper()} (LED {color})", IsUser = false });
        StatusText = ok ? $"Morse enviado: {texto}" : "Morse no pudo enviarse a Node-RED.";
    }

    // pasar el estado a algo que se entienda en el chat/OLED
    private static string NombreEstado(string s) => s switch
    {
        "on"    => "encendida",
        "dim"   => "tenue",
        "blink" => "parpadeando",
        "fast"  => "parpadeo rapido",
        "slow"  => "parpadeo lento",
        "fade"  => "respirando",
        _       => "apagada"
    };

    // pinto los LEDs. Si hay algun estado animado arranco un timer al ritmo que toque
    // y dejo que el propio timer vaya alternando ON/OFF o subiendo/bajando la opacidad
    private void SetLedsFromStates(Dictionary<string, string> states)
    {
        _blinkTimer?.Stop();
        _blinkTimer = null;

        ApplyLedVisual("verde", states.GetValueOrDefault("verde", "off"));
        ApplyLedVisual("roja",  states.GetValueOrDefault("roja",  "off"));
        ApplyLedVisual("azul",  states.GetValueOrDefault("azul",  "off"));

        // busco el estado animado mas "rapido" para ponerle ritmo al timer comun
        int intervalo = 0;
        bool hayFade = false;
        foreach (var v in states.Values)
        {
            switch (v)
            {
                case "fast":  if (intervalo == 0 || 150 < intervalo) intervalo = 150; break;
                case "blink": if (intervalo == 0 || 400 < intervalo) intervalo = 400; break;
                case "slow":  if (intervalo == 0 || 1000 < intervalo) intervalo = 1000; break;
                case "fade":  hayFade = true; break;
            }
        }

        if (intervalo == 0 && !hayFade) return;

        // para fade uso un timer rapido (60ms) y calculo una sinusoide de opacidad
        int tick = hayFade ? 60 : intervalo;
        _blinkVisible = true;
        _blinkTimer = Application.Current!.Dispatcher.CreateTimer();
        _blinkTimer.Interval = TimeSpan.FromMilliseconds(tick);

        var inicio = DateTime.UtcNow;
        _blinkTimer.Tick += (s, e) =>
        {
            _blinkVisible = !_blinkVisible;
            double fadeOpacity = 0;
            if (hayFade)
            {
                double t = (DateTime.UtcNow - inicio).TotalMilliseconds;
                // sinusoide 2s periodo, 0.15..1.0 de opacidad
                fadeOpacity = 0.15 + 0.85 * (0.5 + 0.5 * Math.Sin(2 * Math.PI * t / 2000.0));
            }

            foreach (var kv in _currentStates)
            {
                switch (kv.Value)
                {
                    case "blink" when intervalo == 400:
                    case "fast"  when intervalo == 150:
                    case "slow"  when intervalo == 1000:
                        ApplyLedVisual(kv.Key, _blinkVisible ? "on" : "off");
                        break;
                    case "fade":
                        ApplyLedVisual(kv.Key, "on", fadeOpacity);
                        break;
                }
            }
        };
        _blinkTimer.Start();
    }

    // cambia color + opacidad de un LED en la UI (opacidad opcional sobrescribe el default)
    private void ApplyLedVisual(string led, string state, double? overrideOpacity = null)
    {
        bool encendido = state is "on" or "blink" or "fast" or "slow" or "fade";
        bool tenue = state == "dim";

        Color color = (encendido || tenue)
            ? led switch { "verde" => Colors.Green, "roja" => Colors.Red, "azul" => Colors.Blue, _ => Colors.Gray }
            : Colors.Gray;

        double opacity = overrideOpacity ?? (encendido ? OPACIDAD_ON : (tenue ? 0.5 : OPACIDAD_OFF));

        switch (led)
        {
            case "verde": LuzVerdeColor = color; LuzVerdeOpacity = opacity; break;
            case "roja":  LuzRojaColor = color;  LuzRojaOpacity = opacity;  break;
            case "azul":  LuzAzulColor = color;  LuzAzulOpacity = opacity;  break;
        }
    }

    // --- voz ---
    // esto lo saque de aqui: https://learn.microsoft.com/en-us/dotnet/communitytoolkit/maui/
    // al principio no me funcionaba porque no pedia el permiso de micro antes

    [RelayCommand]
    private async Task VoiceInputAsync()
    {
        if (IsListening || IsLoading)
            return;

        try
        {
            var status = await Permissions.RequestAsync<Permissions.Microphone>();
            if (status != PermissionStatus.Granted)
            {
                StatusText = "No se dio permiso de microfono.";
                return;
            }

            IsListening = true;
            StatusText = "Escuchando... (habla y espera)";

            var speechToText = SpeechToText.Default;
            var tcs = new TaskCompletionSource<string?>();

            // muestro lo parcial en el Entry mientras habla
            void onPartial(object? sender, SpeechToTextRecognitionResultUpdatedEventArgs e)
            {
                UserInput = e.RecognitionResult;
            }

            void onFinal(object? sender, SpeechToTextRecognitionResultCompletedEventArgs e)
            {
                tcs.TrySetResult(e.RecognitionResult.Text);
            }

            speechToText.RecognitionResultUpdated += onPartial;
            speechToText.RecognitionResultCompleted += onFinal;

            try
            {
                // fuerzo es-ES, si no a veces me pillaba ingles
                var options = new SpeechToTextOptions
                {
                    Culture = CultureInfo.GetCultureInfo("es-ES"),
                    ShouldReportPartialResults = true
                };
                await speechToText.StartListenAsync(options);

                // 10s timeout por si se queda colgado y no detecta silencio
                var finalText = await Task.WhenAny(tcs.Task, Task.Delay(10000)) == tcs.Task
                    ? tcs.Task.Result
                    : null;

                await speechToText.StopListenAsync();
                IsListening = false;

                if (!string.IsNullOrWhiteSpace(finalText))
                {
                    UserInput = finalText;
                    StatusText = $"Reconocido: \"{finalText}\"";
                    await SendAsync();
                }
                else
                {
                    StatusText = "No se pudo reconocer la voz.";
                }
            }
            finally
            {
                // desengancho los eventos o memory leak
                speechToText.RecognitionResultUpdated -= onPartial;
                speechToText.RecognitionResultCompleted -= onFinal;
            }
        }
        catch (Exception ex)
        {
            IsListening = false;
            StatusText = $"Error de voz: {ex.Message}";
        }
    }

    // --- botones manuales (para probar sin el LLM, me salvaron la vida debuggeando) ---
    // cada boton hace TOGGLE solo de su color y respeta el estado de los otros dos
    // asi puedo tener verde y azul encendidos y apagar solo el azul con un clic

    private async Task ToggleLedAsync(string led)
    {
        // ciclo de 3 estados: off -> on -> blink -> off
        // asi con un solo boton puedo probar las 3 cosas sin tocar las otras luces
        string actual = _currentStates.GetValueOrDefault(led, "off");
        string nuevo = actual switch
        {
            "off"   => "on",
            "on"    => "blink",
            "blink" => "off",
            _       => "off"
        };

        var states = new Dictionary<string, string>(_currentStates);
        states[led] = nuevo;

        _currentStates = states;
        SetLedsFromStates(states);
        await _nodeRedService.SendCommandAsync(states["verde"], states["roja"], states["azul"]);

        string etiqueta = nuevo switch
        {
            "on"    => "encendido",
            "blink" => "intermitente",
            _       => "apagado"
        };
        StatusText = $"LED {led} {etiqueta} (manual).";
    }

    [RelayCommand]
    private Task ToggleVerdeAsync() => ToggleLedAsync("verde");

    [RelayCommand]
    private Task ToggleRojaAsync() => ToggleLedAsync("roja");

    [RelayCommand]
    private Task ToggleAzulAsync() => ToggleLedAsync("azul");

    [RelayCommand]
    private async Task ApagarAsync()
    {
        var states = new Dictionary<string, string> { ["verde"] = "off", ["roja"] = "off", ["azul"] = "off" };
        _currentStates = states;
        SetLedsFromStates(states);
        await _nodeRedService.SendCommandAsync("off", "off", "off");
        StatusText = "Luces apagadas (manual).";
    }

    [RelayCommand]
    private void ClearChat()
    {
        Messages.Clear();
        // ya no hay historial que limpiar en el servicio: no le mandamos contexto al LLM
        var off = new Dictionary<string, string> { ["verde"] = "off", ["roja"] = "off", ["azul"] = "off" };
        _currentStates = off;
        SetLedsFromStates(off);
        StatusText = "Chat limpiado.";
        Messages.Add(new ChatMessage { Text = "Chat reiniciado.", IsUser = false });
    }
}
