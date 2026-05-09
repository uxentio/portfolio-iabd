using ObjCRuntime;
using UIKit;

namespace LucesIoT.MAUI;

public class Program
{
	// Punto de entrada principal de la aplicacion en iOS
	static void Main(string[] args)
	{
		UIApplication.Main(args, null, typeof(AppDelegate));
	}
}
