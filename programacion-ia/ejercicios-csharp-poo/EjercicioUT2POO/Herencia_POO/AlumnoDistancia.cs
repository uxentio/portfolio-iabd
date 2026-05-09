public class AlumnoDistancia : Alumno
    {
        public DateTime UltimaConexion { get; set; }

        public AlumnoDistancia() : base() { }

        public AlumnoDistancia(string dni, string nombre, int edad, double nota, DateTime ultimaConexion)
            : base(dni, nombre, edad, nota)
        {
            UltimaConexion = ultimaConexion;
        }

        public override string ToString()
            => $"AlumnoDistancia[DNI={Dni}, Nombre={Nombre}, Edad={Edad}, Nota={Nota:F2}, UltimaConexion={UltimaConexion:yyyy-MM-dd}]";
    }