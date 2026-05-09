using FacturasOCR.Servicios;

namespace FacturasOCR.Paginas;

public partial class PaginaAjustes : ContentPage
{
    public PaginaAjustes()
    {
        InitializeComponent();
    }

    // Opciones del picker de tema
    private string[] _themeOptions = Array.Empty<string>();

    protected override void OnAppearing()
    {
        base.OnAppearing();

        // Cargar valores guardados
        entryEndpoint.Text = Preferences.Get("AzureEndpoint", ServicioAnalisis.DefaultEndpoint);
        entryApiKey.Text = Preferences.Get("AzureApiKey", ServicioAnalisis.DefaultApiKey);

        // Tema
        CargarPickerTema();

        // Almacenamiento
        string dbDir = Preferences.Get("DbDirectory", ServicioBaseDatos.DefaultDbDirectory);
        entryDbDirectory.Text = dbDir;
        ActualizarRutas(dbDir);

        // Copia de seguridad
        switchBackup.IsToggled = Preferences.Get("BackupEnabled", false);
        entryBackupFolder.Text = Preferences.Get("BackupFolder", "");

        // Idioma: rellenar picker
        CargarPickerIdioma();

        // Aplicar traducciones
        AplicarIdioma();
    }

    // Atajo para ServicioIdiomas.T()
    private static string L(string key) => ServicioIdiomas.T(key);

    // Rellena el picker de idiomas y selecciona el actual
    private void CargarPickerIdioma()
    {
        pickerLanguage.Items.Clear();
        int selectedIndex = 0;
        for (int i = 0; i < ServicioIdiomas.IdiomasDisponibles.Count; i++)
        {
            var (code, name) = ServicioIdiomas.IdiomasDisponibles[i];
            pickerLanguage.Items.Add(name);
            if (code == ServicioIdiomas.IdiomaActual)
                selectedIndex = i;
        }
        pickerLanguage.SelectedIndex = selectedIndex;
    }

    // Carga el picker de tema y selecciona el actual
    private void CargarPickerTema()
    {
        _themeOptions = new[] { L("theme_light"), L("theme_dark"), L("theme_system") };
        pickerTheme.Items.Clear();
        foreach (var opt in _themeOptions)
            pickerTheme.Items.Add(opt);

        string saved = Preferences.Get("AppTheme", "system");
        pickerTheme.SelectedIndex = saved switch
        {
            "light" => 0,
            "dark" => 1,
            _ => 2
        };
    }

    // Aplica el tema elegido
    public static void AplicarTema()
    {
        string tema = Preferences.Get("AppTheme", "system");
        if (Application.Current == null) return;

        Application.Current.UserAppTheme = tema switch
        {
            "light" => AppTheme.Light,
            "dark" => AppTheme.Dark,
            _ => AppTheme.Unspecified
        };
    }

    // Aplica las traducciones a todos los elementos de la pagina
    private void AplicarIdioma()
    {
        Title = L("settings_title");

        // Idioma
        lblLanguageTitle.Text = L("language_title");
        lblLanguageDesc.Text = L("language_desc");

        // Tema
        lblThemeTitle.Text = L("theme_title");
        lblThemeDesc.Text = L("theme_desc");
        // Refrescar opciones del picker con el idioma actual
        CargarPickerTema();

        // Azure
        lblAzureTitle.Text = L("azure_title");
        lblAzureDesc.Text = L("azure_desc");
        lblApiKeyLabel.Text = L("api_key");
        lblSavedLocally.Text = L("saved_locally");
        lblModelInfo.Text = L("model_info");
        btnSaveAzure.Text = L("btn_save_azure");
        btnTest.Text = L("btn_test");
        btnReset.Text = L("btn_reset");

        // Almacenamiento
        lblStorageTitle.Text = L("storage_label");
        lblStorageDesc.Text = L("storage_desc");
        lblDataFolder.Text = L("data_folder");
        lblDbImagesInfo.Text = L("db_images_info");
        btnPickFolder.Text = L("btn_pick_folder");
        btnSavePath.Text = L("btn_save_path");
        btnRestoreStorage.Text = L("btn_restore");
        lblCurrentDb.Text = L("current_db");
        lblCurrentFiles.Text = L("current_files");
        btnOpenFolder.Text = L("btn_open_folder");

        // Copia de seguridad
        lblBackupTitle.Text = L("backup_title");
        lblBackupDesc.Text = L("backup_desc");
        lblBackupEnabled.Text = L("backup_enabled");
        lblBackupFolder.Text = L("backup_folder");
        btnPickBackup.Text = L("btn_pick_folder");
        btnSaveBackup.Text = L("btn_save_backup");
    }

