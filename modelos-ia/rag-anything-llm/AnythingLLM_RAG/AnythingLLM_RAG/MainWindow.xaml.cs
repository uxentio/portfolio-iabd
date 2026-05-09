using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using Microsoft.Win32;
using Newtonsoft.Json;

namespace AnythingLLM_RAG
{
    public partial class MainWindow : Window
    {
        private const string API_KEY = "4718F5C-WCW4XV2-M3Y4304-X9B53CG";
        private const string SLUG = "maxi";
        private const string BASE_URL = "http://localhost:3001/api";

        public MainWindow()
        {
            InitializeComponent();
        }

        /// <summary>
        /// Sube el documento y retorna el objeto (dinámico) con la información devuelta.
        /// </summary>
        private async Task<dynamic> UploadDocument(HttpClient client, string filePath)
        {
            string originalFileName = Path.GetFileName(filePath);
            MultipartFormDataContent form = new MultipartFormDataContent();
            form.Add(new StringContent(SLUG), "slug");
            byte[] fileBytes = File.ReadAllBytes(filePath);
            ByteArrayContent fileContent = new ByteArrayContent(fileBytes);
            fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");
            form.Add(fileContent, "file", originalFileName);

            HttpResponseMessage uploadResponse = await client.PostAsync($"{BASE_URL}/v1/document/upload", form);
            if (uploadResponse.IsSuccessStatusCode)
            {
                string uploadResult = await uploadResponse.Content.ReadAsStringAsync();
                dynamic uploadJson = JsonConvert.DeserializeObject(uploadResult);
                // Retornamos el primer documento del array
                return uploadJson.documents[0];
            }
            else
            {
                return null;
            }
        }

        /// <summary>
        /// Mueve el documento usando el endpoint move-files.
        /// </summary>
        private async Task<bool> MoveDocument(HttpClient client, string location, string toName)
        {
            // Suponiendo que 'custom-documents' es la carpeta base
            string workspaceFolder = "custom-documents/";

            var movePayload = new
            {
                files = new[]
                {
            new
            {
                from = location,
                to = $"{workspaceFolder}{toName}" // Construye la ruta completa
            }
        }
            };

            string moveJson = JsonConvert.SerializeObject(movePayload);
            var moveContent = new StringContent(moveJson, Encoding.UTF8, "application/json");
            HttpResponseMessage moveResponse = await client.PostAsync($"{BASE_URL}/v1/document/move-files", moveContent);

            return moveResponse.IsSuccessStatusCode;
        }

        /// <summary>
        /// Actualiza los embeddings del workspace usando el endpoint update-embeddings.
        /// Se envía el nombre del fichero en "adds" con la ruta relativa,
        /// por ejemplo "custom-documents/" + fileName.
        /// </summary>
        private async Task<bool> UpdateEmbeddings(HttpClient client, string location)
        {
            var updatePayload = new
            {
                adds = new[] { location },
                deletes = new string[0]
            };

            string updateJson = JsonConvert.SerializeObject(updatePayload);
            var updateContent = new StringContent(updateJson, Encoding.UTF8, "application/json");
            HttpResponseMessage updateResponse = await client.PostAsync(
                $"{BASE_URL}/v1/workspace/{SLUG}/update-embeddings", updateContent);
            return updateResponse.IsSuccessStatusCode;
        }

        private async void btnUpload_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = "Documentos (*.pdf;*.docx;*.txt)|*.pdf;*.docx;*.txt|Todos los archivos (*.*)|*.*"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                string filePath = openFileDialog.FileName;
                txtStatus.Text = "Subiendo documento...";

