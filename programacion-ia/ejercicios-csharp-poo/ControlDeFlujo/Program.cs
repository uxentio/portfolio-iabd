using System;
using System.Security.Cryptography;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("=== EJERCICIOS C# ===");
        Console.WriteLine("Selecciona que ejercicio ejecutar (1-14 o 0 para salir):");

        int opcion;
        do
        {
            Console.Write("\nEjercicio: ");
            if (int.TryParse(Console.ReadLine(), out opcion))
            {

                switch (opcion)
                {
                    case 1: Ejercicio1(); break;
                    case 2: Ejercicio2(); break;
                    case 3: Ejercicio3(); break;
                    case 4: Ejercicio4(); break;
                    case 5: Ejercicio5(); break;
                    case 6: Ejercicio6(); break;
                    case 7: Ejercicio7(); break;
                    case 8: Ejercicio8(); break;
                    case 9: Ejercicio9(); break;
                    case 10: Ejercicio10(); break;
                    case 11: Ejercicio11(); break;
                    case 12: Ejercicio12(); break;
                    case 13: Ejercicio13(); break;
                    case 14: Ejercicio14(); break;
                }
            }
        } while (opcion != 0);

        // Ejercicio 1
        static void Ejercicio1()
        {
            Console.Write("Introduce el primer número: ");
            int num1 = int.Parse(Console.ReadLine());
            Console.Write("Introduce el segundo número: ");
            int num2 = int.Parse(Console.ReadLine());

            if (num1 >= 0 && num2 >= 0)
            {
                int suma = num1 + num2;
                Console.WriteLine($"La suma de {num1} y {num2} es {suma}");
            }
            else
            {
                Console.WriteLine("Error: Ambos números deben ser positivos.");
            }
        }
        // Ejercicio 2
        static void Ejercicio2()
        {
            Console.Write("Introduce el primer número: ");
            int num1 = int.Parse(Console.ReadLine());
            Console.Write("Introduce el segundo número: ");
            int num2 = int.Parse(Console.ReadLine());

            if (num1 > num2)
            {
                Console.WriteLine($"El número mayor es {num1}");
            }
            else if (num2 > num1)
            {
                Console.WriteLine($"El número mayor es {num2}");
            }
            else
            {
                Console.WriteLine("Los números son iguales.");
            }
        }
        // Ejercicio 3
        static void Ejercicio3()
        {
            for (int i = 1; i <= 5; i++)
            {
                Console.WriteLine(i);
            }
        }
        // Ejercicio 4
        static void Ejercicio4()
        {
            int i = 1;
            while (i <= 5)
            {
                Console.WriteLine(i);
                i++;
            }
        }
        // Ejercicio 5
        static void Ejercicio5()
        {
            int i = 1;
            do
            {
                Console.WriteLine(i);
                i++;
            } while (i <= 5);
        }
        // Ejercicio 6
        static void Ejercicio6()
        {
            Console.Write("Introduce tamaño del array: ");
            int tamano = int.Parse(Console.ReadLine());
            int[] numeros = new int[tamano];
            for (int i = 0; i < numeros.Length; i++)
            {
                Console.Write($"Introduce el número {i + 1}: ");
                numeros[i] = int.Parse(Console.ReadLine());
            }

            Console.WriteLine("Contenido del array:");
            foreach (int num in numeros)
            {
                Console.WriteLine(num);
            }
        }
        // Ejercicio 7
        static void Ejercicio7()
        {
            Console.Write("Introduce el primer número: ");
            int num1 = int.Parse(Console.ReadLine());
            Console.Write("Introduce el segundo número: ");
            int num2 = int.Parse(Console.ReadLine());
            Console.Write("Introduce el tercer número: ");
            int num3 = int.Parse(Console.ReadLine());

            double media = (num1 + num2 + num3) / 3.0;
            Console.WriteLine($"La media aritmética es: {media}");
        }
        // Ejercicio 8
        static void Ejercicio8()
        {
            Random random = new Random();
            double suma = 0;

            for (int i = 0; i < 50; i++)
            {
                int numero = random.Next(1, 101); // Número aleatorio entre 1 y 100
                suma += numero;
            }
            Console.WriteLine("Números generados:");
            for (int i = 0; i < 50; i++)
            {
                int numero = random.Next(1, 101);
                Console.WriteLine(numero);
            }
            double media = suma / 50;
            Console.WriteLine($"La media de los 50 números aleatorios es: {media}");
        }
        // Ejercicio 9
        static void Ejercicio9()
        {
            Console.Write("¿Cuántos números quieres introducir (máximo 50)? ");
            int cantidad = int.Parse(Console.ReadLine());
            if (cantidad < 1 || cantidad > 50)
            {
                Console.WriteLine("Cantidad inválida. Debe ser entre 1 y 50.");
                return;
            }

            double?[] numeros = new double?[50];
            for (int i = 0; i < cantidad; i++)
            {
                numeros[i] = RandomNumberGenerator.GetInt32(1, 50)
            }

            double suma = 0;
            int contador = 0;
            foreach (var num in numeros)
            {
                if (num.HasValue)
                {
                    suma += num.Value;
                    contador++;
                }
            }

            if (contador > 0)
            {
                double media = suma / contador;
                Console.WriteLine($"La media de los números introducidos es: {media}");
            }
            else
            {
                Console.WriteLine("No se han introducido números.");
            }
        }
        // Ejercicio 10
        static void Ejercicio10()
        {

        }
        // Ejercicio 11
        static void Ejercicio11()
        {

        }
        // Ejercicio 12
        static void Ejercicio12()
        {

        }
        // Ejercicio 13
        static void Ejercicio13()
        {

        }
        // Ejercicio 143
        static void Ejercicio14()
        {

        }
    }
}   
