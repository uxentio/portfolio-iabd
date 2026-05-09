using FacturasOCR.Paginas;
using FacturasOCR.Servicios;

namespace FacturasOCR;

public partial class AppShell : Shell
{
	public AppShell()
	{
		InitializeComponent();
		Routing.RegisterRoute("detail", typeof(PaginaDetalle));
		AplicarIdioma();

		// Suscribirse al cambio de idioma para actualizar tabs en tiempo real
		ServicioIdiomas.IdiomaChanged += () =>
			MainThread.BeginInvokeOnMainThread(AplicarIdioma);
	}

	protected override void OnNavigated(ShellNavigatedEventArgs args)
	{
		base.OnNavigated(args);
		AplicarIdioma();
	}

	private void AplicarIdioma()
	{
		tabAnalyze.Title = ServicioIdiomas.T("tab_analyze");
		tabArchive.Title = ServicioIdiomas.T("tab_archive");
		tabSettings.Title = ServicioIdiomas.T("tab_settings");
	}
}
