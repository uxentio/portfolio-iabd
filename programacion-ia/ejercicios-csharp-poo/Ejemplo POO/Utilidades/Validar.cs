using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace UT2_POO_Memoria.Utilidades
{
    public static class Validar
    {
        public static bool ComparaFecha(DateTime fechaMat)
        {
            return fechaMat.Date <= DateTime.Today;
        }


        public static bool ValidaMatricula(string matricula)
        {
            //return Regex.IsMatch(matricula ?? string.Empty, @"^\d{4}[A-Z]{3}$", RegexOptions.IgnoreCase);
            return true;
        }
        public static bool ValidaNombre(string nombreCompleto)
        {
            if (string.IsNullOrWhiteSpace(nombreCompleto)) 
                return false;

            // var partes = Regex.Split(nombreCompleto.Trim(), @"\s+");
            //return partes.Length >= 3;

            return true;
        }
    }
}
