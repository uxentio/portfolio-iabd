using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace RpaChatApp.ViewModels;

// Base mínima de MVVM con INotifyPropertyChanged.
public class BaseViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    // [CallerMemberName] inyecta el nombre: evita strings mágicos al renombrar.
    protected void OnPropertyChanged([CallerMemberName] string propertyName = "")
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }

    // Notifico solo si cambió el valor; devuelvo bool para encadenar lógica en el setter.
    protected bool SetProperty<T>(ref T field, T value, [CallerMemberName] string propertyName = "")
    {
        if (EqualityComparer<T>.Default.Equals(field, value)) return false;
        field = value;
        OnPropertyChanged(propertyName);
        return true;
    }
}

// ICommand para los botones. Sin async/cancelación.
public class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;

    public void Execute(object? parameter) => _execute();

    // Permite a la View refrescar el estado habilitado del botón cuando
    // cambia la condición de CanExecute (p. ej. al alternar IsBusy).
    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
