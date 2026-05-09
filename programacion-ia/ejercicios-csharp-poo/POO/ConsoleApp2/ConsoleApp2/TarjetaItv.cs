using System;

namespace UT2_POO_Memoria
{
    public class TarjetaItv
    {
        public string Numero { get; set; } = string.Empty;
        public DateTime FechaExpedicion { get; set; }
        public DateTime FechaCaducidad { get; set; }
        public string CentroInspeccion { get; set; } = string.Empty;

        public override string ToString() =>
            $"ITV{{numero={Numero}, expedicion={FechaExpedicion}, caducidad={FechaCaducidad}, centro={CentroInspeccion}}}";
    }
}