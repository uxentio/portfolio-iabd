public class GestionAlumnosArray : GestionAlumnosAbstract
    {
        private readonly Alumno[] _alumnos;
        private int _count;

        public GestionAlumnosArray(int capacidad)
        {
            if (capacidad <= 0) capacidad = 10;
            _alumnos = new Alumno[capacidad];
            _count = 0;
        }

        public override void Insertar(Alumno alumno)
        {
            if (alumno == null) return;

           
            if (BuscarAlumno(alumno) != null) return;

            if (_count >= _alumnos.Length)
            {
                Console.WriteLine("No hay espacio disponible en el array.");
                return;
            }

            _alumnos[_count++] = alumno;
        }

        public override Alumno BuscarAlumno(Alumno alumno)
        {
            if (alumno == null) return null;
            for (int i = 0; i < _count; i++)
            {
                if (_alumnos[i] != null && _alumnos[i].Equals(alumno))
                    return _alumnos[i];
            }
            return null;
        }

        public override void Eliminar(string dni)
        {
            if (string.IsNullOrWhiteSpace(dni)) return;

            int idx = -1;
            for (int i = 0; i < _count; i++)
            {
                if (_alumnos[i] != null &&
                    string.Equals(_alumnos[i].Dni, dni, StringComparison.OrdinalIgnoreCase))
                {
                    idx = i; break;
                }
            }

            if (idx == -1) return;

            
            for (int i = idx; i < _count - 1; i++)
                _alumnos[i] = _alumnos[i + 1];

            _alumnos[_count - 1] = null;
            _count--;
        }

        public override List<Alumno> GetAlumnos()
        {
            var lista = new List<Alumno>(_count);
            for (int i = 0; i < _count; i++)
                if (_alumnos[i] != null) lista.Add(_alumnos[i]);
            return lista;
        }

        public override int GetCount() => _count;
    }