using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UT2_POO_Memoria.Utilidades
{
    public static class Utils
    {
        // Por si necesitas parsear fechas estilo inglés del Java original.
        public static DateTime? ParseFechaIngles(string fecha)
        {
            string fmt = "ddd MMM dd HH:mm:ss 'GMT'zzz yyyy";
            if (DateTimeOffset.TryParseExact(fecha, fmt, CultureInfo.InvariantCulture,
                                             DateTimeStyles.None, out var dto))
            {
                return dto.DateTime;
            }
            return null;
        }

        public static DateTime? ParseFechaEs(string fecha)
        {
            if (DateTime.TryParseExact(fecha, "dd/MM/yyyy", new CultureInfo("es-ES"),
                                       DateTimeStyles.None, out var dt))
            {
                return dt;
            }
            return null;
        }
    }
}
