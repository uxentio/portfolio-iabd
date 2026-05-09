using System.Diagnostics;
using System.Text.RegularExpressions;

namespace MauiRAG.Servicios
{
    // llama a los scripts de python para preprocesar PDFs y videos de YouTube
    // antes de subirlos a anythingllm
    public static class PythonProcessorService
    {
        public static string ScriptsPath { get; set; } = "";
        public static string PythonExePath { get; set; } = "python";

        public static bool EsPdf(string filePath)
        {
            string ext = Path.GetExtension(filePath).ToLower();
            return ext == ".pdf";
        }

        public static bool EsUrlYouTube(string url)
        {
            if (string.IsNullOrWhiteSpace(url)) return false;
            return url.Contains("youtube.com/watch") || url.Contains("youtu.be/")
                || url.Contains("youtube.com/embed/") || url.Contains("youtube.com/shorts/");
        }

        // llama a segmentar_pdf_por_pagina.py y devuelve la ruta del txt generado
        public static async Task<string> ProcesarPdf(string pdfPath)
        {
            string scriptPath = Path.Combine(ScriptsPath, "segmentar_pdf_por_pagina.py");
            if (!File.Exists(scriptPath))
                throw new FileNotFoundException($"No se encontro el script '{scriptPath}'. Configura la ruta en Config.");

            await EjecutarPython(scriptPath, $"\"{pdfPath}\"");

            // el script genera {nombre}_segmentado.txt en la misma carpeta del PDF
            string nombreBase = Path.GetFileNameWithoutExtension(pdfPath);
            string carpetaPdf = Path.GetDirectoryName(pdfPath);
            string archivoSalida = Path.Combine(carpetaPdf, $"{nombreBase}_segmentado.txt");

            if (!File.Exists(archivoSalida))
                throw new FileNotFoundException($"El script termino pero no genero '{archivoSalida}'");

            return archivoSalida;
        }

        // llama a transcribir_video_youtube.py y devuelve la ruta del txt generado
        public static async Task<string> ProcesarYouTube(string url)
        {
            string scriptPath = Path.Combine(ScriptsPath, "transcribir_video_youtube.py");
            if (!File.Exists(scriptPath))
                throw new FileNotFoundException($"No se encontro el script '{scriptPath}'. Configura la ruta en Config.");

            // extraer el video ID para saber como se llamara el archivo de salida
            string videoId = ExtraerVideoId(url);
            if (string.IsNullOrEmpty(videoId))
                throw new ArgumentException($"No se pudo extraer el ID del video de '{url}'");

            await EjecutarPython(scriptPath, $"\"{url}\" es");

            // el script genera transcripcion_{id}.txt en la carpeta del script
            string archivoSalida = Path.Combine(ScriptsPath, $"transcripcion_{videoId}.txt");

            if (!File.Exists(archivoSalida))
                throw new FileNotFoundException($"El script termino pero no genero '{archivoSalida}'");

            return archivoSalida;
        }

        // extrae el ID de 11 caracteres de una URL de YouTube
        private static string ExtraerVideoId(string url)
        {
            var patrones = new[]
            {
                @"[?&]v=([\w-]{11})",
                @"youtu\.be/([\w-]{11})",
                @"youtube\.com/embed/([\w-]{11})",
                @"youtube\.com/shorts/([\w-]{11})"
            };

            foreach (var patron in patrones)
            {
                var match = Regex.Match(url, patron);
                if (match.Success)
                    return match.Groups[1].Value;
            }

            // si ya es un ID directo
            if (Regex.IsMatch(url.Trim(), @"^[\w-]{11}$"))
                return url.Trim();

            return null;
        }

        // ejecuta un script de python y espera a que termine
        private static async Task EjecutarPython(string scriptPath, string args)
        {
            var psi = new ProcessStartInfo
            {
                FileName = PythonExePath,
                Arguments = $"\"{scriptPath}\" {args}",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                WorkingDirectory = Path.GetDirectoryName(scriptPath)
            };

            using var process = new Process { StartInfo = psi };

            try
            {
                process.Start();
            }
            catch (Exception ex)
            {
                throw new Exception("No se pudo ejecutar Python. Asegurate de tener Python 3 instalado y en el PATH.\n" + ex.Message);
            }

            string stdout = await process.StandardOutput.ReadToEndAsync();
            string stderr = await process.StandardError.ReadToEndAsync();

            await process.WaitForExitAsync();

            if (process.ExitCode != 0)
            {
                string error = !string.IsNullOrWhiteSpace(stderr) ? stderr : stdout;
                throw new Exception($"El script fallo (codigo {process.ExitCode}):\n{error.Trim()}");
            }
        }
    }
}