                try
                {
                    using (var client = new HttpClient())
                    {
                        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", API_KEY);

                        // 1. Subir el documento
                        dynamic document = await UploadDocument(client, filePath);
                        if (document == null)
                        {
                            txtStatus.Text = "Error al subir el documento.";
                            return;
                        }

                        // Extraer las propiedades 'location' y 'title'
                        // Ejemplo de location: "custom-documents/codigo.txt-8b2c8d11-8381-49e1-91a4-d6d8411a4067.json"
                        string location = document.location;
                        string title = document.title; // Ejemplo: "codigo.txt"

                        // Extraer el nombre del fichero (incluyendo hash y extensión) de la propiedad location.
                        string fileName = location.Substring(location.LastIndexOf('/') + 1);

                        txtStatus.Text = $"Documento subido con éxito: {title}";

                        // 2. Mover el documento al workspace.
                        // En este ejemplo se utiliza como nombre destino el mismo nombre obtenido (fileName).
                        // NO ES NECESARIO EN ESTE CASO
                        /** 
                        bool moved = await MoveDocument(client, location, fileName);
                        if (moved)
                        {
                            txtStatus.Text += " | Documento movido al workspace.";
                        }
                        else
                        {
                            txtStatus.Text += " | Error al mover el documento.";
                            return;
                        }
                        **/
                        // 3. Actualizar embeddings.
                        bool updated = await UpdateEmbeddings(client, location);
                        if (updated)
                        {
                            txtStatus.Text += " | Embeddings actualizados.";
                        }
                        else
                        {
                            txtStatus.Text += " | Error al actualizar embeddings.";
                        }
                    }
                }
                catch (Exception ex)
                {
                    txtStatus.Text = "Excepción: " + ex.Message;
                }
            }
        }

        private async void btnAsk_Click(object sender, RoutedEventArgs e)
        {
            string question = txtQuestion.Text;
            if (string.IsNullOrWhiteSpace(question))
            {
                MessageBox.Show("Por favor, ingrese una pregunta.", "Aviso", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            txtAnswer.Text = "Consultando...";
            txtChunks.Text = string.Empty;

            try
            {
                using (var client = new HttpClient())
                {
                    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", API_KEY);

                    // Determinar el modo basado en el RadioButton seleccionado
                    string selectedMode = rbChat.IsChecked == true ? "chat" : "query";

                    var payload = new
                    {
                        message = question,
                        mode = selectedMode,//query o chat
                        sessionId = Guid.NewGuid().ToString(),
                        attachments = new object[0]
                    };

                    string jsonPayload = JsonConvert.SerializeObject(payload);
                    var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

                    HttpResponseMessage response = await client.PostAsync($"{BASE_URL}/v1/workspace/{SLUG}/chat", content);
                    if (response.IsSuccessStatusCode)
                    {
                        string responseContent = await response.Content.ReadAsStringAsync();
                        dynamic result = JsonConvert.DeserializeObject(responseContent);

                        txtAnswer.Text = (string)result.textResponse;

                        StringBuilder chunksBuilder = new StringBuilder();
                        if (result.sources != null && result.sources.Count > 0)
                        {
                            chunksBuilder.AppendLine("Información de los chunks:");
                            foreach (var source in result.sources)
                            {
                                chunksBuilder.AppendLine($"Documento: {source.text}");
                                chunksBuilder.AppendLine($"Score: {source.score}");
                                chunksBuilder.AppendLine(new string('-', 50));
                            }
                        }
                        else
                        {
                            chunksBuilder.AppendLine("No se encontraron chunks.");
                        }
                        txtChunks.Text = chunksBuilder.ToString();
                    }
                    else
                    {
                        txtAnswer.Text = $"Error al obtener respuesta: {response.ReasonPhrase}";
                    }
                }
            }
            catch (Exception ex)
            {
                txtAnswer.Text = "Excepción: " + ex.Message;
            }
        }



        private async Task<string> GetAllDocuments(HttpClient client)
        {
            HttpResponseMessage response = await client.GetAsync($"{BASE_URL}/v1/documents");
            if (response.IsSuccessStatusCode)
            {
                string jsonResponse = await response.Content.ReadAsStringAsync();
                return jsonResponse;
            }
            else
            {
                return $"Error: {response.ReasonPhrase}";
            }
        }

        /// <summary>
        /// Evento del botón para obtener los documentos en la API.
        /// </summary>
        private async void btnGetDocuments_Click(object sender, RoutedEventArgs e)
        {
            txtWorkspaceDocs.Text = "Obteniendo documentos...";
            try
            {
                using (var client = new HttpClient())
                {
                    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", API_KEY);
                    string documents = await GetAllDocuments(client);
                    txtWorkspaceDocs.Text = documents;
                }
            }
            catch (Exception ex)
            {
                txtWorkspaceDocs.Text = "Excepción: " + ex.Message;
            }
        }

        /// <summary>
        /// Obtiene la información del workspace, que podría incluir los documentos.
        /// </summary>
        private async Task<string> GetWorkspaceSlugInfo(HttpClient client)
        {
            HttpResponseMessage response = await client.GetAsync($"{BASE_URL}/v1/workspace/{SLUG}");
            if (response.IsSuccessStatusCode)
            {
                string jsonResponse = await response.Content.ReadAsStringAsync();
                return jsonResponse;
            }
            else
            {
                return $"Error: {response.ReasonPhrase}";
            }
        }

        /// <summary>
        /// Evento del botón para obtener información del workspace.
        /// </summary>
        private async void btnGetDocumentsSlug_Click(object sender, RoutedEventArgs e)
        {
            txtWorkspaceDocs.Text = "Obteniendo información del workspace...";
            try
            {
                using (var client = new HttpClient())
                {
                    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", API_KEY);
                    string workspaceInfo = await GetWorkspaceSlugInfo(client);
                    txtWorkspaceDocs.Text = workspaceInfo;
                }
            }
            catch (Exception ex)
            {
                txtWorkspaceDocs.Text = "Excepción: " + ex.Message;
            }
        }

        /// <summary>
        /// Obtiene la lista de documentos globales en la API.
        /// </summary>
    }
}
