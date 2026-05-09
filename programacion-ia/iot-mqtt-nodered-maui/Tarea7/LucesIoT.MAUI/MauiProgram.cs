using Microsoft.Extensions.Logging;
using CommunityToolkit.Maui;
using LucesIoT.MAUI.Services;
using LucesIoT.MAUI.ViewModels;
using LucesIoT.MAUI.Views;

namespace LucesIoT.MAUI;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // subo el timeout, LM Studio en mi portatil tarda un huevo en la primera respuesta
        builder.Services.AddSingleton(new HttpClient { Timeout = TimeSpan.FromMinutes(5) });

        // los servicios en singleton, si no al ir a Settings y volver perdia la config
        builder.Services.AddSingleton<LmStudioService>();
        builder.Services.AddSingleton<NodeRedService>();

        // VMs y paginas en transient
        builder.Services.AddTransient<MainViewModel>();
        builder.Services.AddTransient<SettingsViewModel>();
        builder.Services.AddTransient<Views.MainPage>();
        builder.Services.AddTransient<SettingsPage>();

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}
