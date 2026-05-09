using System.Text;
using System.Xml.Linq;
using Azure.AI.FormRecognizer.DocumentAnalysis;
using FacturasOCR.Modelos;
using FacturasOCR.Servicios;

namespace FacturasOCR;

public partial class PaginaPrincipal : ContentPage
{
    // Servicios para el OCR y la base de datos
    private ServicioAnalisis _analysisService;
    private ServicioBaseDatos _databaseService;

    public PaginaPrincipal()
    {
        InitializeComponent();
        _analysisService = new ServicioAnalisis();
        _databaseService = new ServicioBaseDatos();
        AplicarIdioma();

        // Actualizar textos en tiempo real al cambiar idioma
        ServicioIdiomas.IdiomaChanged += () =>
            MainThread.BeginInvokeOnMainThread(AplicarIdioma);
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
        AplicarIdioma();
    }

    // Poner todos los textos en el idioma seleccionado
    private void AplicarIdioma()
    {
        Title = L("main_title");
        lblInstruction.Text = L("main_instruction");
        btnTakePhoto.Text = $"\U0001F4F7 {L("btn_photo")}";
        btnPickPhoto.Text = $"\U0001F4C1 {L("btn_file")}";
        btnBatch.Text = $"\U0001F4CB {L("btn_batch")}";
        lblSummaryTitle.Text = L("summary_title");
        lblProviderLabel.Text = L("provider");
        lblInvoiceNumLabel.Text = L("invoice_num");
        lblDateLabel.Text = L("date");
        lblTotalLabel.Text = L("total");
        lblOcrDataLabel.Text = L("ocr_data");
        editorResults.Placeholder = L("placeholder_ocr");
        lblZoomHint.Text = L("zoom_hint");
        lblStatus.Text = L("status_ready");
        string baseDir = Preferences.Get("DbDirectory", ServicioBaseDatos.DefaultDbDirectory);
        lblStoragePath.Text = $"{L("storage_label")}: {Path.Combine(baseDir, "images")}";
    }

    // Atajo para traducir
    private static string L(string key) => ServicioIdiomas.T(key);

    // Zoom de imagen: al tocar se abre grande
    private void OnImageTapped(object? sender, EventArgs e)
    {
        if (imgPreview.Source == null) return;
        imgZoom.Source = imgPreview.Source;
        overlayZoom.IsVisible = true;
    }

    private void OnCloseZoom(object? sender, EventArgs e)
    {
        overlayZoom.IsVisible = false;
    }

    // Boton "Tomar Foto"
    private async void OnTakePhotoClicked(object? sender, EventArgs e)
    {
        try
        {
            var photo = await MediaPicker.CapturePhotoAsync();
            if (photo != null)
                await ProcesarArchivo(photo);
        }
        catch (FeatureNotSupportedException)
        {
            await DisplayAlert(L("error"), L("camera_unavailable"), L("ok"));
        }
        catch (PermissionException)
        {
            await DisplayAlert(L("error"), L("camera_permission"), L("ok"));
        }
        catch (Exception ex)
        {
            await DisplayAlert(L("error"), $"{L("error_capture")}: {ex.Message}", L("ok"));
        }
    }

