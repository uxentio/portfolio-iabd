
using System;
using System.Security.Cryptography;

internal class Program
{
    private static void Main(string[] args)
    {
        Console.WriteLine("1: Procedimiento Menu");
        Console.WriteLine("2: Funcion Menu");
        Console.WriteLine("3: Ecuación de segundo grado");
        Console.WriteLine("4: Área de un triangulo");
        Console.WriteLine("5: Array de floats");

        Console.Write("Ingrese una opción: ");
        string opcion = Console.ReadLine();
        if (opcion == "1")
        {
            ProcedimientoMenu(); 
        }
        else if (opcion == "2")
        {
            string resultado = FuncionMenu();
            Console.WriteLine(resultado);
        }
        else if (opcion == "3")
        {
            EcuacionSegundoGrado();
        }
        else if (opcion == "4")
        {
            AreaTriangulo();
        }
        else if (opcion == "5")
        {
            NumeroMayor();
        }
        else
        {
            Console.WriteLine("Opción no válida");
        }

        void ProcedimientoMenu()
        {
            Console.WriteLine("Opción 1");
            Console.WriteLine("Opción 2");
            Console.WriteLine("Opción 3");


            Console.Write("Ingrese una opción: ");
            string opcion = Console.ReadLine();
            switch (opcion)
            {
                case "1":
                    Console.WriteLine("Ha seleccionado la opción 1");
                    break;
                case "2":
                    Console.WriteLine("Ha seleccionado la opción 2");
                    break;
                case "3":
                    Console.WriteLine("Ha seleccionado la opción 3");
                    break;
                default:
                    Console.WriteLine("Opción no válida");
                    break;
            }
        }

        string FuncionMenu()
        {
            Console.WriteLine("Opción 1");
            Console.WriteLine("Opción 2");
            Console.WriteLine("Opción 3");

            Console.Write("Ingrese una opción: ");
            string opcion = Console.ReadLine();
            switch (opcion)
            {
                case "1":
                    return "Ha seleccionado la opción 1";
                case "2":
                    return "Ha seleccionado la opción 2";
                case "3":
                    return "Ha seleccionado la opción 3";
                default:
                    return "Opción no válida";
            }
        }

        void EcuacionSegundoGrado()
        {
            Console.Write("Ingrese el valor de a: ");
            double a = Convert.ToDouble(Console.ReadLine());
            Console.Write("Ingrese el valor de b: ");
            double b = Convert.ToDouble(Console.ReadLine());
            Console.Write("Ingrese el valor de c: ");
            double c = Convert.ToDouble(Console.ReadLine());

            double discriminante = b * b - 4 * a * c;

            if (discriminante > 0)
            {
                double raiz1 = (-b + Math.Sqrt(discriminante)) / (2 * a);
                double raiz2 = (-b - Math.Sqrt(discriminante)) / (2 * a);
                Console.WriteLine("Las raíces son reales y diferentes: " + raiz1 + " y " + raiz2);
            }
            else if (discriminante == 0)
            {
                double raiz = -b / (2 * a);
                Console.WriteLine("Las raíces son reales e iguales: " + raiz);
            }
            else
            {
                Console.WriteLine("Las raíces son complejas y no reales.");
            }
        }

        void AreaTriangulo()
        {
            Console.WriteLine("Ingrese la base del triangulo:");
            double baseTriangulo = Convert.ToDouble(Console.ReadLine());
            Console.WriteLine("Ingrese la altura del triangulo:");
            double alturaTriangulo = Convert.ToDouble(Console.ReadLine());
            double areaTriangulo = baseTriangulo * alturaTriangulo / 2;
            Console.WriteLine("El área del triangulo es: " + areaTriangulo);
        }

        void NumeroMayor()
        {
            Console.WriteLine("¿De que tamaño deseas el array?");
            int tamaño = Convert.ToInt32(Console.ReadLine());
            float[] array = new float[tamaño];
            Console.Write("Array generado: [ ");
            for (int i = 0; i < tamaño; i++)
            {
                array[i] = RandomNumberGenerator.GetInt32(0, 1000);
                Console.Write(array[i] + " ");
            }
            Console.WriteLine("]");

            float numeroMayor = array[0];
            for (int i = 1; i < tamaño; i++)
            {
                if (array[i] > numeroMayor)
                {
                    numeroMayor = array[i];
                }
            }

            Console.WriteLine("El número mayor es: " + numeroMayor);
        }
    }
}