    // Actualiza los labels de rutas segun la carpeta elegida
    private void ActualizarRutas(string directory)
    {
        lblDbPath.Text = Path.Combine(directory, "invoices.db");
        lblFilesPath.Text = Path.Combine(directory, "images");
    }

    // Cuando el usuario cambia el idioma en el picker
    private void OnLanguageChanged(object? sender, EventArgs e)
    {
        if (pickerLanguage.SelectedIndex < 0) return;
        string code = ServicioIdiomas.IdiomasDisponibles[pickerLanguage.SelectedIndex].Code;
        ServicioIdiomas.CambiarIdioma(code);
        AplicarIdioma();
    }

    // Cuando el usuario cambia el tema
    private void OnThemeChanged(object? sender, EventArgs e)
    {
        if (pickerTheme.SelectedIndex < 0) return;
        string tema = pickerTheme.SelectedIndex switch
        {
            0 => "light",
            1 => "dark",
            _ => "system"
        };
        Preferences.Set("AppTheme", tema);
        AplicarTema();
    }

    // Guardar credenciales de Azure
    private async void OnSaveClicked(object? sender, EventArgs e)
    {
        string endpoint = entryEndpoint.Text?.Trim() ?? "";
        string apiKey = entryApiKey.Text?.Trim() ?? "";

        if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(apiKey))
        {
            await DisplayAlert(L("error"), L("fill_endpoint_key"), L("ok"));
            return;
        }

