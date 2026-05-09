using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UT2_POO_Memoria.Modelos
{
    public class Vehiculo
    {
        public string Matricula { get; set; }
        public string Marca { get; set; } 
        public string Modelo { get; set; } 
        public DateTime FechaMatriculacion { get; set; } 
        public string Propietario { get; set; } 
        public string DniPropietario { get; set; }

        // Composición: la tarjeta ITV forma parte del vehículo
        public TarjetaItv Tarjeta { get; set; } = new TarjetaItv();

        //public int CompareTo(Vehiculo? other)
        //{
        //    if (other is null) return 1;
        //    return string.Compare(Matricula, other.Matricula, StringComparison.OrdinalIgnoreCase);
        //}

        public override string ToString()
            => $"Vehiculo{{marca={Marca}, modelo={Modelo}, matricula={Matricula}, fecha={FechaMatriculacion:dd/MM/yyyy}, " +
               $"propietario={Propietario}, dni_propietario={DniPropietario}, itv={Tarjeta?.Numero}}}";
    }

}
