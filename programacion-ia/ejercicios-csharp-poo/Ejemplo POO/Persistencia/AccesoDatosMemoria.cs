using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UT2_POO_Memoria.Modelos;

namespace UT2_POO_Memoria.Persistencia
{
    public class AccesoDatosMemoria
    {
        // Almacén en memoria
        private readonly List<Vehiculo> _datos = new List<Vehiculo>();

        public AccesoDatosMemoria()
        {
            Seed();
        }

        public List<Vehiculo> GetAll()
        {
            // Devolver copia (defensiva)
            var copia = new List<Vehiculo>(_datos.Count);
            for (int i = 0; i < _datos.Count; i++)
            {
                copia.Add(Clone(_datos[i]));
            }
            return copia;
        }

        public void Add(Vehiculo vehiculo)
        {
            if (vehiculo == null) throw new ArgumentNullException(nameof(vehiculo));
            if (string.IsNullOrWhiteSpace(vehiculo.Matricula))
                throw new ArgumentException("La matrícula es obligatoria.");

            // Comprobar duplicado por matrícula
            for (int i = 0; i < _datos.Count; i++)
            {
                if (string.Equals(_datos[i].Matricula, vehiculo.Matricula, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Ya existe un vehículo con esa matrícula.");
            }

            _datos.Add(Clone(vehiculo));
        }

        public void Update(Vehiculo vehiculo)
        {
            if (vehiculo == null) throw new ArgumentNullException(nameof(vehiculo));
            if (string.IsNullOrWhiteSpace(vehiculo.Matricula))
                throw new ArgumentException("La matrícula es obligatoria.");

            int idx = -1;
            for (int i = 0; i < _datos.Count; i++)
            {
                if (string.Equals(_datos[i].Matricula, vehiculo.Matricula, StringComparison.OrdinalIgnoreCase))
                {
                    idx = i;
                    break;
                }
            }

            if (idx < 0)
                throw new KeyNotFoundException("No existe un vehículo con esa matrícula.");

            _datos[idx] = Clone(vehiculo);
        }

        public void Delete(Vehiculo vehiculo)
        {
            if (vehiculo == null) throw new ArgumentNullException(nameof(vehiculo));
            if (string.IsNullOrWhiteSpace(vehiculo.Matricula))
                throw new ArgumentException("La matrícula es obligatoria.");

            // Eliminar todas las coincidencias por matrícula (en sentido inverso para no desajustar índices)
            for (int i = _datos.Count - 1; i >= 0; i--)
            {
                if (string.Equals(_datos[i].Matricula, vehiculo.Matricula, StringComparison.OrdinalIgnoreCase))
                {
                    _datos.RemoveAt(i);
                }
            }
        }

        private static Vehiculo Clone(Vehiculo v)
        {
            return new Vehiculo
            {
                Matricula = v.Matricula,
                Marca = v.Marca,
                Modelo = v.Modelo,
                FechaMatriculacion = v.FechaMatriculacion,
                Propietario = v.Propietario,
                DniPropietario = v.DniPropietario
            };
        }

        private void Seed()
        {
            _datos.Clear();

            var v1 = new Vehiculo
            {
                Matricula = "1234ABC",
                Marca = "Toyota",
                Modelo = "Corolla",
                FechaMatriculacion = new DateTime(2018, 5, 10),
                Propietario = "Juan Pérez López",
                DniPropietario = "12345678A"
            };
            _datos.Add(v1);

            var v2 = new Vehiculo
            {
                Matricula = "5678DEF",
                Marca = "Seat",
                Modelo = "León",
                FechaMatriculacion = new DateTime(2020, 11, 2),
                Propietario = "María García Ruiz",
                DniPropietario = "87654321B"
            };
            _datos.Add(v2);

            var v3 = new Vehiculo
            {
                Matricula = "9012GHI",
                Marca = "Tesla",
                Modelo = "Model 3",
                FechaMatriculacion = new DateTime(2023, 3, 25),
                Propietario = "Carlos Sánchez Díaz",
                DniPropietario = "11223344C"
            };
            _datos.Add(v3);
        }
    }
}