        Preferences.Set("AzureEndpoint", endpoint);
        Preferences.Set("AzureApiKey", apiKey);
        await DisplayAlert(L("saved"), L("azure_saved"), L("ok"));
    }

    private async void OnTestClicked(object? sender, EventArgs e)
    {
        string endpoint = entryEndpoint.Text?.Trim() ?? "";
        string apiKey = entryApiKey.Text?.Trim() ?? "";

        if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(apiKey))
        {
            lblTestResult.Text = L("fill_first");
            lblTestResult.TextColor = Colors.Red;
            return;
        }

        lblTestResult.Text = L("testing_azure");
        lblTestResult.TextColor = Colors.Gray;

        try
        {
            var client = new Azure.AI.FormRecognizer.DocumentAnalysis.DocumentAnalysisClient(
                new Uri(endpoint),
                new Azure.AzureKeyCredential(apiKey));

            // Mandamos un byte para probar que el servidor responde
            using var testStream = new MemoryStream(new byte[] { 0 });
            try
            {
                await client.AnalyzeDocumentAsync(Azure.WaitUntil.Completed, "prebuilt-invoice", testStream);
            }
            catch (Azure.RequestFailedException ex) when (ex.Status == 400)
            {
                // 400 = servidor respondio, la conexion funciona
                lblTestResult.Text = L("connection_ok");
                lblTestResult.TextColor = Colors.Green;
                return;
            }

            lblTestResult.Text = L("connection_ok");
            lblTestResult.TextColor = Colors.Green;
        }
        catch (Exception ex)
        {
            lblTestResult.Text = $"{L("error")}: {ex.Message}";
            lblTestResult.TextColor = Colors.Red;
        }
    }

    private async void OnResetClicked(object? sender, EventArgs e)
    {
        bool confirm = await DisplayAlert(L("restore_title"), L("restore_confirm"), L("yes"), L("cancel"));
        if (!confirm) return;

        entryEndpoint.Text = ServicioAnalisis.DefaultEndpoint;
        entryApiKey.Text = ServicioAnalisis.DefaultApiKey;
        Preferences.Set("AzureEndpoint", ServicioAnalisis.DefaultEndpoint);
        Preferences.Set("AzureApiKey", ServicioAnalisis.DefaultApiKey);

        lblTestResult.Text = L("values_restored");
        lblTestResult.TextColor = Colors.Gray;
    }

    // Elegir carpeta de almacenamiento
    private async void OnPickFolderClicked(object? sender, EventArgs e)
    {
        try
        {
            // En MAUI no hay FolderPicker nativo, usamos FilePicker y cogemos la carpeta
            var file = await FilePicker.PickAsync();
            if (file != null)
            {
                string dir = Path.GetDirectoryName(file.FullPath) ?? "";
                entryDbDirectory.Text = dir;
                ActualizarRutas(dir);
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert(L("error"), $"{L("pick_folder_error")}: {ex.Message}", L("ok"));
        }
    }

    private async void OnSaveStorageClicked(object? sender, EventArgs e)
    {
        string dir = entryDbDirectory.Text?.Trim() ?? "";
        if (string.IsNullOrEmpty(dir))
        {
            await DisplayAlert(L("error"), L("path_empty"), L("ok"));
            return;
        }

        try
        {
            Directory.CreateDirectory(dir);
        }
        catch (Exception ex)
        {
            await DisplayAlert(L("error"), $"{L("folder_error")}:\n{ex.Message}", L("ok"));
            return;
        }

        Preferences.Set("DbDirectory", dir);
        ActualizarRutas(dir);
        await DisplayAlert(L("saved"), $"{L("folder_saved")}:\n{dir}\n\n{L("folder_saved_msg")}", L("ok"));
    }

    private async void OnResetStorageClicked(object? sender, EventArgs e)
    {
        bool confirm = await DisplayAlert(L("restore_title"), L("restore_folder_confirm"), L("yes"), L("cancel"));
        if (!confirm) return;

        string defaultDir = ServicioBaseDatos.DefaultDbDirectory;
        entryDbDirectory.Text = defaultDir;
        Preferences.Set("DbDirectory", defaultDir);
        ActualizarRutas(defaultDir);
    }

    private async void OnOpenFolderClicked(object? sender, EventArgs e)
    {
        try
        {
            string folder = Preferences.Get("DbDirectory", ServicioBaseDatos.DefaultDbDirectory);
            await Launcher.OpenAsync(new Uri($"file:///{folder.Replace('\\', '/')}"));
        }
        catch (Exception)
        {
            string folder = Preferences.Get("DbDirectory", ServicioBaseDatos.DefaultDbDirectory);
            await DisplayAlert(L("info"),
                $"{L("open_folder_error")}\n{L("path_label")}: {folder}",
                L("ok"));
        }
    }

    // Elegir carpeta de backup
    private async void OnPickBackupFolderClicked(object? sender, EventArgs e)
    {
        try
        {
            var file = await FilePicker.PickAsync();
            if (file != null)
            {
                string dir = Path.GetDirectoryName(file.FullPath) ?? "";
                entryBackupFolder.Text = dir;
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert(L("error"), $"{L("pick_folder_error")}: {ex.Message}", L("ok"));
        }
    }

    private async void OnSaveBackupClicked(object? sender, EventArgs e)
    {
        bool enabled = switchBackup.IsToggled;
        string folder = entryBackupFolder.Text?.Trim() ?? "";

        Preferences.Set("BackupEnabled", enabled);
        Preferences.Set("BackupFolder", folder);

        if (enabled && !string.IsNullOrEmpty(folder))
        {
            try { Directory.CreateDirectory(folder); }
            catch (Exception ex)
            {
                await DisplayAlert(L("error"), $"{L("folder_error")}:\n{ex.Message}", L("ok"));
                return;
            }
        }

        await DisplayAlert(L("saved"), L("backup_saved"), L("ok"));
    }
}
