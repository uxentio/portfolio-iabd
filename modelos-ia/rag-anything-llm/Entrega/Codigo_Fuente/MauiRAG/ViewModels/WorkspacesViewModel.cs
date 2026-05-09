using System.Collections.ObjectModel;
using System.Windows.Input;
using MauiRAG.Modelos;
using MauiRAG.Servicios;
using Newtonsoft.Json;

namespace MauiRAG.ViewModels
{
    public class WorkspacesViewModel : BaseViewModel
    {
        public ObservableCollection<WorkspaceItem> Workspaces { get; } = new ObservableCollection<WorkspaceItem>();

        private string _nuevoNombre;
        public string NuevoNombre
        {
            get => _nuevoNombre;
            set => SetProperty(ref _nuevoNombre, value);
        }

        public ICommand CrearCommand { get; }
        public ICommand RefrescarCommand { get; }

        public WorkspacesViewModel()
        {
            CrearCommand = new Command(async () => await CrearWorkspace());
            RefrescarCommand = new Command(async () => await CargarWorkspaces());
        }

        public async Task CargarWorkspaces()
        {
            try
            {
                string resultado = await ApiService.ObtenerWorkspaces();
                if (resultado != null)
                {
                    dynamic json = JsonConvert.DeserializeObject(resultado);
                    Workspaces.Clear();

                    foreach (var ws in json.workspaces)
                    {
                        Workspaces.Add(new WorkspaceItem
                        {
                            Nombre = (string)ws.name,
                            Slug = (string)ws.slug
                        });
                    }
                }
            }
            catch (Exception)
            {
            }
        }

        public async Task<bool> CrearWorkspace()
        {
            if (string.IsNullOrWhiteSpace(NuevoNombre)) return false;

            try
            {
                string resultado = await ApiService.CrearWorkspace(NuevoNombre);
                if (resultado != null)
                {
                    NuevoNombre = "";
                    await CargarWorkspaces();
                    return true;
                }
            }
            catch (Exception) { }
            return false;
        }

        // el rename y delete necesitan confirmacion asi que se llaman desde la vista
        public async Task<bool> RenombrarWorkspace(string slug, string nuevoNombre)
        {
            try
            {
                bool ok = await ApiService.RenombrarWorkspace(slug, nuevoNombre);
                if (ok) await CargarWorkspaces();
                return ok;
            }
            catch (Exception) { return false; }
        }

        public async Task<bool> EliminarWorkspace(string slug)
        {
            try
            {
                bool ok = await ApiService.EliminarWorkspace(slug);
                if (ok) await CargarWorkspaces();
                return ok;
            }
            catch (Exception) { return false; }
        }
    }
}
