using System.Globalization;

namespace LucesIoT.MAUI.Converters;

// Converters para el chat - alinean y colorean los mensajes segun quien los escribio

// Alinea: usuario a la derecha, bot a la izquierda
public class BoolToAlignmentConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value is bool isUser && isUser ? LayoutOptions.End : LayoutOptions.Start;
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

// Color de fondo del mensaje
public class BoolToColorConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value is bool isUser && isUser
            ? Color.FromArgb("#1F6FEB")  // azul para el usuario
            : Color.FromArgb("#21262D"); // gris para el bot
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

// Color del texto
public class BoolToTextColorConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value is bool isUser && isUser
            ? Color.FromArgb("#FFFFFF")
            : Color.FromArgb("#C9D1D9");
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
}

// Color del boton de microfono: rojo cuando esta escuchando, gris cuando no
public class BoolToMicColorConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value is bool listening && listening
            ? Color.FromArgb("#EF4444")  // rojo = grabando
            : Color.FromArgb("#64748B"); // gris = inactivo
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotImplementedException();
}
