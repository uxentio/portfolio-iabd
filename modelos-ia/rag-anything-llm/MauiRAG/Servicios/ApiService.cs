using System.Net.Http.Headers;
using System.Text;
using Newtonsoft.Json;

namespace MauiRAG.Servicios
{
    // servicio para la api de anythingllm
    public static class ApiService
    {
        // se configuran desde la pantalla de config
        public static string BaseUrl = "http://localhost:3001/api";
        public static string ApiKey = "";
        public static string SystemPrompt = "";
        public static string LmStudioUrl = "http://localhost:1234";

        private static HttpClient GetClient()
        {
            var client = new HttpClient();
            client.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", ApiKey);
            return client;
        }

        // --- WORKSPACES ---

        public static async Task<string> ObtenerWorkspaces()
        {
            using var client = GetClient();
            var response = await client.GetAsync($"{BaseUrl}/v1/workspaces");
            if (response.IsSuccessStatusCode)
                return await response.Content.ReadAsStringAsync();
            else
                return null;
        }

        public static async Task<string> CrearWorkspace(string nombre)
        {
            using var client = GetClient();
            var payload = new { name = nombre };
            var json = JsonConvert.SerializeObject(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await client.PostAsync($"{BaseUrl}/v1/workspace/new", content);
            if (response.IsSuccessStatusCode)
                return await response.Content.ReadAsStringAsync();
            else
                return null;
        }

        public static async Task<bool> RenombrarWorkspace(string slug, string nuevoNombre)
        {
            using var client = GetClient();
            var payload = new { name = nuevoNombre };
            var json = JsonConvert.SerializeObject(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await client.PostAsync($"{BaseUrl}/v1/workspace/{slug}/update", content);
            return response.IsSuccessStatusCode;
        }

        public static async Task<bool> EliminarWorkspace(string slug)
        {
            using var client = GetClient();
            var response = await client.DeleteAsync($"{BaseUrl}/v1/workspace/{slug}");
            return response.IsSuccessStatusCode;
        }

        // --- DOCUMENTOS ---

        public static async Task<dynamic> SubirDocumento(string filePath)
        {
            using var client = GetClient();
            string nombreArchivo = Path.GetFileName(filePath);

            var form = new MultipartFormDataContent();
            byte[] fileBytes = File.ReadAllBytes(filePath);
            var fileContent = new ByteArrayContent(fileBytes);
            fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");
            form.Add(fileContent, "file", nombreArchivo);

            var response = await client.PostAsync($"{BaseUrl}/v1/document/upload", form);
            if (response.IsSuccessStatusCode)
            {
                string resultado = await response.Content.ReadAsStringAsync();
                dynamic json = JsonConvert.DeserializeObject(resultado);
                return json.documents[0];
            }
            return null;
        }

        public static async Task<bool> ActualizarEmbeddings(string slug, string location)
        {
            using var client = GetClient();
            var payload = new
            {
                adds = new[] { location },
                deletes = new string[0]
            };

            var json = JsonConvert.SerializeObject(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await client.PostAsync($"{BaseUrl}/v1/workspace/{slug}/update-embeddings", content);
            return response.IsSuccessStatusCode;
        }

        public static async Task<string> ObtenerDocumentos()
        {
            using var client = GetClient();
            var response = await client.GetAsync($"{BaseUrl}/v1/documents");
            if (response.IsSuccessStatusCode)
                return await response.Content.ReadAsStringAsync();
            else
                return null;
        }

        public static async Task<bool> EliminarDocumentos(List<string> nombres)
        {
            using var client = GetClient();
            var payload = new { names = nombres };
            var json = JsonConvert.SerializeObject(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            // DELETE con body necesita SendAsync
            var request = new HttpRequestMessage(HttpMethod.Delete, $"{BaseUrl}/v1/system/remove-documents")
            {
                Content = content
            };
            var response = await client.SendAsync(request);
            return response.IsSuccessStatusCode;
        }

        // --- VISION (LM Studio) ---

        // busca automaticamente un modelo de vision entre los disponibles en lm studio
        private static async Task<string> DetectarModeloVision()
        {
            try
            {
                using var client = new HttpClient();
                client.Timeout = TimeSpan.FromSeconds(10);
                var response = await client.GetAsync($"{LmStudioUrl}/v1/models");
                if (response.IsSuccessStatusCode)
                {
                    string resultado = await response.Content.ReadAsStringAsync();
                    dynamic json = JsonConvert.DeserializeObject(resultado);

                    // busco un modelo que tenga "llava" o "vision" en el nombre
                    foreach (var model in json.data)
                    {
                        string id = ((string)model.id).ToLower();
                        if (id.Contains("llava") || id.Contains("vision"))
                            return (string)model.id;
                    }
                }
            }
            catch { }
            return null;
        }

        // manda una imagen al modelo de vision de lm studio para que la describa
        public static async Task<string> DescribirImagen(string filePath)
        {
            try
            {
                // primero detecto que modelo de vision hay disponible
                string modeloVision = await DetectarModeloVision();
                if (modeloVision == null)
                    return "No se encontro ningun modelo de vision en LM Studio. Carga un modelo como LLaVA o Llama Vision.";

                // paso la imagen a base64
                byte[] imageBytes = File.ReadAllBytes(filePath);
                string base64 = Convert.ToBase64String(imageBytes);
                string extension = Path.GetExtension(filePath).ToLower().TrimStart('.');
                if (extension == "jpg") extension = "jpeg";
                string dataUri = $"data:image/{extension};base64,{base64}";

                // armo el payload con formato openai vision usando el modelo detectado
                var payload = new
                {
                    model = modeloVision,
                    messages = new[]
                    {
                        new
                        {
                            role = "user",
                            content = new object[]
                            {
                                new { type = "text", text = "Describe esta imagen en detalle en español. Indica qué se ve, los elementos principales, colores, personas u objetos, y cualquier detalle relevante." },
                                new { type = "image_url", image_url = new { url = dataUri } }
                            }
                        }
                    },
                    max_tokens = 500
                };

                using var client = new HttpClient();
                client.Timeout = TimeSpan.FromSeconds(120); // puede tardar un rato en CPU

                var json = JsonConvert.SerializeObject(payload);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await client.PostAsync($"{LmStudioUrl}/v1/chat/completions", content);
                if (response.IsSuccessStatusCode)
                {
                    string resultado = await response.Content.ReadAsStringAsync();
                    dynamic respuesta = JsonConvert.DeserializeObject(resultado);
                    return (string)respuesta.choices[0].message.content;
                }
                else
                {
                    return $"El modelo '{modeloVision}' no pudo describir la imagen (HTTP {(int)response.StatusCode}). Asegurate de tener el modelo cargado en LM Studio.";
                }
            }
            catch (Exception ex)
            {
                return $"No se pudo conectar con LM Studio para describir la imagen: {ex.Message}";
            }
        }

        // --- CHAT ---

        public static async Task<dynamic> EnviarMensaje(string slug, string mensaje, string modo, string sessionId)
        {
            using var client = GetClient();

            var payload = new Dictionary<string, object>
            {
                { "message", mensaje },
                { "mode", modo },
                { "sessionId", sessionId },
                { "attachments", new object[0] }
            };

            // mando el system prompt si esta configurado
            if (!string.IsNullOrEmpty(SystemPrompt))
            {
                payload["systemPrompt"] = SystemPrompt;
            }

            var json = JsonConvert.SerializeObject(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await client.PostAsync($"{BaseUrl}/v1/workspace/{slug}/chat", content);
            if (response.IsSuccessStatusCode)
            {
                string resultado = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject(resultado);
            }
            return null;
        }
    }
}