    // Tipos de archivo aceptados
    private static FilePickerFileType InvoiceFileTypes = new(new Dictionary<DevicePlatform, IEnumerable<string>>
    {
        { DevicePlatform.WinUI, new[] { ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf", ".xml", ".xsig" } },
        { DevicePlatform.Android, new[] { "image/*", "application/pdf", "text/xml", "application/xml" } },
        { DevicePlatform.iOS, new[] { "public.image", "com.adobe.pdf", "public.xml" } },
    });

    // Boton "Elegir Archivo"
    private async void OnPickPhotoClicked(object? sender, EventArgs e)
    {
        try
        {
            var file = await FilePicker.PickAsync(new PickOptions
            {
                PickerTitle = L("picker_title"),
                FileTypes = InvoiceFileTypes
            });
            if (file != null)
                await ProcesarArchivo(file);
        }
        catch (Exception ex)
        {
            await DisplayAlert(L("error"), $"{L("error_select")}: {ex.Message}", L("ok"));
        }
    }

    // Boton "Procesar Lote" (varias facturas a la vez)
    private async void OnBatchClicked(object? sender, EventArgs e)
    {
        try
        {
            var results = await FilePicker.PickMultipleAsync(new PickOptions
            {
                PickerTitle = L("picker_batch"),
                FileTypes = InvoiceFileTypes
            });

            if (results == null || !results.Any())
                return;

            var fileList = results.ToList();
            int total = fileList.Count;
            int processed = 0;
            int errors = 0;

            MostrarCargando(true);
            editorResults.Text = "";

            var sb = new StringBuilder();
            sb.AppendLine($"=== {L("batch_header")}: {total} ===\n");

            foreach (var file in fileList)
            {
                processed++;
                lblStatus.Text = $"{L("processing")} {processed}/{total}: {file.FileName}...";

                try
                {
                    // 1) Guardar copia local del archivo
                    string savedPath = await GuardarArchivoLocal(file);
                    ResultadoFactura invoice;

                    if (EsArchivoXml(file.FileName))
                    {
                        // XML: parseo directo, no necesita OCR
                        string xmlContent;
                        using (var stream = await file.OpenReadAsync())
                        using (var reader = new StreamReader(stream))
                            xmlContent = await reader.ReadToEndAsync();

                        // Quitar namespaces para buscar mas facil
                        string localXml = System.Text.RegularExpressions.Regex.Replace(xmlContent, @"xmlns\s*=\s*""[^""]*""", "");
                        var xdoc = XDocument.Parse(localXml);
                        var xroot = xdoc.Root!;

                        invoice = new ResultadoFactura
                        {
                            AnalyzedAt = DateTime.Now,
                            ImagePath = savedPath,
                            RawText = $"[XML] {file.FileName}",
                            FileName = file.FileName,
                            VendorName = BuscarValorXml(xroot, "SellerParty", "CorporateName", "Name", "Emisor") ?? "",
                            InvoiceId = BuscarValorXml(xroot, "InvoiceNumber", "NumeroFactura") ?? "",
                            InvoiceDate = BuscarValorXml(xroot, "IssueDate", "FechaExpedicion") ?? "",
                            Total = BuscarValorXml(xroot, "TotalAmount", "TotalExecutableAmount", "ImporteTotal") ?? ""
                        };
                    }
                    else
                    {
                        // Imagen o PDF: mandar a Azure OCR
                        AnalyzeResult result;
                        using (var stream = await file.OpenReadAsync())
                            result = await _analysisService.AnalyzeDocumentAsync(stream);

                        string formatted = FormatearResultado(result);
                        invoice = new ResultadoFactura
                        {
                            AnalyzedAt = DateTime.Now,
                            ImagePath = savedPath,
                            RawText = formatted,
                            FileName = file.FileName,
                            VendorName = ExtraerCampo(result, "VendorName") ?? ExtraerProveedor(result),
                            InvoiceId = ExtraerCampo(result, "InvoiceId") ?? ExtraerKeyValue(result, 20, "invoice no", "factura", "invoice"),
                            InvoiceDate = ExtraerCampo(result, "InvoiceDate") ?? ExtraerKeyValue(result, 30, "date of invoice", "date of issue", "fecha emisi", "fecha factura", "fecha", "date", "issue date", "invoice date"),
                            Total = ExtraerCampo(result, "InvoiceTotal") ?? ExtraerKeyValue(result, 25, "total", "importe total", "amount due", "total due", "balance due", "grand total")
                        };
                    }

                    // 2) Comprobar si ya existe esta factura
                    var duplicate = await _databaseService.FindDuplicateAsync(file.FileName, invoice.RawText);
                    if (duplicate != null)
                    {
                        sb.AppendLine($"--- {file.FileName} ({L("duplicate_omitted")}) ---");
                        sb.AppendLine($"  {L("already_exists")}: '{duplicate.FileName}' ({duplicate.AnalyzedAt:dd/MM/yyyy HH:mm})\n");
                    }
                    else
                    {
                        await _databaseService.SaveInvoiceAsync(invoice);
                        await CopiarABackup(invoice);
                        sb.AppendLine($"--- {file.FileName} (OK) ---");
                        sb.AppendLine(invoice.RawText);
                    }
                }
                catch (Exception ex)
                {
                    errors++;
                    sb.AppendLine($"--- {file.FileName} (ERROR) ---");
                    sb.AppendLine($"  {ex.Message}\n");
                }
            }

            sb.AppendLine($"\n=== {L("batch_completed")}: {processed - errors}/{total} {L("successful")}, {errors} {L("errors")} ===");
            editorResults.Text = sb.ToString();
            lblStatus.Text = $"{L("batch_completed")}: {processed - errors}/{total} OK";
            MostrarCargando(false);
        }
        catch (Exception ex)
        {
            MostrarCargando(false);
            await DisplayAlert(L("error"), $"{L("error_batch")}: {ex.Message}", L("ok"));
        }
    }

    // Comprueba si es XML
    private static bool EsArchivoXml(string fileName)
    {
        string ext = Path.GetExtension(fileName).ToLowerInvariant();
        return ext is ".xml" or ".xsig";
    }

    private static bool EsImagen(string fileName)
    {
        string ext = Path.GetExtension(fileName).ToLowerInvariant();
        return ext is ".jpg" or ".jpeg" or ".png" or ".bmp" or ".tiff" or ".tif";
    }

    // Segun el tipo de archivo lo mandamos a OCR o a parseo XML
    private async Task ProcesarArchivo(FileResult file)
    {
        if (EsArchivoXml(file.FileName))
            await ProcesarXML(file);
        else
            await ProcesarConOCR(file);
    }

    // Manda la imagen/PDF a Azure Document Intelligence y muestra el resultado
    private async Task ProcesarConOCR(FileResult photo)
    {
        MostrarCargando(true);
        LimpiarFicha();
        lblStatus.Text = L("analyzing_azure");
        editorResults.Text = "";

        // Mostrar preview si es imagen (PDF no tiene preview)
        if (EsImagen(photo.FileName))
            imgPreview.Source = ImageSource.FromFile(photo.FullPath);
        else
            imgPreview.Source = null;

        try
        {
            // 1) Guardar copia local
            string savedPath = await GuardarArchivoLocal(photo);

            // 2) Enviar a Azure y esperar resultado
            AnalyzeResult result;
            using (var stream = await photo.OpenReadAsync())
            {
                result = await _analysisService.AnalyzeDocumentAsync(stream);
            }

            // 3) Formatear y mostrar el resultado
            string formatted = FormatearResultado(result);
            editorResults.Text = formatted;

            // 4) Extraer campos clave
            //    Con prebuilt-invoice Azure devuelve VendorName, InvoiceId, InvoiceDate, InvoiceTotal directamente
            //    Si no los detecta (prebuilt-document, o factura rara), usamos busqueda manual como fallback
            var invoice = new ResultadoFactura
            {
                AnalyzedAt = DateTime.Now,
                ImagePath = savedPath,
                RawText = formatted,
                FileName = photo.FileName,
                VendorName = ExtraerCampo(result, "VendorName") ?? ExtraerProveedor(result),
                InvoiceId = ExtraerCampo(result, "InvoiceId") ?? ExtraerKeyValue(result, 20, "invoice no", "factura", "invoice"),
                InvoiceDate = ExtraerCampo(result, "InvoiceDate") ?? ExtraerKeyValue(result, 30, "date of invoice", "date of issue", "fecha emisi", "fecha factura", "fecha", "date", "issue date", "invoice date"),
                Total = ExtraerCampo(result, "InvoiceTotal") ?? ExtraerKeyValue(result, 25, "total", "importe total", "amount due", "total due", "balance due", "grand total")
            };

            // 5) Rellenar ficha visual
            RellenarFicha(invoice.VendorName, invoice.InvoiceId, invoice.InvoiceDate, invoice.Total);

            await GuardarAutomatico(invoice);
        }
        catch (Exception ex)
        {
            editorResults.Text = $"{L("error_analyze")}:\n{ex.Message}";
            lblStatus.Text = L("error_analysis");
        }
        finally
        {
            MostrarCargando(false);
        }
    }

    // Procesa XML (FacturaE) - no necesita OCR, leemos los campos directamente
    private async Task ProcesarXML(FileResult file)
    {
        MostrarCargando(true);
        LimpiarFicha();
        lblStatus.Text = L("processing_xml");
        editorResults.Text = "";
        imgPreview.Source = null;

        try
        {
            string savedPath = await GuardarArchivoLocal(file);

            // 1) Leer el contenido XML del archivo
            string xmlContent;
            using (var stream = await file.OpenReadAsync())
            using (var reader = new StreamReader(stream))
            {
                xmlContent = await reader.ReadToEndAsync();
            }

            // 2) Parsear XML (quitamos namespaces para simplificar)
            string localXml = System.Text.RegularExpressions.Regex.Replace(xmlContent, @"xmlns\s*=\s*""[^""]*""", "");
            var cleanDoc = XDocument.Parse(localXml);
            var cleanRoot = cleanDoc.Root!;

            // 3) Buscar campos tipicos de FacturaE y formatos similares
            string vendor = BuscarValorXml(cleanRoot, "SellerParty", "CorporateName", "Name", "TradeName",
                                          "CompanyName", "SellerName", "Emisor", "NombreRazon") ?? "";
            string invoiceId = BuscarValorXml(cleanRoot, "InvoiceNumber", "InvoiceSeriesCode",
                                             "NumeroFactura", "InvoiceId", "Number") ?? "";
            string invoiceDate = BuscarValorXml(cleanRoot, "IssueDate", "InvoiceDate",
                                               "FechaExpedicion", "IssuingDate") ?? "";
            string total = BuscarValorXml(cleanRoot, "TotalAmount", "TotalExecutableAmount",
                                         "InvoiceTotal", "GrossAmount", "ImporteTotal") ?? "";

            // 4) Mostrar resultados
            var sb = new StringBuilder();
            sb.AppendLine($"=== {L("fmt_xml_title")} ===");
            sb.AppendLine($"  {L("provider_label")}: {vendor}");
            sb.AppendLine($"  {L("invoice_num_label")}: {invoiceId}");
            sb.AppendLine($"  {L("date_label")}: {invoiceDate}");
            sb.AppendLine($"  {L("total_label")}: {total}");
            sb.AppendLine();
            sb.AppendLine($"=== {L("fmt_xml_summary")} ===");
            // Mostrar los primeros elementos hoja del XML como resumen
            foreach (var elem in cleanRoot.Descendants().Where(e => !e.HasElements).Take(50))
            {
                sb.AppendLine($"  {elem.Name.LocalName}: {elem.Value.Trim()}");
            }

            editorResults.Text = sb.ToString();

            var invoice = new ResultadoFactura
            {
                AnalyzedAt = DateTime.Now,
                ImagePath = savedPath,
                RawText = sb.ToString(),
                FileName = file.FileName,
                VendorName = vendor,
                InvoiceId = invoiceId,
                InvoiceDate = invoiceDate,
                Total = total
            };

            // 5) Rellenar ficha visual
            RellenarFicha(vendor, invoiceId, invoiceDate, total);

            await GuardarAutomatico(invoice);
        }
        catch (Exception ex)
        {
            editorResults.Text = $"{L("error_xml")}:\n{ex.Message}";
            lblStatus.Text = L("error_xml");
        }
        finally
        {
            MostrarCargando(false);
        }
    }

    // Busca un valor en el XML por nombre de etiqueta
    private static string? BuscarValorXml(XElement root, params string[] elementNames)
    {
        foreach (var name in elementNames)
        {
            var elem = root.Descendants()
                .FirstOrDefault(e => e.Name.LocalName.Equals(name, StringComparison.OrdinalIgnoreCase));
            if (elem != null && !string.IsNullOrWhiteSpace(elem.Value))
                return elem.Value.Trim();
        }
        return null;
    }

    // Guarda en la BD (comprueba duplicados antes)
    private async Task GuardarAutomatico(ResultadoFactura invoice)
    {
        var duplicate = await _databaseService.FindDuplicateAsync(invoice.FileName, invoice.RawText);

        if (duplicate != null)
        {
            bool overwrite = await DisplayAlert(
                L("duplicate_title"),
                $"{L("duplicate_msg")}:\n'{duplicate.FileName}' ({duplicate.AnalyzedAt:dd/MM/yyyy HH:mm})\n\n{L("save_anyway")}",
                L("save"), L("cancel"));
            if (!overwrite)
            {
                lblStatus.Text = L("save_cancelled");
                return;
            }
        }

        await _databaseService.SaveInvoiceAsync(invoice);

        // Copiar a carpeta de backup si esta activada
        await CopiarABackup(invoice);

        lblStatus.Text = L("saved_auto");
    }

    // Copia de seguridad (si esta activada en ajustes)
    private static async Task CopiarABackup(ResultadoFactura invoice)
    {
        bool backupEnabled = Preferences.Get("BackupEnabled", false);
        string backupFolder = Preferences.Get("BackupFolder", "");
        if (!backupEnabled || string.IsNullOrEmpty(backupFolder)) return;

        try
        {
            Directory.CreateDirectory(backupFolder);

            // Copiar el archivo de texto con los datos extraidos
            string txtFile = Path.Combine(backupFolder, $"factura_{invoice.AnalyzedAt:yyyyMMdd_HHmmss}.txt");
            await File.WriteAllTextAsync(txtFile, invoice.RawText);

            // Copiar la imagen/archivo original si existe
            if (!string.IsNullOrEmpty(invoice.ImagePath) && File.Exists(invoice.ImagePath))
            {
                string destFile = Path.Combine(backupFolder, Path.GetFileName(invoice.ImagePath));
                File.Copy(invoice.ImagePath, destFile, overwrite: true);
            }
        }
        catch (Exception)
        {
            // No interrumpir el flujo si falla la copia
        }
    }

    // Muestra/oculta el spinner de carga
    private void MostrarCargando(bool loading)
    {
        loadingIndicator.IsRunning = loading;
        loadingIndicator.IsVisible = loading;
        btnTakePhoto.IsEnabled = !loading;
        btnPickPhoto.IsEnabled = !loading;
        btnBatch.IsEnabled = !loading;
    }

    // Rellena la ficha visual
    private void RellenarFicha(string proveedor, string numero, string fecha, string total)
    {
        lblFichaProveedor.Text = string.IsNullOrEmpty(proveedor) ? L("not_detected") : proveedor;
        lblFichaNumero.Text = string.IsNullOrEmpty(numero) ? L("not_detected") : numero;
        lblFichaFecha.Text = string.IsNullOrEmpty(fecha) ? L("not_detected") : fecha;
        lblFichaTotal.Text = string.IsNullOrEmpty(total) ? L("not_detected") : total;

        // Resaltar en rojo los campos que no se detectaron
        lblFichaProveedor.TextColor = string.IsNullOrEmpty(proveedor) ? Colors.Gray : Colors.White;
        lblFichaNumero.TextColor = string.IsNullOrEmpty(numero) ? Colors.Gray : Colors.White;
        lblFichaFecha.TextColor = string.IsNullOrEmpty(fecha) ? Colors.Gray : Colors.White;
        lblFichaTotal.TextColor = string.IsNullOrEmpty(total) ? Colors.Gray : Color.FromArgb("#10B981");
    }

    // Limpia la ficha visual
    private void LimpiarFicha()
    {
        lblFichaProveedor.Text = "-";
        lblFichaNumero.Text = "-";
        lblFichaFecha.Text = "-";
        lblFichaTotal.Text = "-";
        lblFichaProveedor.TextColor = Colors.White;
        lblFichaNumero.TextColor = Colors.White;
        lblFichaFecha.TextColor = Colors.White;
        lblFichaTotal.TextColor = Color.FromArgb("#10B981");
    }

    // Guarda una copia del archivo en la carpeta de la app
    private static async Task<string> GuardarArchivoLocal(FileResult file)
    {
        string baseDir = Preferences.Get("DbDirectory", ServicioBaseDatos.DefaultDbDirectory);
        string imagesDir = Path.Combine(baseDir, "images");
        Directory.CreateDirectory(imagesDir);

        string destPath = Path.Combine(imagesDir, $"{DateTime.Now:yyyyMMdd_HHmmss}_{file.FileName}");
        using var sourceStream = await file.OpenReadAsync();
        using var destStream = File.Create(destPath);
        await sourceStream.CopyToAsync(destStream);
        return destPath;
    }

    // Saca un campo de los Documents[].Fields de Azure (VendorName, InvoiceId, etc.)
    // Si no lo encuentra devuelve null y se usa el fallback manual
    private static string? ExtraerCampo(AnalyzeResult result, string fieldName)
    {
        foreach (var doc in result.Documents)
        {
            if (doc.Fields.TryGetValue(fieldName, out var field))
            {
                var val = field.Content;
                if (!string.IsNullOrWhiteSpace(val))
                    return val.Trim();
            }
        }
        return null;
    }

    // Busqueda manual en pares clave-valor y tablas (para cuando Azure no lo pilla solo)
    private static string ExtraerKeyValue(AnalyzeResult result, int maxValueLength, params string[] keywords)
    {
        // 1) Buscar en pares clave-valor del OCR
        foreach (var keyword in keywords)
        {
            string kw = keyword.ToLowerInvariant();
            foreach (var kvp in result.KeyValuePairs)
            {
                if (kvp.Value == null) continue;
                string key = kvp.Key.Content?.ToLowerInvariant() ?? "";
                string val = kvp.Value.Content?.Trim() ?? "";
                if (string.IsNullOrEmpty(val)) continue;
                if (key == kw || key.StartsWith(kw))
                {
                    // A veces el OCR mete parte del valor dentro de la clave
                    // Ej: "Date of Invoice:Aug." => "14, 2023"  -> deberia ser "Aug. 14, 2023"
                    string extra = key.Length > kw.Length ? kvp.Key.Content!.Substring(kw.Length).TrimStart(':', ' ') : "";
                    string fullVal = string.IsNullOrEmpty(extra) ? val : $"{extra} {val}";
                    if (fullVal.Length <= maxValueLength)
                        return fullVal.Trim();
                }
            }
        }

        // 2) Buscar en tablas: a veces el total u otros campos estan en la ultima fila de una tabla
        foreach (var keyword in keywords)
        {
            string kw = keyword.ToLowerInvariant();
            foreach (var tbl in result.Tables)
            {
                foreach (var cell in tbl.Cells)
                {
                    string cellText = cell.Content?.ToLowerInvariant() ?? "";
                    if (cellText.Contains(kw))
                    {
                        // Buscar el valor en la misma fila, ultima columna
                        var valueCell = tbl.Cells
                            .Where(c => c.RowIndex == cell.RowIndex && c.ColumnIndex > cell.ColumnIndex)
                            .OrderByDescending(c => c.ColumnIndex)
                            .FirstOrDefault();
                        if (valueCell != null && !string.IsNullOrWhiteSpace(valueCell.Content)
                            && valueCell.Content.Trim().Length <= maxValueLength)
                            return valueCell.Content.Trim();
                    }
                }
            }
        }
        return "";
    }

    // Intenta sacar el nombre del proveedor buscando en las claves y lineas del documento
    private static string ExtraerProveedor(AnalyzeResult result)
    {
        // 1) Buscar en KV pairs con claves tipicas de emisor
        string[] vendorKeys = { "seller", "vendor", "from", "emitida por", "empresa emisora", "razon social", "proveedor" };
        foreach (var kw in vendorKeys)
        {
            foreach (var kvp in result.KeyValuePairs)
            {
                if (kvp.Value == null) continue;
                string key = kvp.Key.Content?.ToLowerInvariant() ?? "";
                if (key.StartsWith(kw))
                    return kvp.Value.Content?.Trim() ?? "";
            }
        }

        // 2) Obtener datos del cliente para poder descartarlos luego
        //    Ojo: la clave puede venir como "EMITIDA A:" o "FACTURA\nEMITIDA A:" (el OCR las junta a veces)
        string clientData = "";
        foreach (var kvp in result.KeyValuePairs)
        {
            if (kvp.Value == null) continue;
            string key = kvp.Key.Content?.ToLowerInvariant() ?? "";
            string val = kvp.Value.Content?.ToLowerInvariant() ?? "";
            if (key.Contains("emitida a") || key.Contains("facturado a") || key.Contains("cliente")
                || key.Contains("client") || key.Contains("bill to") || key.Contains("ship to")
                || key.Contains("invoice to") || key.Contains("buyer") || key.Contains("customer"))
            {
                clientData = val;
                break;
            }
        }
        // Fallback: si no hay clave de cliente, buscar "factura" con valor largo (suele ser datos del cliente)
        if (string.IsNullOrEmpty(clientData))
        {
            foreach (var kvp in result.KeyValuePairs)
            {
                if (kvp.Value == null) continue;
                string key = kvp.Key.Content?.ToLowerInvariant() ?? "";
                string val = kvp.Value.Content?.ToLowerInvariant() ?? "";
                if (key.StartsWith("factura") && val.Length > 30)
                {
                    clientData = val;
                    break;
                }
            }
        }

        // Separar en palabras para comparar luego linea por linea
        var clientWords = clientData
            .Split(new[] { ' ', ',', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries)
            .Where(w => w.Length > 2)
            .ToHashSet();

        // 3) Recorrer las primeras lineas de la pagina buscando algo que parezca nombre de empresa
        if (result.Pages.Count > 0)
        {
            var lines = result.Pages[0].Lines;

            // Palabras con las que suelen empezar lineas que NO son el nombre de empresa
            string[] skipStarts = { "factura", "emitida", "fecha", "pedido", "total", "base", "iva",
                                    "producto", "servicio", "cantidad", "precio", "retencion",
                                    "detalles", "banco", "condiciones", "n.º", "n°", "vencimiento",
                                    "superbanco", "calle" };

            foreach (var line in lines.Take(20))
            {
                string text = line.Content.Trim();
                string lower = text.ToLowerInvariant();

                // Saltar labels, headers, lineas muy cortas o muy largas
                if (skipStarts.Any(s => lower.StartsWith(s))) continue;
                if (text.Length < 2 || text.Length > 40) continue;

                // Saltar numeros, emails, telefonos, direcciones
                if (double.TryParse(text.Replace("€", "").Replace(" ", ""), out _)) continue;
                if (lower.Contains("@")) continue;
                if (lower.StartsWith("c/")) continue;
                if (text.All(c => char.IsDigit(c) || c == '-' || c == ' ' || c == '+' || c == '/' || c == '.')) continue;

                // Saltar fechas tipo dd/mm/yyyy
                if (System.Text.RegularExpressions.Regex.IsMatch(text, @"^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$")) continue;

                // Si todas las palabras de esta linea estan en los datos del cliente, es del cliente -> saltar
                var lineWords = text.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                if (lineWords.Length > 0 && clientWords.Count > 0)
                {
                    bool allInClient = lineWords.All(w =>
                        clientWords.Contains(w.ToLowerInvariant().TrimEnd(',', '.', ':')));
                    if (allInClient) continue;
                }

                // Si llega aqui, probablemente es el nombre de la empresa
                return text;
            }
        }
        return "";
    }

    // Formatea el resultado de Azure para mostrarlo como texto
    private static string FormatearResultado(AnalyzeResult result)
    {
        var sb = new StringBuilder();

        // Pares Clave-Valor
        sb.AppendLine($"=== {ServicioIdiomas.T("fmt_kv")} ===");
        foreach (var kvp in result.KeyValuePairs)
        {
            if (kvp.Value is null)
                sb.AppendLine($"  {ServicioIdiomas.T("fmt_key_no_value")}: '{kvp.Key.Content}'");
            else
                sb.AppendLine($"  {kvp.Key.Content} => {kvp.Value.Content}");
        }
        sb.AppendLine();

        // Campos del Documento (Fields)
        sb.AppendLine($"=== {ServicioIdiomas.T("fmt_fields")} ===");
        foreach (var doc in result.Documents)
        {
            sb.AppendLine($"  {ServicioIdiomas.T("fmt_type")}: {doc.DocumentType} ({ServicioIdiomas.T("fmt_confidence")}: {doc.Confidence:0.00})");
            foreach (var f in doc.Fields)
            {
                var fld = f.Value;
                var val = fld.Content;
                sb.AppendLine($"    {f.Key}: '{val}' [tipo={fld.FieldType}, conf={fld.Confidence:0.00}]");
            }
            sb.AppendLine();
        }

        // Paginas y lineas
        sb.AppendLine($"=== {ServicioIdiomas.T("fmt_pages")} ===");
        foreach (var page in result.Pages)
        {
            sb.AppendLine($"  {ServicioIdiomas.T("fmt_page")} {page.PageNumber}: {page.Lines.Count} {ServicioIdiomas.T("fmt_lines")}, {page.Words.Count} {ServicioIdiomas.T("fmt_words")}");
            foreach (var line in page.Lines)
            {
                sb.AppendLine($"    > {line.Content}");
            }
            sb.AppendLine();
        }

        // Tablas
        sb.AppendLine($"=== {ServicioIdiomas.T("fmt_tables")} ===");
        for (int t = 0; t < result.Tables.Count; t++)
        {
            var tbl = result.Tables[t];
            sb.AppendLine($"  {ServicioIdiomas.T("fmt_table")} {t}: {tbl.RowCount} {ServicioIdiomas.T("fmt_rows")} x {tbl.ColumnCount} {ServicioIdiomas.T("fmt_cols")}");
            foreach (var cell in tbl.Cells)
            {
                sb.AppendLine($"    Celda({cell.RowIndex},{cell.ColumnIndex})[{cell.Kind}] '{cell.Content}'");
            }
            sb.AppendLine();
        }

        return sb.ToString();
    }
}
