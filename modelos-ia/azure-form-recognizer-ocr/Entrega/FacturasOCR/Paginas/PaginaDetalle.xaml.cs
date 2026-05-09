using FacturasOCR.Modelos;
using FacturasOCR.Servicios;

namespace FacturasOCR.Paginas;

[QueryProperty(nameof(InvoiceId), "id")]
public partial class PaginaDetalle : ContentPage
{
    private ServicioBaseDatos _databaseService;
    private ResultadoFactura? _invoice;

    public int InvoiceId { get; set; }

    public PaginaDetalle()
    {
        InitializeComponent();
        _databaseService = new ServicioBaseDatos();

        // si cambian el idioma se actualiza esta pagina tambien
        ServicioIdiomas.IdiomaChanged += () =>
            MainThread.BeginInvokeOnMainThread(AplicarIdioma);
    }

    private static string L(string key) => ServicioIdiomas.T(key);

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        AplicarIdioma();
        await LoadInvoice();
    }

    private void AplicarIdioma()
    {
        Title = L("detail_title");
        lblProviderLabel.Text = L("provider_label");
        lblInvoiceNumLabel.Text = L("invoice_num_label");
        lblDateLabel.Text = L("date_label");
        lblTotalLabel.Text = L("total_label");
        btnBack.Text = L("btn_back");
        btnShare.Text = L("btn_share");
        btnDelete.Text = L("delete");
    }

    private async Task LoadInvoice()
    {
        _invoice = await _databaseService.GetInvoiceAsync(InvoiceId);
        if (_invoice == null)
        {
            await DisplayAlert(L("error"), L("invoice_not_found"), L("ok"));
            await Shell.Current.GoToAsync("..");
            return;
        }

        // Datos resumen
        lblFileName.Text = _invoice.FileName;
        lblDate.Text = _invoice.AnalyzedAt.ToString("dd/MM/yyyy HH:mm:ss");

        // Campos clave
        lblVendor.Text = string.IsNullOrEmpty(_invoice.VendorName) ? "-" : _invoice.VendorName;
        lblInvoiceId.Text = string.IsNullOrEmpty(_invoice.InvoiceId) ? "-" : _invoice.InvoiceId;
        lblInvoiceDate.Text = string.IsNullOrEmpty(_invoice.InvoiceDate) ? "-" : _invoice.InvoiceDate;
        lblTotal.Text = string.IsNullOrEmpty(_invoice.Total) ? "-" : _invoice.Total;

        // Imagen original
        if (!string.IsNullOrEmpty(_invoice.ImagePath) && File.Exists(_invoice.ImagePath))
        {
            imgInvoice.Source = ImageSource.FromFile(_invoice.ImagePath);
        }

        // Texto completo
        editorFullText.Text = _invoice.RawText;
    }

    private async void OnBackClicked(object? sender, EventArgs e)
    {
        await Shell.Current.GoToAsync("..");
    }

    private async void OnShareClicked(object? sender, EventArgs e)
    {
        if (_invoice == null) return;

        await Share.RequestAsync(new ShareTextRequest
        {
            Title = $"{L("detail_title")} - {_invoice.FileName}",
            Text = _invoice.RawText
        });
    }

    private async void OnDeleteClicked(object? sender, EventArgs e)
    {
        if (_invoice == null) return;

        bool confirm = await DisplayAlert(
            L("confirm"),
            $"{L("delete_confirm_msg")} '{_invoice.FileName}'?",
            L("delete"), L("cancel"));

        if (!confirm) return;

        // Eliminar imagen guardada
        if (!string.IsNullOrEmpty(_invoice.ImagePath) && File.Exists(_invoice.ImagePath))
        {
            File.Delete(_invoice.ImagePath);
        }

        await _databaseService.DeleteInvoiceAsync(_invoice);
        await Shell.Current.GoToAsync("..");
    }
}
