public abstract class GestionAlumnosAbstract
    {
        
        public abstract Alumno BuscarAlumno(Alumno alumno);
        public abstract void Insertar(Alumno alumno);
        public abstract void Eliminar(string dni);
        public abstract List<Alumno> GetAlumnos();
        public abstract int GetCount();

      
        public static Dictionary<string, int> CalcularEstadisticasNotas(List<Alumno> alumnos)
        {
            var mapa = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase)
            {
                ["Suspenso"] = 0,
                ["Aprobado"] = 0,
                ["Bien"] = 0,
                ["Notable"] = 0,
                ["Sobresaliente"] = 0
            };

            if (alumnos == null) return mapa;

            foreach (var a in alumnos)
            {
                double n = a?.Nota ?? 0.0;
                string categoria =
                    (n < 5.0) ? "Suspenso" :
                    (n < 6.0) ? "Aprobado" :
                    (n < 7.0) ? "Bien" :
                    (n < 9.0) ? "Notable" : "Sobresaliente";

                mapa[categoria]++;
            }

            return mapa;
        }
    }