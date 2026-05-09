using System.Collections.ObjectModel;
using System.Windows.Input;
using MauiRAG.Modelos;
using MauiRAG.Servicios;
using Newtonsoft.Json;

namespace MauiRAG.ViewModels
{
    public class DocumentosViewModel : BaseViewModel
    {
        private List<WorkspaceItem> workspacesData = new List<WorkspaceItem>();

        public ObservableCollection<string> NombresWorkspaces { get; } = new ObservableCollection<string>();
        public ObservableCollection<DocumentoItem> Documentos { get; } = new ObservableCollection<DocumentoItem>();
        public List<DocumentoItem> DocumentosSeleccionados { get; } = new List<DocumentoItem>();

        private int _workspaceSeleccionado = -1;
        public int WorkspaceSeleccionado
        {
            get => _workspaceSeleccionado;
            set => SetProperty(ref _workspaceSeleccionado, value);
        }

        private string _archivoSeleccionado;
        public string ArchivoSeleccionado
        {
            get => _archivoSeleccionado;
            set
            {
                SetProperty(ref _archivoSeleccionado, value);
                OnPropertyChanged(nameof(NombreArchivo));
                OnPropertyChanged(nameof(TipoArchivoTexto));
                OnPropertyChanged(nameof(ColorTipoArchivo));
                OnPropertyChanged(nameof(EsPdfSeleccionado));
                // activar el checkbox por defecto al seleccionar un PDF
                if (PythonProcessorService.EsPdf(value ?? ""))
                    ProcesarPdfConMarcas = true;
            }
        }

        public string NombreArchivo => string.IsNullOrEmpty(ArchivoSeleccionado)
            ? "Ningun archivo seleccionado"
            : Path.GetFileName(ArchivoSeleccionado);

        public string TipoArchivoTexto
        {
            get
            {
                if (string.IsNullOrEmpty(ArchivoSeleccionado)) return "";
                if (ImageProcessorService.EsImagen(ArchivoSeleccionado))
                    return "Imagen detectada: se extraera descripcion IA + OCR + metadatos EXIF";
                if (PythonProcessorService.EsPdf(ArchivoSeleccionado))
                    return "PDF detectado";
                return "Documento de texto";
            }
        }

        public Color ColorTipoArchivo
        {
            get
            {
                if (string.IsNullOrEmpty(ArchivoSeleccionado)) return Colors.Gray;
                if (ImageProcessorService.EsImagen(ArchivoSeleccionado)) return Colors.Blue;
                if (PythonProcessorService.EsPdf(ArchivoSeleccionado)) return Colors.Purple;
                return Colors.Gray;
            }
        }

        // indica si el archivo seleccionado es un PDF (para mostrar el checkbox)
        public bool EsPdfSeleccionado => !string.IsNullOrEmpty(ArchivoSeleccionado)
            && PythonProcessorService.EsPdf(ArchivoSeleccionado);

        // checkbox para procesar PDF con marcas de pagina
        private bool _procesarPdfConMarcas;
        public bool ProcesarPdfConMarcas
        {
            get => _procesarPdfConMarcas;
            set => SetProperty(ref _procesarPdfConMarcas, value);
        }

        // campo de URL de YouTube
        private string _urlYouTube;
        public string UrlYouTube
        {
            get => _urlYouTube;
            set
            {
                SetProperty(ref _urlYouTube, value);
                OnPropertyChanged(nameof(EsUrlYouTubeValida));
            }
        }

        public bool EsUrlYouTubeValida => PythonProcessorService.EsUrlYouTube(UrlYouTube);

        private string _estadoSubida;
        public string EstadoSubida
        {
            get => _estadoSubida;
            set => SetProperty(ref _estadoSubida, value);
        }

        private Color _colorEstado = Colors.Gray;
        public Color ColorEstado
        {
            get => _colorEstado;
            set => SetProperty(ref _colorEstado, value);
        }

        private bool _subiendo;
        public bool Subiendo
        {
            get => _subiendo;
            set => SetProperty(ref _subiendo, value);
        }

