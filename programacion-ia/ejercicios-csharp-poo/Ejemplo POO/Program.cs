using UT2_POO_Memoria.Modelos;
using UT2_POO_Memoria.Persistencia;
using UT2_POO_Memoria.Utilidades;

namespace UT2_POO_Memoria
{
    internal class Program
    {
        static void Main(string[] args)
        {
            var repo = new AccesoDatosMemoria();

            while (true)
            {
                Console.WriteLine();
                Console.WriteLine("1) Listar");
                Console.WriteLine("2) Insertar");
                Console.WriteLine("3) Actualizar (por matrícula)");
                Console.WriteLine("4) Eliminar (por matrícula)");
                Console.WriteLine("0) Salir");
                Console.Write("Opción: ");
                var op = Console.ReadLine();

                if (op == "0") break;

                try
                {
                    switch (op)
                    {
                        case "1":
                            foreach (var v in repo.GetAll())
                                Console.WriteLine(v);
                            break;

                        case "2":
                            {
                                var v = LeerVehiculoDeConsola();
                                if (!Validar.ValidaMatricula(v.Matricula))
                                {
                                    Console.WriteLine("Matrícula incorrecta. Formato: NNNNLLL (p. ej., 1234ABC)");
                                    break;
                                }
                                if (!Validar.ValidaNombre(v.Propietario))
                                {
                                    Console.WriteLine("Nombre incorrecto. Formato: Nombre Apellido1 Apellido2");
                                    break;
                                }
                                if (!Validar.ComparaFecha(v.FechaMatriculacion))
                                {
                                    Console.WriteLine("Fecha de matriculación inválida (no puede ser futura).");
                                    break;
                                }

                                repo.Add(v);
                                Console.WriteLine("Insertado.");
                                break;
                            }
                        case "3":
                            {
                                Console.Write("Matrícula a actualizar: ");
                                var mat = Console.ReadLine()!.Trim().ToUpperInvariant();

                                var set = repo.GetAll();
                                Vehiculo? actual = null;
                                foreach (var x in set)
                                {
                                    if (x.Matricula.Equals(mat, StringComparison.OrdinalIgnoreCase))
                                    {
                                        actual = x; break;
                                    }
                                }
                                if (actual == null)
                                {
                                    Console.WriteLine("No encontrado.");
                                    break;
                                }

                                var nuevo = LeerVehiculoDeConsola(mat);
                                repo.Update(nuevo);
                                Console.WriteLine("Actualizado.");
                                break;
                            }
                        case "4":
                            {
                                Console.Write("Matrícula a eliminar: ");
                                var mat = Console.ReadLine()!.Trim().ToUpperInvariant();
                                repo.Delete(new Vehiculo { Matricula = mat });
                                Console.WriteLine("Eliminado (si existía).");
                                break;
                            }
                        default:
                            Console.WriteLine("Opción no válida.");
                            break;
                    }
                }
                catch (NotSupportedException nse)
                {
                    Console.WriteLine($"[No implementado en este modo] {nse.Message}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[Error] {ex.Message}");
                }
            }
        }

        private static Vehiculo LeerVehiculoDeConsola(string? matPrefijada = null)
        {
            if (matPrefijada == null)
            {
                Console.Write("Matrícula (NNNNLLL): ");
                matPrefijada = Console.ReadLine()!.Trim().ToUpperInvariant();
            }

            Console.Write("Marca: ");
            var marca = Console.ReadLine()!.Trim();

            Console.Write("Modelo: ");
            var modelo = Console.ReadLine()!.Trim();

            Console.Write("Fecha matriculación (dd/MM/yyyy): ");
            var fechaStr = Console.ReadLine()!.Trim();
            var fecha = Utils.ParseFechaEs(fechaStr) ?? DateTime.Today;

            Console.Write("Propietario (Nombre Apellido1 Apellido2): ");
            var propietario = Console.ReadLine()!.Trim();

            Console.Write("DNI propietario: ");
            var dni = Console.ReadLine()!.Trim().ToUpperInvariant();

            return new Vehiculo
            {
                Matricula = matPrefijada,
                Marca = marca,
                Modelo = modelo,
                FechaMatriculacion = fecha,
                Propietario = propietario,
                DniPropietario = dni
            };
        }
    }
}
