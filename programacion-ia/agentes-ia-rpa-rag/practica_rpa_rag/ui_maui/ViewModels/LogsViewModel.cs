using System.Collections.ObjectModel;
using System.Windows.Input;
using RpaChatApp.Services;

namespace RpaChatApp.ViewModels;

// VM de la pantalla de logs y observabilidad: muestra las últimas líneas
// del log del runner RPA, las capturas de pantalla generadas en errores,
// los traces de Playwright y los vídeos. Polling opcional para refresco
// en directo durante la demo.
public class LogsViewModel : BaseViewModel
{
    private readonly AgentApiService _api;
    // Guard contra re-entrada: si el usuario pulsa Refrescar dos veces o
    // un polling dispara antes de terminar el anterior, descartamos el
    // segundo en lugar de solapar peticiones.
    private bool _refreshing;

    public ObservableCollection<string> LogLines { get; } = new();
    public ObservableCollection<ScreenshotItem> Screenshots { get; } = new();
    public ObservableCollection<string> Traces { get; } = new();
    public ObservableCollection<string> Videos { get; } = new();

    private string _statusText = "";
    public string StatusText
    {
        get => _statusText;
        set => SetProperty(ref _statusText, value);
    }

    private string _logPath = "";
    public string LogPath
    {
        get => _logPath;
        set => SetProperty(ref _logPath, value);
    }

    public ICommand RefreshCommand { get; }

    public LogsViewModel(AgentApiService api)
    {
        _api = api;
        RefreshCommand = new RelayCommand(async () => await RefreshAsync());
    }

    public async Task RefreshAsync()
    {
        if (_refreshing) return;
        _refreshing = true;
        StatusText = "Actualizando...";
        try
        {
            // Cuatro llamadas en paralelo. Task.WhenAll permite paralelizar
            // los GET independientes contra logs, screenshots, traces y videos.
            var logsTask = _api.GetLogsAsync(300);
            var shotsTask = _api.GetFileListAsync("screenshots");
            var tracesTask = _api.GetFileListAsync("traces");
            var videosTask = _api.GetFileListAsync("videos");
            await Task.WhenAll(logsTask, shotsTask, tracesTask, videosTask);

            var snap = await logsTask;
            LogLines.Clear();
            if (snap != null)
            {
                LogPath = snap.Path;
                foreach (var l in snap.Lines) LogLines.Add(l);
            }
            else
            {
                LogPath = "(sin conexión con la API)";
            }

            Screenshots.Clear();
            foreach (var f in await shotsTask)
            {
                Screenshots.Add(new ScreenshotItem(f.Name, _api.ScreenshotUrl(f.Name), f.SizeBytes));
            }

            FillCollection(Traces, await tracesTask);
            FillCollection(Videos, await videosTask);

            StatusText = $"OK: {LogLines.Count} líneas · {Screenshots.Count} capturas · {Traces.Count} traces · {Videos.Count} vídeos";
        }
        catch (Exception ex)
        {
            StatusText = $"Error: {ex.Message}";
        }
        finally
        {
            _refreshing = false;
        }
    }

    // Vuelca la lista en la collection con formato "nombre (NN KB)".
    // Centralizado porque traces y vídeos tienen presentación idéntica
    // y duplicar el bucle invitaba a divergencias.
    private static void FillCollection(ObservableCollection<string> col, IReadOnlyList<AgentApiService.FileItem> items)
    {
        col.Clear();
        foreach (var f in items)
        {
            col.Add($"{f.Name}  ({f.SizeBytes / 1024} KB)");
        }
    }
}

// Item de captura para que el CollectionView pueda mostrar la imagen
// remota directamente (Image.Source soporta UriImageSource).
public record ScreenshotItem(string Name, string Url, long SizeBytes);