        // para el boton de eliminar varios
        private bool _mostrarEliminarSeleccion;
        public bool MostrarEliminarSeleccion
        {
            get => _mostrarEliminarSeleccion;
            set => SetProperty(ref _mostrarEliminarSeleccion, value);
        }

        private string _textoEliminarSeleccion;
        public string TextoEliminarSeleccion
        {
            get => _textoEliminarSeleccion;
            set => SetProperty(ref _textoEliminarSeleccion, value);
        }

        public ICommand RefrescarCommand { get; }

        public DocumentosViewModel()
        {
            RefrescarCommand = new Command(async () => await CargarDocumentos());
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
            catch (Exception) { }
        }

        public async Task CargarDocumentos()
        {
            try
            {
                string resultado = await ApiService.ObtenerDocumentos();
                if (resultado != null)
                {
                    dynamic json = JsonConvert.DeserializeObject(resultado);
                    Documentos.Clear();
                    DocumentosSeleccionados.Clear();
                    MostrarEliminarSeleccion = false;

                    if (json.localFiles != null && json.localFiles.items != null)
                    {
                        foreach (var item in json.localFiles.items)
                        {
                            string carpeta = (string)(item.name ?? "");

                            if (item.items != null)
                            {
                                foreach (var doc in item.items)
                                {
                                    string nombre = (string)(doc.name ?? doc.title ?? "sin nombre");
                                    Documentos.Add(new DocumentoItem
                                    {
                                        Nombre = nombre,
                                        RutaCompleta = carpeta + "/" + nombre
                                    });
                                }
                            }
                            else
                            {
                                Documentos.Add(new DocumentoItem
                                {
                                    Nombre = (string)(item.name ?? item.title ?? "sin nombre"),
                                    RutaCompleta = carpeta
                                });
                            }
                        }
                    }
                }
            }
            catch (Exception) { }
        }

        // sube doc o imagen procesada al workspace
        public async Task<bool> SubirDocumento()
        {
            if (string.IsNullOrEmpty(ArchivoSeleccionado)) return false;
            if (WorkspaceSeleccionado < 0) return false;

            string slugSeleccionado = workspacesData[WorkspaceSeleccionado].Slug;
            Subiendo = true;

            try
            {
                string archivoParaSubir = ArchivoSeleccionado;

                // si es imagen primero la proceso (vision + OCR + EXIF)
                if (ImageProcessorService.EsImagen(ArchivoSeleccionado))
                {
                    EstadoSubida = "Procesando imagen (Vision IA + OCR + EXIF)...";
                    ColorEstado = Colors.Orange;

                    string textoAnalisis = await ImageProcessorService.ProcesarImagen(ArchivoSeleccionado);
                    archivoParaSubir = ImageProcessorService.GuardarComoTexto(textoAnalisis, ArchivoSeleccionado);

                    EstadoSubida = "Imagen procesada. Subiendo analisis...";
                }
                // si es PDF y el checkbox esta marcado, procesar con marcas de pagina
                else if (PythonProcessorService.EsPdf(ArchivoSeleccionado) && ProcesarPdfConMarcas)
                {
                    EstadoSubida = "Procesando PDF con marcas [Pagina XX]...";
                    ColorEstado = Colors.Orange;

                    archivoParaSubir = await PythonProcessorService.ProcesarPdf(ArchivoSeleccionado);

                    EstadoSubida = "PDF procesado. Subiendo texto con marcas de pagina...";
                }
                else
                {
                    EstadoSubida = "Subiendo documento...";
                    ColorEstado = Colors.Orange;
                }

                // subo y luego actualizo embeddings
                dynamic documento = await ApiService.SubirDocumento(archivoParaSubir);
                if (documento == null)
                {
                    EstadoSubida = "Error al subir el documento";
                    ColorEstado = Colors.Red;
                    return false;
                }

                string location = (string)documento.location;
                string title = (string)documento.title;
                EstadoSubida = $"Documento '{title}' subido. Actualizando embeddings...";

                bool ok = await ApiService.ActualizarEmbeddings(slugSeleccionado, location);
                if (ok)
                {
                    string tipoMsg = "Documento";
                    if (ImageProcessorService.EsImagen(ArchivoSeleccionado))
                        tipoMsg = "Imagen procesada (Vision IA + OCR + EXIF)";
                    else if (PythonProcessorService.EsPdf(ArchivoSeleccionado) && ProcesarPdfConMarcas)
                        tipoMsg = "PDF procesado con marcas [Pagina XX]";
                    EstadoSubida = $"{tipoMsg} '{Path.GetFileName(ArchivoSeleccionado)}' subido y embeddings actualizados!";
                    ColorEstado = Colors.Green;
                    ArchivoSeleccionado = null;
                    await CargarDocumentos();
                    return true;
                }
                else
                {
                    EstadoSubida = "Documento subido pero error al actualizar embeddings";
                    ColorEstado = Colors.Red;
                    return false;
                }
            }
            catch (Exception ex)
            {
                EstadoSubida = "Error: " + ex.Message;
                ColorEstado = Colors.Red;
                return false;
            }
            finally
            {
                Subiendo = false;
            }
        }

