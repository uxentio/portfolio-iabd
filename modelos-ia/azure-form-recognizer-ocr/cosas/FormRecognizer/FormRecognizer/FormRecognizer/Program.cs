using System;
using System.Threading.Tasks;
using Azure;
using Azure.AI.FormRecognizer.DocumentAnalysis;

namespace FormRecognizer
{
    public class Program
    {
        // Punto de conexión y clave del servicio de Azure
        private const string Endpoint = "https://uxentio.cognitiveservices.azure.com/";
        private const string ApiKey = "GAJHYJsl8OsKt6cHM0gEsr08kTL52shrYi6ynVt5bL0rc6XfUkiyJQQJ99CBAC5RqLJXJ3w3AAALACOG8tq0";

        // URI del documento que se analizará
        private static readonly Uri fileUri = new Uri(
            "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"
        );

        public static async Task Main(string[] args)
        {
            var client = new DocumentAnalysisClient(
                new Uri(Endpoint),
                new AzureKeyCredential(ApiKey)
            );

            // Inicia y espera la operación de análisis
            AnalyzeDocumentOperation operation = await client
                .AnalyzeDocumentFromUriAsync(
                    WaitUntil.Completed,
                    "prebuilt-document",
                    fileUri
                );

            // Obtenemos el resultado una vez completado
            AnalyzeResult result = operation.Value;

            ShowKeyValuePairsSummary(result);
            ShowEntitiesSummary(result);
            ShowLayoutAndMarksSummary(result);
            ShowHandwrittenSectionsSummary(result);
            ShowTablesSummary(result);
        }

        private static void ShowKeyValuePairsSummary(AnalyzeResult result)
        {
            Console.WriteLine("Detected key-value pairs:");
            foreach (var kvp in result.KeyValuePairs)
            {
                if (kvp.Value == null)
                    Console.WriteLine($"  Key sin valor: '{kvp.Key.Content}'");
                else
                    Console.WriteLine($"  Pair: '{kvp.Key.Content}' => '{kvp.Value.Content}'");
            }
            Console.WriteLine();
        }

        private static void ShowEntitiesSummary(AnalyzeResult result)
        {
            Console.WriteLine("Detected entities (fields) in each document:");
            foreach (AnalyzedDocument doc in result.Documents)
            {
                Console.WriteLine($" Document Type: {doc.DocumentType} (confidence: {doc.Confidence:0.00})");

                if (doc.Fields.Count == 0)
                {
                    Console.WriteLine("   (no fields detected)");
                }
                else
                {
                    foreach (var kvp in doc.Fields)
                    {
                        string name = kvp.Key;
                        DocumentField fld = kvp.Value;
                        string valueText = fld.Value?.ToString() ?? fld.Content;
                        Console.WriteLine(
                            $"   Field '{name}': '{valueText}' " +
                            $"(type: {fld.FieldType}, confid.: {fld.Confidence:0.00})"
                        );
                    }
                }

                Console.WriteLine();
            }
        }

        private static void ShowLayoutAndMarksSummary(AnalyzeResult result)
        {
            foreach (var page in result.Pages)
            {
                Console.WriteLine(
                    $"Página {page.PageNumber}: " +
                    $"{page.Lines.Count} líneas, {page.Words.Count} palabras, " +
                    $"{page.SelectionMarks.Count} marcas"
                );

                // Líneas y su polígono
                for (int i = 0; i < page.Lines.Count; i++)
                {
                    var line = page.Lines[i];
                    Console.WriteLine($"  Línea {i}: '{line.Content}'");
                    Console.WriteLine("    BoundingPolygon:");
                    Console.WriteLine(
                        $"      UL=({line.BoundingPolygon[0].X:0.00},{line.BoundingPolygon[0].Y:0.00})  " +
                        $"UR=({line.BoundingPolygon[1].X:0.00},{line.BoundingPolygon[1].Y:0.00})"
                    );
                    Console.WriteLine(
                        $"      LR=({line.BoundingPolygon[2].X:0.00},{line.BoundingPolygon[2].Y:0.00})  " +
                        $"LL=({line.BoundingPolygon[3].X:0.00},{line.BoundingPolygon[3].Y:0.00})"
                    );
                }

                // Selection marks y su polígono
                for (int i = 0; i < page.SelectionMarks.Count; i++)
                {
                    var mark = page.SelectionMarks[i];
                    Console.WriteLine($"  Mark {i}: {mark.State}");
                    Console.WriteLine("    BoundingPolygon:");
                    Console.WriteLine(
                        $"      UL=({mark.BoundingPolygon[0].X:0.00},{mark.BoundingPolygon[0].Y:0.00})  " +
                        $"UR=({mark.BoundingPolygon[1].X:0.00},{mark.BoundingPolygon[1].Y:0.00})"
                    );
                    Console.WriteLine(
                        $"      LR=({mark.BoundingPolygon[2].X:0.00},{mark.BoundingPolygon[2].Y:0.00})  " +
                        $"LL=({mark.BoundingPolygon[3].X:0.00},{mark.BoundingPolygon[3].Y:0.00})"
                    );
                }

                Console.WriteLine();
            }
        }

        private static void ShowHandwrittenSectionsSummary(AnalyzeResult result)
        {
            Console.WriteLine("Handwritten sections:");
            foreach (var style in result.Styles)
            {
                if (style.IsHandwritten == true && style.Confidence > 0.8)
                {
                    foreach (var span in style.Spans)
                    {
                        string snippet = result.Content.Substring(span.Index, span.Length);
                        Console.WriteLine($"  '{snippet}'");
                    }
                }
            }
            Console.WriteLine();
        }

        private static void ShowTablesSummary(AnalyzeResult result)
        {
            Console.WriteLine("The following tables were extracted:");
            for (int t = 0; t < result.Tables.Count; t++)
            {
                var table = result.Tables[t];
                Console.WriteLine($"  Table {t}: {table.RowCount} rows x {table.ColumnCount} columns");

                foreach (var cell in table.Cells)
                {
                    Console.WriteLine(
                        $"    Cell ({cell.RowIndex},{cell.ColumnIndex}) " +
                        $"[{cell.Kind}] '{cell.Content}'"
                    );
                }
            }
            Console.WriteLine();
        }
    }
}
