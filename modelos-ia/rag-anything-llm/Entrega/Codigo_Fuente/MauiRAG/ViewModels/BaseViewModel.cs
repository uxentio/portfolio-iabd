using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace MauiRAG.ViewModels
{
    // base para los viewmodels, con INotifyPropertyChanged
    public class BaseViewModel : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged([CallerMemberName] string propiedad = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propiedad));
        }

        // para setear y notificar de una
        protected bool SetProperty<T>(ref T campo, T valor, [CallerMemberName] string propiedad = null)
        {
            if (EqualityComparer<T>.Default.Equals(campo, valor)) return false;
            campo = valor;
            OnPropertyChanged(propiedad);
            return true;
        }
    }
}
