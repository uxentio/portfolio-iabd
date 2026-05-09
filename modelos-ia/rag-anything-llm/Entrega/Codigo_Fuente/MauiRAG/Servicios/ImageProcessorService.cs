using MetadataExtractor;
using MetadataExtractor.Formats.Exif;
using MetadataExtractor.Formats.FileType;
using MetadataExtractor.Formats.Jpeg;
using MetadataExtractor.Formats.Png;

#if WINDOWS
using Windows.Graphics.Imaging;
using Windows.Media.Ocr;
using Windows.Storage;
#endif

namespace MauiRAG.Servicios
{
    // procesa imagenes: descripcion con IA (vision) + OCR + EXIF + info del archivo
    // genera un txt que se sube a anythingllm para hacer rag
    public static class ImageProcessorService
    {
        public static readonly string[] ExtensionesImagen = { ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp" };

        public static bool EsImagen(string filePath)
        {
            string ext = Path.GetExtension(filePath).ToLower();
            return ExtensionesImagen.Contains(ext);
        }

        public static async Task<string> ProcesarImagen(string filePath)
        {
            var resultado = new System.Text.StringBuilder();
            string nombreArchivo = Path.GetFileName(filePath);

            resultado.AppendLine("=========================================");
            resultado.AppendLine($"ANALISIS DE IMAGEN: {nombreArchivo}");
            resultado.AppendLine("=========================================");
            resultado.AppendLine();

            // info del archivo
            resultado.AppendLine("--- INFORMACION DEL ARCHIVO ---");
            try
            {
                var fileInfo = new FileInfo(filePath);
                resultado.AppendLine($"Nombre: {fileInfo.Name}");
                resultado.AppendLine($"Tipo: {fileInfo.Extension.ToUpper().TrimStart('.')}");
                resultado.AppendLine($"Tamano: {FormatearTamano(fileInfo.Length)}");
                resultado.AppendLine($"Fecha de creacion: {fileInfo.CreationTime}");
                resultado.AppendLine($"Ultima modificacion: {fileInfo.LastWriteTime}");
            }
            catch (Exception ex)
            {
                resultado.AppendLine($"No se pudo leer info del archivo: {ex.Message}");
            }
            resultado.AppendLine();

            // metadatos EXIF
            resultado.AppendLine("--- METADATOS EXIF ---");
            try
            {
                var directories = ImageMetadataReader.ReadMetadata(filePath);
                bool hayMetadatos = false;

                // camara
                var exifIfd0 = directories.OfType<ExifIfd0Directory>().FirstOrDefault();
                if (exifIfd0 != null)
                {
                    var marca = exifIfd0.GetDescription(ExifDirectoryBase.TagMake);
                    var modelo = exifIfd0.GetDescription(ExifDirectoryBase.TagModel);
                    var software = exifIfd0.GetDescription(ExifDirectoryBase.TagSoftware);
                    var orientacion = exifIfd0.GetDescription(ExifDirectoryBase.TagOrientation);

                    if (marca != null) { resultado.AppendLine($"Marca camara: {marca}"); hayMetadatos = true; }
                    if (modelo != null) { resultado.AppendLine($"Modelo camara: {modelo}"); hayMetadatos = true; }
                    if (software != null) { resultado.AppendLine($"Software edicion: {software}"); hayMetadatos = true; }
                    if (orientacion != null) { resultado.AppendLine($"Orientacion: {orientacion}"); hayMetadatos = true; }
                }

                // parametros tecnicos
                var exifSubIfd = directories.OfType<ExifSubIfdDirectory>().FirstOrDefault();
                if (exifSubIfd != null)
                {
                    var fechaOriginal = exifSubIfd.GetDescription(ExifDirectoryBase.TagDateTimeOriginal);
                    var exposicion = exifSubIfd.GetDescription(ExifDirectoryBase.TagExposureTime);
                    var apertura = exifSubIfd.GetDescription(ExifDirectoryBase.TagFNumber);
                    var iso = exifSubIfd.GetDescription(ExifDirectoryBase.TagIsoEquivalent);
                    var focal = exifSubIfd.GetDescription(ExifDirectoryBase.TagFocalLength);
                    var flash = exifSubIfd.GetDescription(ExifDirectoryBase.TagFlash);
                    var ancho = exifSubIfd.GetDescription(ExifDirectoryBase.TagExifImageWidth);
                    var alto = exifSubIfd.GetDescription(ExifDirectoryBase.TagExifImageHeight);

                    if (fechaOriginal != null) { resultado.AppendLine($"Fecha de captura: {fechaOriginal}"); hayMetadatos = true; }
                    if (exposicion != null) { resultado.AppendLine($"Tiempo exposicion: {exposicion}"); hayMetadatos = true; }
                    if (apertura != null) { resultado.AppendLine($"Apertura diafragma: {apertura}"); hayMetadatos = true; }
                    if (iso != null) { resultado.AppendLine($"ISO: {iso}"); hayMetadatos = true; }
                    if (focal != null) { resultado.AppendLine($"Distancia focal: {focal}"); hayMetadatos = true; }
                    if (flash != null) { resultado.AppendLine($"Flash: {flash}"); hayMetadatos = true; }
                    if (ancho != null && alto != null) { resultado.AppendLine($"Resolucion: {ancho} x {alto}"); hayMetadatos = true; }
                }

                // GPS
                var gps = directories.OfType<GpsDirectory>().FirstOrDefault();
                if (gps != null)
                {
                    var latitud = gps.GetDescription(GpsDirectory.TagLatitude);
                    var longitud = gps.GetDescription(GpsDirectory.TagLongitude);
                    var latRef = gps.GetDescription(GpsDirectory.TagLatitudeRef);
                    var lonRef = gps.GetDescription(GpsDirectory.TagLongitudeRef);
                    var altitud = gps.GetDescription(GpsDirectory.TagAltitude);

                    if (latitud != null && longitud != null)
                    {
                        resultado.AppendLine($"Coordenadas GPS: {latitud} {latRef}, {longitud} {lonRef}");
                        hayMetadatos = true;
                    }
                    if (altitud != null) { resultado.AppendLine($"Altitud: {altitud}"); hayMetadatos = true; }
                }

                // dimensiones JPEG
                var jpeg = directories.OfType<JpegDirectory>().FirstOrDefault();
                if (jpeg != null)
                {
                    var anchoJpeg = jpeg.GetDescription(JpegDirectory.TagImageWidth);
                    var altoJpeg = jpeg.GetDescription(JpegDirectory.TagImageHeight);
                    if (anchoJpeg != null && altoJpeg != null)
                    {
                        resultado.AppendLine($"Dimensiones imagen: {anchoJpeg} x {altoJpeg} pixeles");
                        hayMetadatos = true;
                    }
                }

                if (!hayMetadatos)
                    resultado.AppendLine("No se encontraron metadatos EXIF en esta imagen.");
            }
            catch (Exception ex)
            {
                resultado.AppendLine($"Error al leer metadatos: {ex.Message}");
            }
            resultado.AppendLine();

            // descripcion con modelo de vision
            resultado.AppendLine("--- DESCRIPCION DE LA IMAGEN ---");
            try
            {
                string descripcion = await ApiService.DescribirImagen(filePath);
                if (!string.IsNullOrWhiteSpace(descripcion))
                    resultado.AppendLine(descripcion);
                else
                    resultado.AppendLine("No se pudo obtener una descripcion de la imagen.");
            }
            catch (Exception ex)
            {
                resultado.AppendLine($"Error al describir la imagen: {ex.Message}");
            }
            resultado.AppendLine();

            // OCR
            resultado.AppendLine("--- TEXTO DETECTADO (OCR) ---");
            try
            {
                string textoOcr = await ExtraerTextoOCR(filePath);
                if (!string.IsNullOrWhiteSpace(textoOcr))
                    resultado.AppendLine(textoOcr);
                else
                    resultado.AppendLine("No se detecto texto en la imagen.");
            }
            catch (Exception ex)
            {
                resultado.AppendLine($"Error en OCR: {ex.Message}");
            }
            resultado.AppendLine();

            resultado.AppendLine("=========================================");
            resultado.AppendLine("Fin del analisis de imagen");
            resultado.AppendLine("=========================================");

            return resultado.ToString();
        }

        // OCR con Windows.Media.Ocr
        private static async Task<string> ExtraerTextoOCR(string filePath)
        {
#if WINDOWS
            try
            {
                var file = await StorageFile.GetFileFromPathAsync(filePath);
                using var stream = await file.OpenAsync(FileAccessMode.Read);

                var decoder = await BitmapDecoder.CreateAsync(stream);
                var bitmap = await decoder.GetSoftwareBitmapAsync();

                var ocrEngine = OcrEngine.TryCreateFromUserProfileLanguages();
                if (ocrEngine == null)
                    return "Motor OCR no disponible en este sistema.";

                var ocrResult = await ocrEngine.RecognizeAsync(bitmap);
                return ocrResult.Text;
            }
            catch (Exception ex)
            {
                return $"Error en OCR de Windows: {ex.Message}";
            }
#else
            return "OCR solo disponible en Windows.";
#endif
        }

        // guarda el texto en un .txt temporal
        public static string GuardarComoTexto(string textoAnalisis, string nombreImagenOriginal)
        {
            string nombreTxt = Path.GetFileNameWithoutExtension(nombreImagenOriginal) + "_analisis.txt";
            string rutaTemporal = Path.Combine(Path.GetTempPath(), nombreTxt);
            File.WriteAllText(rutaTemporal, textoAnalisis);
            return rutaTemporal;
        }

        private static string FormatearTamano(long bytes)
        {
            if (bytes < 1024) return $"{bytes} bytes";
            if (bytes < 1024 * 1024) return $"{bytes / 1024.0:F1} KB";
            return $"{bytes / (1024.0 * 1024.0):F1} MB";
        }
    }
}
