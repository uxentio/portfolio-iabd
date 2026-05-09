using Azure;
using Azure.AI.FormRecognizer.DocumentAnalysis;

namespace FacturasOCR.Servicios;

// Servicio que conecta con Azure Document Intelligence para el OCR
public class ServicioAnalisis
{
    // Endpoint y clave por defecto (los del recurso de clase)
    // Se pueden cambiar en Ajustes
    public const string DefaultEndpoint = "https://uxentio.cognitiveservices.azure.com/";
    public const string DefaultApiKey = "GAJHYJsl8OsKt6cHM0gEsr08kTL52shrYi6ynVt5bL0rc6XfUkiyJQQJ99CBAC5RqLJXJ3w3AAALACOG8tq0";

    private DocumentAnalysisClient _client;

    public ServicioAnalisis()
    {
        // Leemos el endpoint y clave guardados, o usamos los de clase
        string endpoint = Preferences.Get("AzureEndpoint", DefaultEndpoint);
        string apiKey = Preferences.Get("AzureApiKey", DefaultApiKey);

        _client = new DocumentAnalysisClient(
            new Uri(endpoint),
            new AzureKeyCredential(apiKey));
    }

    // Manda el documento a Azure y devuelve el resultado del analisis
    // Usamos prebuilt-invoice porque es el modelo que mejor extrae datos de facturas
    public async Task<AnalyzeResult> AnalyzeDocumentAsync(Stream imageStream)
    {
        var operation = await _client.AnalyzeDocumentAsync(
            WaitUntil.Completed,
            "prebuilt-invoice",
            imageStream);

        return operation.Value;
    }
}
