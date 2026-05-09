public class AlumnoPresencial : Alumno
    {
        public string Aula { get; set; }

        public AlumnoPresencial() : base() { }

        public AlumnoPresencial(string dni, string nombre, int edad, double nota, string aula)
            : base(dni, nombre, edad, nota)
        {
            Aula = aula;
        }

        public override string ToString()
            => $"AlumnoPresencial[DNI={Dni}, Nombre={Nombre}, Edad={Edad}, Nota={Nota:F2}, Aula={Aula}]";
    }