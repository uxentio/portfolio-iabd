using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using Azure;
using Azure.AI.OpenAI;
using OpenAI.Chat;

namespace AzureOpenAI
{
    public partial class MainWindow : Window
    {
        // Tus credenciales
        private const string Endpoint = "https://david-mahb9brt-eastus2.cognitiveservices.azure.com/";
        private const string ApiKey = "DoHjh51Ujk8t3QuIUqin8uIxYnajEQTqeWRfKyXcrdmYS1AjPKwzJQQJ99BEACHYHv6XJ3w3AAAAACOGHJ9w";
        private const string DeploymentId = "gpt-4o"; // Nombre exacto de tu deployment

        private readonly ChatClient _chatClient;

        public MainWindow()
        {
            InitializeComponent();

            // Crea el cliente de Azure OpenAI y obtiene el ChatClient
            var credential = new AzureKeyCredential(ApiKey);
            var openAIClient = new AzureOpenAIClient(new Uri(Endpoint), credential);
            _chatClient = openAIClient.GetChatClient(DeploymentId);
        }

        private async void BtnEnviar_Click(object sender, RoutedEventArgs e)
        {
            var prompt = txtPrompt.Text?.Trim();
            if (string.IsNullOrEmpty(prompt))
            {
                MessageBox.Show("Escribe algo antes de enviar.", "Aviso",
                                MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            try
            {
                txtResponse.Text = "Pensando…";

                // 1. Prepara los mensajes
                var messages = new List<ChatMessage>
                {
                    new SystemChatMessage("You are a helpful assistant."),
                    new UserChatMessage(prompt)
                };

                // 2. Configura las opciones de la petición
                var options = new ChatCompletionOptions
                {
                    Temperature = 0.7f,
                    MaxOutputTokenCount = 1000
                };

                // 3. Llama al endpoint de chat (versión asíncrona)
                ChatCompletion completion = await _chatClient.CompleteChatAsync(messages, options);

                // 4. Ensambla el contenido en un solo string
                string responseText = string.Concat(completion.Content.Select(p => p.Text)).Trim();

                txtResponse.Text = responseText;
            }
            catch (Exception ex)
            {
                txtResponse.Text = $"❌ Error: {ex.Message}";
            }
        }
    }
}
