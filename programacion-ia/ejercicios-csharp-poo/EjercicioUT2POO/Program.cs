namespace Herencia_POO
{
    // ========== PROGRAMA PRINCIPAL (conversión de Main.java) ==========
    public class Program
    {
        public static void Main(string[] args)
        {
            System.Console.WriteLine("Seleccione la implementación de gestión de alumnos:");
            System.Console.WriteLine("1. GestionAlumnoArray");
            System.Console.WriteLine("2. GestionAlumnoColecciones");
            System.Console.Write("Opción: ");

            int eleccion;
            string linea = System.Console.ReadLine();
            if (!int.TryParse(linea, out eleccion)) eleccion = 2;

            GestionAlumnosAbstract gestion;
            if (eleccion == 1) gestion = new GestionAlumnosArray(10);
            else gestion = new GestionAlumnosColeccion();

            bool salir = false;
            while (!salir)
            {
                System.Console.WriteLine("\n--- Menú de Gestión de Alumnos ---");
                System.Console.WriteLine("1. Insertar alumnos");
                System.Console.WriteLine("2. Mostrar todos los alumnos (ordenados)");
                System.Console.WriteLine("3. Eliminar alumno (elimina DNI: 22222222B)");
                System.Console.WriteLine("4. Mostrar número de alumnos creados");
                System.Console.WriteLine("5. Buscar alumno por DNI (buscando DNI: 33333333C)");
                System.Console.WriteLine("6. Mostrar estadísticas de las notas");
                System.Console.WriteLine("0. Salir");
                System.Console.Write("Opción: ");

                int opcion;
                string s = System.Console.ReadLine();
                if (!int.TryParse(s, out opcion)) opcion = -1;

                switch (opcion)
                {
                    case 1:
                        Alumno[] hardcoded = new Alumno[] {
                            new AlumnoPresencial("11111111A","Alice",20,7.5,"Aula 101"),
                            new AlumnoDistancia("22222222B","Bob",22,4.5,new DateTime(2023,3,15)),
                            new AlumnoPresencial("33333333C","Charlie",19,9.0,"Aula 102"),
                            new AlumnoDistancia("44444444D","Diana",21,6.8,new DateTime(2023,3,16)),
                            new AlumnoPresencial("55555555E","Eva",20,8.5,"Aula 103"),
                            new AlumnoDistancia("66666666F","Frank",23,4.0,new DateTime(2023,3,17)),
                            new AlumnoPresencial("77777777G","Grace",21,6.5,"Aula 104"),
                            new AlumnoDistancia("88888888H","Héctor",19,7.0,new DateTime(2023,3,18)),
                            new AlumnoPresencial("99999999I","Irene",22,8.0,"Aula 105"),
                            new AlumnoDistancia("10101010J","James",20,9.5,new DateTime(2023,3,19))
                        };
                        for (int i = 0; i < hardcoded.Length; i++)
                        {
                            gestion.Insertar(hardcoded[i]);
                        }
                        System.Console.WriteLine("Alumnos hardcodeados insertados correctamente.");
                        break;

                    case 2:
                        List<Alumno> todos = gestion.GetAlumnos();
                        if (todos.Count == 0)
                        {
                            System.Console.WriteLine("No hay alumnos registrados.");
                        }
                        else
                        {
                            // Orden por nombre
                            todos.Sort();
                            System.Console.WriteLine("Listado de alumnos (ordenados por nombre):");
                            for (int i = 0; i < todos.Count; i++)
                            {
                                System.Console.WriteLine(todos[i].ToString());
                            }
                        }
                        break;

                    case 3:
                        gestion.Eliminar("22222222B");
                        break;

                    case 4:
                        System.Console.WriteLine("Número de alumnos creados: " + gestion.GetCount());
                        break;

                    case 5:
                        Alumno alumnoBuscado = gestion.BuscarAlumno(new Alumno("33333333C", "", 0, 0.0));
                        if (alumnoBuscado != null)
                            System.Console.WriteLine("Alumno encontrado: " + alumnoBuscado.ToString());
                        else
                            System.Console.WriteLine("Alumno NO encontrado.");
                        break;

                    case 6:
                        List<Alumno> lista = gestion.GetAlumnos();
                        Dictionary<string, int> estad = GestionAlumnosAbstract.CalcularEstadisticasNotas(lista);
                        System.Console.WriteLine("Estadísticas de notas:");
                        foreach (KeyValuePair<string, int> kv in estad)
                        {
                            System.Console.WriteLine(kv.Key + ": " + kv.Value);
                        }
                        break;

                    case 0:
                        System.Console.WriteLine("Saliendo.");
                        salir = true;
                        break;

                    default:
                        System.Console.WriteLine("Opción no válida.");
                        break;
                }
            }
        }
    }
}
}
