using System;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using Azure;
using Azure.AI.FormRecognizer.DocumentAnalysis;

namespace FormRecognizerWPF
{
    public partial class MainWindow : Window
    {
        private const string Endpoint = "https://uxentio.cognitiveservices.azure.com/";
        private const string ApiKey = "GAJHYJsl8OsKt6cHM0gEsr08kTL52shrYi6ynVt5bL0rc6XfUkiyJQQJ99CBAC5RqLJXJ3w3AAALACOG8tq0";
        private readonly DocumentAnalysisClient _client;

        public MainWindow()
        {
            InitializeComponent();
            _client = new DocumentAnalysisClient(new Uri(Endpoint), new AzureKeyCredential(ApiKey));
        }

        private async void BtnLoad_Click(object sender, RoutedEventArgs e)
        {
            var ofd = new Microsoft.Win32.OpenFileDialog
            {
                Filter = "Imágenes|*.png;*.jpg;*.jpeg;*.bmp"
            };
            if (ofd.ShowDialog() != true) return;

            string file = ofd.FileName;
            txtStatus.Text = "Analizando…";
            txtOutput.Clear();
            overlayCanvas.Children.Clear();

            // 1) Cargamos la imagen ráster
            var bmp = new BitmapImage(new Uri(file));

            // 2) Obtenemos el DPI real (para convertir px→DIP)
            var dpi = VisualTreeHelper.GetDpi(imgDoc);

            // 3) Calculamos tamaño en DIPs
            double dipW = bmp.PixelWidth / dpi.DpiScaleX;
            double dipH = bmp.PixelHeight / dpi.DpiScaleY;

            // 4) Ajustamos Image y Canvas a DIPs
            imgDoc.Source = bmp;
            imgDoc.Width = dipW;
            imgDoc.Height = dipH;

            overlayCanvas.Width = dipW;
            overlayCanvas.Height = dipH;

            previewGrid.Width = dipW;
            previewGrid.Height = dipH;

            // 5) Llamada a Form Recognizer
            AnalyzeResult result;
            using (var fs = File.OpenRead(file))
            {
                var op = await _client.AnalyzeDocumentAsync(WaitUntil.Completed, "prebuilt-document", fs);
                result = op.Value;
            }

            // 6) Dibujamos polígonos:
            DrawBoundingBoxes(result, dpi);

            // 7) Volcamos la info en el TextBox
            txtOutput.Text = FormatResult(result);
            txtStatus.Text = "Completado";
        }

        private void DrawBoundingBoxes(AnalyzeResult result, DpiScale dpi)
        {
            // Tomamos la primera página
            var page = result.Pages[0];

            // Azure nos da page.Width/Height en píxeles para imágenes
            double pageW_px = page.Width ?? overlayCanvas.Width * dpi.DpiScaleX;
            double pageH_px = page.Height ?? overlayCanvas.Height * dpi.DpiScaleY;

            // Para pasar px → DIPs, usamos 1 / dpiScale
            double toDipX = 1.0 / dpi.DpiScaleX;
            double toDipY = 1.0 / dpi.DpiScaleY;

            // Dibujamos líneas en rojo
            foreach (var line in page.Lines)
            {
                DrawPolygon(line.BoundingPolygon, toDipX, toDipY,
                            Brushes.Transparent, Brushes.Red, 1);
            }

            // Dibujamos selection marks en azul
            foreach (var mark in page.SelectionMarks)
            {
                DrawPolygon(mark.BoundingPolygon, toDipX, toDipY,
                            Brushes.Transparent, Brushes.Blue, 1);
            }
        }

        private void DrawPolygon(
            System.Collections.Generic.IReadOnlyList<System.Drawing.PointF> poly,
            double toDipX, double toDipY,
            Brush fill, Brush stroke, double thickness)
        {
            var shape = new Polygon
            {
                Fill = fill,
                Stroke = stroke,
                StrokeThickness = thickness
            };
            var pts = new PointCollection();
            foreach (var p in poly)
            {
                double x = p.X * toDipX;
                double y = p.Y * toDipY;
                pts.Add(new Point(x, y));
            }
            shape.Points = pts;
            overlayCanvas.Children.Add(shape);
        }

        private string FormatResult(AnalyzeResult result)
        {
            var sb = new StringBuilder();

            sb.AppendLine("=== Key-Value Pairs ===");
            foreach (var kvp in result.KeyValuePairs)
            {
                if (kvp.Value is null)
                    sb.AppendLine($"  Key sin valor: '{kvp.Key.Content}'");
                else
                    sb.AppendLine($"  {kvp.Key.Content} => {kvp.Value.Content}");
            }
            sb.AppendLine();

            sb.AppendLine("=== Fields (Documents) ===");
            foreach (var doc in result.Documents)
            {
                sb.AppendLine($" DocumentType: {doc.DocumentType}  (conf: {doc.Confidence:0.00})");
                foreach (var f in doc.Fields)
                {
                    var fld = f.Value;
                    var val = fld.Value?.ToString() ?? fld.Content;
                    sb.AppendLine($"   {f.Key}: '{val}'  [type={fld.FieldType}, conf={fld.Confidence:0.00}]");
                }
                sb.AppendLine();
            }

            sb.AppendLine("=== Pages/Layout ===");
            foreach (var p in result.Pages)
            {
                sb.AppendLine($" Page {p.PageNumber}: {p.Lines.Count} líneas, {p.Words.Count} palabras, {p.SelectionMarks.Count} marcas");
            }
            sb.AppendLine();

            sb.AppendLine("=== Tables ===");
            for (int t = 0; t < result.Tables.Count; t++)
            {
                var tbl = result.Tables[t];
                sb.AppendLine($" Table {t}: {tbl.RowCount} filas × {tbl.ColumnCount} columnas");
                foreach (var cell in tbl.Cells)
                {
                    sb.AppendLine($"   Cell({cell.RowIndex},{cell.ColumnIndex})[{cell.Kind}] '{cell.Content}'");
                }
                sb.AppendLine();
            }

            return sb.ToString();
        }
    }
}
