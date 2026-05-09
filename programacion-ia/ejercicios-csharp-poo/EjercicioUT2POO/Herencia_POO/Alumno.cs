namespace Herencia_POO { 
public class Alumno : IComparable
    {
        
        public string Dni { get; set; }
        public string Nombre { get; set; }
        public int Edad { get; set; }
        public double Nota { get; set; }

       
        public Alumno()
        {
            Nombre = string.Empty;
            Edad = 0;
            Dni = string.Empty;
            Nota = 0.0;
        }

        public Alumno(string dni, string nombre, int edad, double nota)
        {
            Dni = dni;
            Nombre = nombre;
            Edad = edad;
            Nota = nota;
        }

        
        public int CompareTo(Alumno other)
        {
            if (other is null) return 1;
            return string.Compare(Nombre, other.Nombre, StringComparison.CurrentCultureIgnoreCase);
        }

        
        public bool Equals(Alumno other)
        {
            if (other is null) return false;
            return string.Equals(Dni, other.Dni, StringComparison.OrdinalIgnoreCase);
        }

        public override bool Equals(object obj) => Equals(obj as Alumno);

        public override int GetHashCode() => (Dni ?? string.Empty).ToUpperInvariant().GetHashCode();

        
        public override string ToString()
            => $"Alumno[DNI={Dni}, Nombre={Nombre}, Edad={Edad}, Nota={Nota:F2}]";
    }
}