        public async Task<bool> EliminarDocumento(DocumentoItem doc)
        {
            try
            {
                bool ok = await ApiService.EliminarDocumentos(new List<string> { doc.RutaCompleta });
                if (ok) await CargarDocumentos();
                return ok;
            }
            catch (Exception) { return false; }
        }

        public async Task<bool> EliminarSeleccionados()
        {
            if (DocumentosSeleccionados.Count == 0) return false;

            try
            {
                var nombres = DocumentosSeleccionados.Select(d => d.RutaCompleta).ToList();
                bool ok = await ApiService.EliminarDocumentos(nombres);
                if (ok)
                {
                    DocumentosSeleccionados.Clear();
                    await CargarDocumentos();
                }
                return ok;
            }
            catch (Exception) { return false; }
        }

        // procesa una URL de YouTube: descarga subtitulos y sube el txt
        public async Task<bool> ProcesarYSubirYouTube()
        {
            if (string.IsNullOrWhiteSpace(UrlYouTube)) return false;
            if (WorkspaceSeleccionado < 0) return false;

            string slugSeleccionado = workspacesData[WorkspaceSeleccionado].Slug;
            Subiendo = true;

            try
            {
                EstadoSubida = "Descargando subtitulos de YouTube...";
                ColorEstado = Colors.Orange;

                string archivoTranscripcion = await PythonProcessorService.ProcesarYouTube(UrlYouTube);

                EstadoSubida = "Transcripcion lista. Subiendo al workspace...";

                dynamic documento = await ApiService.SubirDocumento(archivoTranscripcion);
                if (documento == null)
                {
                    EstadoSubida = "Error al subir la transcripcion";
                    ColorEstado = Colors.Red;
                    return false;
                }

                string location = (string)documento.location;
                string title = (string)documento.title;
                EstadoSubida = $"Transcripcion '{title}' subida. Actualizando embeddings...";

                bool ok = await ApiService.ActualizarEmbeddings(slugSeleccionado, location);
                if (ok)
                {
                    EstadoSubida = $"Video de YouTube procesado! '{title}' subido y embeddings actualizados!";
                    ColorEstado = Colors.Green;
                    UrlYouTube = "";
                    await CargarDocumentos();
                    return true;
                }
                else
                {
                    EstadoSubida = "Transcripcion subida pero error al actualizar embeddings";
                    ColorEstado = Colors.Red;
                    return false;
                }
            }
            catch (Exception ex)
            {
                EstadoSubida = "Error: " + ex.Message;
                ColorEstado = Colors.Red;
                return false;
            }
            finally
            {
                Subiendo = false;
            }
        }

        // toggle del checkbox
        public void ToggleSeleccionDocumento(DocumentoItem doc, bool seleccionado)
        {
            if (seleccionado && !DocumentosSeleccionados.Contains(doc))
                DocumentosSeleccionados.Add(doc);
            else if (!seleccionado)
                DocumentosSeleccionados.Remove(doc);

            MostrarEliminarSeleccion = DocumentosSeleccionados.Count > 0;
            TextoEliminarSeleccion = $"Eliminar seleccionados ({DocumentosSeleccionados.Count})";
        }
    }
}
