using FacturasOCR.Servicios;

namespace FacturasOCR.Paginas;

public partial class PaginaHistorial : ContentPage
{
    private ServicioBaseDatos _databaseService;

    public PaginaHistorial()
    {
        InitializeComponent();
        _databaseService = new ServicioBaseDatos();

        // Actualizar textos en tiempo real al cambiar idioma
        ServicioIdiomas.IdiomaChanged += () =>
            MainThread.BeginInvokeOnMainThread(AplicarIdioma);
    }

    private static string L(string key) => ServicioIdiomas.T(key);

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        AplicarIdioma();
        await LoadSavedResults();
    }

    private void AplicarIdioma()
    {
        Title = L("history_title");
        lblHeader.Text = L("history_header");
        lblHint.Text = L("history_hint");
        lblEmptyTitle.Text = L("history_empty");
        lblEmptyHint.Text = L("history_empty_hint");
    }

    private async Task LoadSavedResults()
    {
        var results = await _databaseService.GetAllInvoicesAsync();
        collectionResults.ItemsSource = results;
        lblCount.Text = $"({results.Count})";
        string dbDir = Preferences.Get("DbDirectory", ServicioBaseDatos.DefaultDbDirectory);
        lblDbPath.Text = $"BD: {Path.Combine(dbDir, "invoices.db")}  |  {L("current_files")} {Path.Combine(dbDir, "images")}";
    }

    private async void OnResultSelected(object? sender, SelectionChangedEventArgs e)
    {
        if (e.CurrentSelection.FirstOrDefault() is Modelos.ResultadoFactura result)
        {
            collectionResults.SelectedItem = null;
            await Shell.Current.GoToAsync($"detail?id={result.Id}");
        }
    }

    private async void OnDeleteSwipe(object? sender, EventArgs e)
    {
        if (sender is SwipeItem swipeItem && swipeItem.BindingContext is Modelos.ResultadoFactura invoice)
            await DeleteInvoice(invoice);
    }

    private async void OnDeleteButtonClicked(object? sender, EventArgs e)
    {
        if (sender is Button btn && btn.BindingContext is Modelos.ResultadoFactura invoice)
            await DeleteInvoice(invoice);
    }

    private async Task DeleteInvoice(Modelos.ResultadoFactura invoice)
    {
        bool confirm = await DisplayAlert(
            L("confirm"),
            $"{L("delete_confirm_msg")} '{invoice.FileName}'?",
            L("delete"), L("cancel"));

        if (!confirm) return;

        if (!string.IsNullOrEmpty(invoice.ImagePath) && File.Exists(invoice.ImagePath))
        {
            File.Delete(invoice.ImagePath);
        }

        await _databaseService.DeleteInvoiceAsync(invoice);
        await LoadSavedResults();
    }
}
