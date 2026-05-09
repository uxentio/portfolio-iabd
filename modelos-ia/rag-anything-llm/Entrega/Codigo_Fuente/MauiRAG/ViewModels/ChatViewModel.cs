using System.Collections.ObjectModel;
using System.Windows.Input;
using MauiRAG.Modelos;
using MauiRAG.Servicios;
using Newtonsoft.Json;

namespace MauiRAG.ViewModels
{
    public class ChatViewModel : BaseViewModel
    {
        // para el historial del chat
        private string sessionId = Guid.NewGuid().ToString();
        private List<WorkspaceItem> workspacesData = new List<WorkspaceItem>();

        // colecciones para la vista
        public ObservableCollection<string> NombresWorkspaces { get; } = new ObservableCollection<string>();
        public ObservableCollection<MensajeChat> Mensajes { get; } = new ObservableCollection<MensajeChat>();
        public ObservableCollection<ChunkInfo> Chunks { get; } = new ObservableCollection<ChunkInfo>();

        private int _workspaceSeleccionado = -1;
        public int WorkspaceSeleccionado
        {
            get => _workspaceSeleccionado;
            set => SetProperty(ref _workspaceSeleccionado, value);
        }

        private string _pregunta;
        public string Pregunta
        {
            get => _pregunta;
            set => SetProperty(ref _pregunta, value);
        }

        private bool _modoChat = true;
        public bool ModoChat
        {
            get => _modoChat;
            set => SetProperty(ref _modoChat, value);
        }

        private bool _enviando;
        public bool Enviando
        {
            get => _enviando;
            set => SetProperty(ref _enviando, value);
        }

        public string TextoBotonEnviar => Enviando ? "Enviando..." : "Enviar";

        public ICommand EnviarCommand { get; }
        public ICommand LimpiarCommand { get; }
        public ICommand ToggleChunkCommand { get; }

        public ChatViewModel()
        {
            EnviarCommand = new Command(async () => await EnviarMensaje(), () => !Enviando);
            LimpiarCommand = new Command(LimpiarChat);
            ToggleChunkCommand = new Command<ChunkInfo>(chunk =>
            {
                if (chunk != null) chunk.Expandido = !chunk.Expandido;
            });
        }

        public async Task CargarWorkspaces()
        {
            try
            {
                string resultado = await ApiService.ObtenerWorkspaces();
                if (resultado != null)
                {
                    dynamic json = JsonConvert.DeserializeObject(resultado);
                    workspacesData.Clear();
                    NombresWorkspaces.Clear();

                    foreach (var ws in json.workspaces)
                    {
                        string nombre = (string)ws.name;
                        string slug = (string)ws.slug;
                        workspacesData.Add(new WorkspaceItem { Nombre = nombre, Slug = slug });
                        NombresWorkspaces.Add(nombre);
                    }

                    if (NombresWorkspaces.Count > 0)
                        WorkspaceSeleccionado = 0;
                }
            }
            catch (Exception)
            {
                // se gestiona en la vista
            }
        }

        public async Task EnviarMensaje()
        {
            if (string.IsNullOrWhiteSpace(Pregunta)) return;
            if (WorkspaceSeleccionado < 0) return;

            string slug = workspacesData[WorkspaceSeleccionado].Slug;
            string modo = ModoChat ? "chat" : "query";

            // en query cada pregunta es independiente
            if (modo == "query")
                sessionId = Guid.NewGuid().ToString();

            Mensajes.Add(new MensajeChat
            {
                Texto = Pregunta,
                EsUsuario = true,
                Hora = DateTime.Now.ToString("HH:mm")
            });

            string preguntaActual = Pregunta;
            Pregunta = "";
            Enviando = true;
            OnPropertyChanged(nameof(TextoBotonEnviar));

            try
            {
                dynamic resultado = await ApiService.EnviarMensaje(slug, preguntaActual, modo, sessionId);

                if (resultado != null)
                {
                    string respuesta = (string)resultado.textResponse;
                    Mensajes.Add(new MensajeChat
                    {
                        Texto = respuesta,
                        EsUsuario = false,
                        Hora = DateTime.Now.ToString("HH:mm")
                    });

                    ProcesarChunks(resultado.sources);
                }
                else
                {
                    Mensajes.Add(new MensajeChat
                    {
                        Texto = "Error: no se obtuvo respuesta del servidor",
                        EsUsuario = false,
                        Hora = DateTime.Now.ToString("HH:mm")
                    });
                }
            }
            catch (Exception ex)
            {
                Mensajes.Add(new MensajeChat
                {
                    Texto = "Error: " + ex.Message,
                    EsUsuario = false,
                    Hora = DateTime.Now.ToString("HH:mm")
                });
            }
            finally
            {
                Enviando = false;
                OnPropertyChanged(nameof(TextoBotonEnviar));
            }
        }

        // saco los chunks que devuelve el rag
        private void ProcesarChunks(dynamic sources)
        {
            Chunks.Clear();

            if (sources == null || sources.Count == 0)
            {
                Chunks.Add(new ChunkInfo
                {
                    Titulo = "Sin resultados",
                    TextoCompleto = "No se encontraron chunks relevantes",
                    Score = "N/A"
                });
                return;
            }

            foreach (var source in sources)
            {
                string titulo = (string)(source.title ?? "Documento desconocido");
                string texto = (string)(source.text ?? "");
                string score = source.score != null ? $"{source.score:F4}" : "N/A";

                Chunks.Add(new ChunkInfo
                {
                    Titulo = titulo,
                    TextoCompleto = texto,
                    Score = score
                });
            }
        }

        private void LimpiarChat()
        {
            Mensajes.Clear();
            Chunks.Clear();
            sessionId = Guid.NewGuid().ToString();
        }
    }
}
