using FacturasOCR.Paginas;

namespace FacturasOCR;

public partial class App : Application
{
	public App()
	{
		InitializeComponent();

		// Aplicar tema guardado al arrancar
		PaginaAjustes.AplicarTema();
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
		return new Window(new AppShell());
	}
}