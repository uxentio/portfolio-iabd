using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UT2_POO_Memoria.Modelos
{
    public class TarjetaItv
    {
        public string Numero { get; set; }
        public DateTime FechaExpedicion { get; set; }
        public DateTime FechaCaducidad { get; set; }
        public string CentroInspeccion { get; set; }

        public override string ToString()
        {
            return $"ITV{{numero={Numero}, expedicion={FechaExpedicion:dd/MM/yyyy}, " +
                   $"caducidad={FechaCaducidad:dd/MM/yyyy}, centro={CentroInspeccion}}}";
        }
    }
}
