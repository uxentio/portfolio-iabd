// See https://aka.ms/new-console-template for more information
using System.Text;

Console.WriteLine("Hello, World!");
//1.	Escribe un programa que sume dos números y muestre el resultado.
int num1 = 5;
int num2 = 10;
int suma = num1 + num2;
Console.WriteLine("La suma de " + num1 + " y " + num2 + " es " + suma);
//2.	Escribe una sentencia de declaración y definición de una variable correspondiente a un tipo manejado por valor. Dibuja un mapa de lo que ocurre en memoria durante la declaración y durante la definición.
int numero = 5; // Declaración y definición de una variable de tipo entero
// En memoria, se reserva espacio para la variable 'numero' y se le asigna el valor 5.
//3.	Escribe un programa que permita concatenar dos palabras introducidas por el usuario.
Console.WriteLine("Introduce la primera palabra:");
string palabra1 = Console.ReadLine();
Console.WriteLine("Introduce la segunda palabra:");
string palabra2 = Console.ReadLine();
string resultado = palabra1 + " " + palabra2;
Console.WriteLine("La concatenación de las palabras es: " + resultado);
//4.	Escribe un programa que muestre el texto "La fecha actual es:", seguido de la fecha actual. Escribe tres versiones del programa: concatenando strings, mediante un StringBuilder y mediante cadenas interpoladas.
Console.WriteLine("La fecha actual es: " + DateTime.Now);//Concatenando strings
StringBuilder sb = new StringBuilder(); //Con StringBuilder
sb.Append("La fecha actual es: ");
sb.Append(DateTime.Now);
Console.WriteLine(sb.ToString());
Console.WriteLine($"La fecha actual es: {DateTime.Now}");
//5.	Declara y define una variable de tipo texto que contenga una ruta de disco duro en formato NTFS
string rutaNTFS = @"C:\Users\Usuario\Documents\archivo.txt";
Console.WriteLine("Ruta NTFS: " + rutaNTFS);