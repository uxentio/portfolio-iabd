public class GestionAlumnosColeccion : GestionAlumnosAbstract
    {
        private readonly List<Alumno> _lista = new List<Alumno>();

        public override void Insertar(Alumno alumno)
        {
            if (alumno == null) return;
            // Evitar duplicados por DNI
            if (_lista.Any(a => a.Equals(alumno))) return;
            _lista.Add(alumno);
        }

        public override Alumno BuscarAlumno(Alumno alumno)
        {
            if (alumno == null) return null;
            return _lista.FirstOrDefault(a => a.Equals(alumno));
        }

        public override void Eliminar(string dni)
        {
            if (string.IsNullOrWhiteSpace(dni)) return;
            _lista.RemoveAll(a => string.Equals(a.Dni, dni, StringComparison.OrdinalIgnoreCase));
        }

        public override List<Alumno> GetAlumnos()
        {
            // Devolver copia defensiva
            return new List<Alumno>(_lista);
        }

        public override int GetCount() => _lista.Count;
    }
}
