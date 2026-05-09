namespace FacturasOCR.Servicios;

// Servicio de idiomas de la app
// Idiomas soportados: lenguas de España + English
public static class ServicioIdiomas
{
    // Idiomas disponibles (codigo, nombre) en orden fijo
    public static readonly List<(string Code, string Name)> IdiomasDisponibles = new()
    {
        ("es", "Castellano"),
        ("an", "Aragonés"),
        ("oc", "Aranés (Occitan)"),
        ("ast", "Asturianu"),
        ("ca", "Català"),
        ("eu", "Euskara"),
        ("ext", "Estremeñu"),
        ("gl", "Galego"),
        ("en", "English")
    };

    // Idioma actual (se lee de Preferences)
    public static string IdiomaActual =>
        Preferences.Get("AppLanguage", "es");

    // Metodo principal: devuelve el texto traducido para una clave
    public static string T(string key)
    {
        string lang = IdiomaActual;
        if (_translations.TryGetValue(key, out var langs))
        {
            if (langs.TryGetValue(lang, out var text))
                return text;
            // Fallback a castellano
            if (langs.TryGetValue("es", out var esText))
                return esText;
        }
        return key;
    }

    // Evento que se dispara al cambiar de idioma (para actualizar toda la app)
    public static event Action? IdiomaChanged;

    // Cambia el idioma y lo guarda en Preferences
    public static void CambiarIdioma(string codigo)
    {
        Preferences.Set("AppLanguage", codigo);
        IdiomaChanged?.Invoke();
    }

    // Abreviatura: pones castellano como base + solo los idiomas que difieren
    private static Dictionary<string, string> Tr(string es, string? an = null, string? oc = null,
        string? ast = null, string? ca = null, string? eu = null, string? ext = null,
        string? gl = null, string? en = null)
    {
        var d = new Dictionary<string, string> { { "es", es } };
        d["an"] = an ?? es;
        d["oc"] = oc ?? es;
        d["ast"] = ast ?? es;
        d["ca"] = ca ?? es;
        d["eu"] = eu ?? es;
        d["ext"] = ext ?? es;
        d["gl"] = gl ?? es;
        d["en"] = en ?? es;
        return d;
    }

    // Todas las traducciones de la app
    private static readonly Dictionary<string, Dictionary<string, string>> _translations = new()
    {
        // === NAVEGACION (AppShell) ===
        ["tab_analyze"] = Tr("Analizar", an: "Analisar", oc: "Analisar", ast: "Analizar", ca: "Analitzar", eu: "Aztertu", ext: "Analizal", gl: "Analizar", en: "Analyze"),
        ["tab_archive"] = Tr("Archivo", an: "Archibo", oc: "Archiu", ast: "Archivu", ca: "Arxiu", eu: "Artxiboa", ext: "Archivu", gl: "Arquivo", en: "Archive"),
        ["tab_settings"] = Tr("Ajustes", an: "Achustes", oc: "Ajustes", ast: "Axustes", ca: "Configuració", eu: "Ezarpenak", ext: "Ajustis", gl: "Axustes", en: "Settings"),

        // === PAGINA PRINCIPAL ===
        ["main_title"] = Tr("OCR de Facturas", an: "OCR de Facturas", oc: "OCR de Factures", ast: "OCR de Factures", ca: "OCR de Factures", eu: "Fakturen OCR", ext: "OCR de Faturas", gl: "OCR de Facturas", en: "Invoice OCR"),
        ["main_instruction"] = Tr(
            "Selecciona una factura (imagen, PDF o XML) para analizar con OCR de Azure.",
            an: "Selecciona una factura (imachen, PDF u XML) pa analisar con OCR d'Azure.",
            oc: "Selecciona ua factura (imòrfo, PDF o XML) entà analisar damb OCR d'Azure.",
            ast: "Seleiciona una factura (imaxe, PDF o XML) pa analizar con OCR d'Azure.",
            ca: "Selecciona una factura (imatge, PDF o XML) per analitzar amb OCR d'Azure.",
            eu: "Hautatu faktura bat (irudia, PDF edo XML) Azure OCR bidez aztertzeko.",
            ext: "Seleciона una fatura (imagen, PDF u XML) pa analizal con OCR d'Azure.",
            gl: "Selecciona unha factura (imaxe, PDF ou XML) para analizar con OCR de Azure.",
            en: "Select an invoice (image, PDF or XML) to analyze with Azure OCR."),
        ["btn_photo"] = Tr("Tomar Foto", an: "Fer Foto", oc: "HarÒfo", ast: "Sacar Semeya", ca: "Fer Foto", eu: "Argazkia Atera", ext: "Sacal Fotu", gl: "Tomar Foto", en: "Take Photo"),
        ["btn_file"] = Tr("Elegir Archivo", an: "Trigar Archibo", oc: "Causir Archiu", ast: "Escoyer Archivu", ca: "Triar Fitxer", eu: "Fitxategia Aukeratu", ext: "Eligil Archivu", gl: "Elixir Arquivo", en: "Choose File"),
        ["btn_batch"] = Tr("Procesar Lote", an: "Procesar Lote", oc: "Processar Òla", ast: "Procesar Llote", ca: "Processar Lot", eu: "Sorta Prozesatu", ext: "Procesal Loti", gl: "Procesar Lote", en: "Batch Process"),
        ["summary_title"] = Tr("Resumen de la Factura", an: "Resumen d'a Factura", oc: "Resumit dera Factura", ast: "Resume de la Factura", ca: "Resum de la Factura", eu: "Fakturaren Laburpena", ext: "Resumen de la Fatura", gl: "Resumo da Factura", en: "Invoice Summary"),
        ["provider"] = Tr("Proveedor:", an: "Proveedor:", oc: "Òrnòr:", ast: "Proveedor:", ca: "Proveïdor:", eu: "Hornitzailea:", ext: "Proveol:", gl: "Provedor:", en: "Vendor:"),
        ["invoice_num"] = Tr("N. Factura:", ca: "N. Factura:", eu: "Faktura Zk.:", en: "Invoice #:"),
        ["date"] = Tr("Fecha:", an: "Calendata:", oc: "Data:", ast: "Fecha:", ca: "Data:", eu: "Data:", ext: "Fecha:", gl: "Data:", en: "Date:"),
        ["total"] = Tr("Total:", eu: "Guztira:", en: "Total:"),
        ["zoom_hint"] = Tr("Toca para cerrar", an: "Toca pa zarrar", oc: "Tòca entà barrar", ast: "Toca pa zarrar", ca: "Toca per tancar", eu: "Sakatu ixteko", ext: "Toca pa cerral", gl: "Toca para pechar", en: "Tap to close"),
        ["ocr_data"] = Tr("Datos completos del OCR:", an: "Datos completos de l'OCR:", oc: "Dades complòtes der OCR:", ast: "Datos completos del OCR:", ca: "Dades completes de l'OCR:", eu: "OCR datu osoak:", ext: "Datus completrus del OCR:", gl: "Datos completos do OCR:", en: "Full OCR data:"),
        ["placeholder_ocr"] = Tr(
            "Aqui apareceran los datos completos del OCR.\n\nFormatos aceptados:\n  - Imagenes (JPG, PNG, BMP, TIFF)\n  - Documentos PDF\n  - Facturas electronicas XML (FacturaE)",
            ast: "Equí apaecerán los datos completos del OCR.\n\nFormatos aceutaos:\n  - Imáxenes (JPG, PNG, BMP, TIFF)\n  - Documentos PDF\n  - Factures electróniques XML (FacturaE)",
            ca: "Aquí apareixeran les dades completes de l'OCR.\n\nFormats acceptats:\n  - Imatges (JPG, PNG, BMP, TIFF)\n  - Documents PDF\n  - Factures electròniques XML (FacturaE)",
            eu: "Hemen OCR datu osoak agertuko dira.\n\nOnartutako formatuak:\n  - Irudiak (JPG, PNG, BMP, TIFF)\n  - PDF dokumentuak\n  - XML faktura elektronikoak (FacturaE)",
            gl: "Aquí aparecerán os datos completos do OCR.\n\nFormatos aceptados:\n  - Imaxes (JPG, PNG, BMP, TIFF)\n  - Documentos PDF\n  - Facturas electrónicas XML (FacturaE)",
            en: "Full OCR data will appear here.\n\nAccepted formats:\n  - Images (JPG, PNG, BMP, TIFF)\n  - PDF documents\n  - Electronic invoices XML (FacturaE)"),
        ["status_ready"] = Tr(
            "Listo. Las facturas se guardan automaticamente al procesarlas.",
            an: "Listo. Las facturas se guardan automaticament al procesalas.",
            oc: "Prèòste. Les factures se guòrden automaticament en processà-les.",
            ast: "Llisto. Les factures guárdense automáticamente al procesales.",
            ca: "Llest. Les factures es guarden automàticament en processar-les.",
            eu: "Prest. Fakturak automatikoki gordetzen dira prozesatzean.",
            ext: "Listu. Las faturas se guardan automáticamente al procesalas.",
            gl: "Listo. As facturas gárdanse automaticamente ao procesalas.",
            en: "Ready. Invoices are saved automatically when processed."),
        ["storage_label"] = Tr("Almacenamiento", an: "Almagazenamiento", oc: "Emmagatzemòrfo", ast: "Almacenamientu", ca: "Emmagatzematge", eu: "Biltegiratzea", ext: "Almacenamientu", gl: "Almacenamento", en: "Storage"),
        ["not_detected"] = Tr("(no detectado)", an: "(no detectau)", oc: "(non detectat)", ast: "(non detectao)", ca: "(no detectat)", eu: "(ez detektatua)", ext: "(no detectau)", gl: "(non detectado)", en: "(not detected)"),

        // === Alertas generales ===
        ["error"] = Tr("Error", eu: "Errorea", en: "Error"),
        ["ok"] = Tr("OK", eu: "Ados", en: "OK"),
        ["cancel"] = Tr("Cancelar", an: "Cancelar", oc: "Anullar", ast: "Encaboxar", ca: "Cancel·lar", eu: "Utzi", ext: "Cancelal", gl: "Cancelar", en: "Cancel"),
        ["save"] = Tr("Guardar", an: "Guardar", oc: "Guardar", ast: "Guardar", ca: "Desar", eu: "Gorde", ext: "Guardal", gl: "Gardar", en: "Save"),
        ["delete"] = Tr("Eliminar", an: "Eliminar", oc: "Eliminar", ast: "Desaniciar", ca: "Eliminar", eu: "Ezabatu", ext: "Eliminal", gl: "Eliminar", en: "Delete"),
        ["confirm"] = Tr("Confirmar", eu: "Berretsi", en: "Confirm"),
        ["yes"] = Tr("Si", an: "Si", oc: "Òc", ast: "Sí", ca: "Sí", eu: "Bai", ext: "Sí", gl: "Si", en: "Yes"),
        ["info"] = Tr("Info"),
        ["saved"] = Tr("Guardado", an: "Guardau", oc: "Guardat", ast: "Guardao", ca: "Desat", eu: "Gordeta", ext: "Guardau", gl: "Gardado", en: "Saved"),
        ["path_label"] = Tr("Ruta", an: "Ruta", oc: "Camin", ast: "Ruta", ca: "Ruta", eu: "Bidea", ext: "Ruta", gl: "Ruta", en: "Path"),

        // === Alertas PaginaPrincipal ===
        ["camera_unavailable"] = Tr("La camara no esta disponible en este dispositivo.", ast: "La cámara nun ta disponible nesti dispositivu.", ca: "La càmera no està disponible en aquest dispositiu.", eu: "Kamera ez dago erabilgarri gailu honetan.", gl: "A cámara non está dispoñible neste dispositivo.", en: "Camera is not available on this device."),
        ["camera_permission"] = Tr("No se otorgaron permisos de camara.", ast: "Nun se dieron permisos de cámara.", ca: "No s'han concedit permisos de càmera.", eu: "Kamera baimenak ez dira eman.", gl: "Non se concederon permisos de cámara.", en: "Camera permissions were not granted."),
        ["error_capture"] = Tr("Error al capturar foto", ast: "Error al sacar semeya", ca: "Error en capturar foto", eu: "Errorea argazkia ateratzean", gl: "Erro ao capturar foto", en: "Error capturing photo"),
        ["picker_title"] = Tr("Selecciona una factura", an: "Selecciona una factura", oc: "Selecciona ua factura", ast: "Seleiciona una factura", ca: "Selecciona una factura", eu: "Hautatu faktura bat", ext: "Seleciona una fatura", gl: "Selecciona unha factura", en: "Select an invoice"),
        ["picker_batch"] = Tr("Selecciona facturas para procesar", an: "Selecciona facturas pa procesar", oc: "Selecciona factures entà processar", ast: "Seleiciona factures pa procesar", ca: "Selecciona factures per processar", eu: "Hautatu fakturak prozesatzeko", ext: "Seleciona faturas pa processal", gl: "Selecciona facturas para procesar", en: "Select invoices to process"),
        ["error_select"] = Tr("Error al seleccionar archivo", ast: "Error al escoyer archivu", ca: "Error en seleccionar fitxer", eu: "Errorea fitxategia hautatzean", gl: "Erro ao seleccionar arquivo", en: "Error selecting file"),
        ["batch_header"] = Tr("Procesamiento por lotes", an: "Procesamiento per lotes", oc: "Processament per òles", ast: "Procesamientu per llotes", ca: "Processament per lots", eu: "Sorta prozesatzea", ext: "Procesamientu por lotis", gl: "Procesamento por lotes", en: "Batch processing"),
        ["processing"] = Tr("Procesando", an: "Procesando", oc: "Processant", ast: "Procesando", ca: "Processant", eu: "Prozesatzen", ext: "Procesandu", gl: "Procesando", en: "Processing"),
        ["duplicate_omitted"] = Tr("DUPLICADA - omitida", ca: "DUPLICADA - omesa", eu: "BIKOIZTUA - baztertua", gl: "DUPLICADA - omitida", en: "DUPLICATE - skipped"),
        ["already_exists"] = Tr("Ya existe", ca: "Ja existeix", eu: "Dagoeneko existitzen da", gl: "Xa existe", en: "Already exists"),
        ["batch_completed"] = Tr("Lote completado", an: "Lote completau", oc: "Òla completada", ast: "Llote completáu", ca: "Lot completat", eu: "Sorta osatua", ext: "Loti completau", gl: "Lote completado", en: "Batch completed"),
        ["successful"] = Tr("exitosas", ca: "correctes", eu: "arrakastatsu", gl: "exitosas", en: "successful"),
        ["errors"] = Tr("errores", ca: "errors", eu: "errore", gl: "erros", en: "errors"),
        ["analyzing_azure"] = Tr("Analizando documento con Azure OCR...", an: "Analisando documento con Azure OCR...", oc: "Analisand document damb Azure OCR...", ast: "Analizando documentu con Azure OCR...", ca: "Analitzant document amb Azure OCR...", eu: "Dokumentua Azure OCR bidez aztertzen...", ext: "Analizandu documentu con Azure OCR...", gl: "Analizando documento con Azure OCR...", en: "Analyzing document with Azure OCR..."),
        ["processing_xml"] = Tr("Procesando factura electronica XML...", ast: "Procesando factura electrónica XML...", ca: "Processant factura electrònica XML...", eu: "XML faktura elektronikoa prozesatzen...", gl: "Procesando factura electrónica XML...", en: "Processing electronic invoice XML..."),
        ["error_analyze"] = Tr("Error al analizar el documento", ast: "Error al analizar el documentu", ca: "Error en analitzar el document", eu: "Errorea dokumentua aztertzean", gl: "Erro ao analizar o documento", en: "Error analyzing document"),
        ["error_analysis"] = Tr("Error en el analisis", ca: "Error en l'anàlisi", eu: "Errorea azterketan", gl: "Erro na análise", en: "Analysis error"),
        ["error_xml"] = Tr("Error al procesar XML", ca: "Error en processar XML", eu: "Errorea XML prozesatzean", gl: "Erro ao procesar XML", en: "Error processing XML"),
        ["duplicate_title"] = Tr("Factura duplicada", ast: "Factura duplicada", ca: "Factura duplicada", eu: "Faktura bikoiztua", gl: "Factura duplicada", en: "Duplicate invoice"),
        ["duplicate_msg"] = Tr("Ya existe una factura similar", ca: "Ja existeix una factura similar", eu: "Antzeko faktura bat dagoeneko existitzen da", gl: "Xa existe unha factura similar", en: "A similar invoice already exists"),
        ["save_anyway"] = Tr("¿Guardar de todos modos?", ast: "¿Guardar igual?", ca: "Desar igualment?", eu: "Gorde hala ere?", gl: "Gardar igualmente?", en: "Save anyway?"),
        ["save_cancelled"] = Tr("Guardado cancelado (duplicada)", ast: "Guardao cancelao (duplicada)", ca: "Desat cancel·lat (duplicada)", eu: "Gordetzea utzita (bikoiztua)", gl: "Gardado cancelado (duplicada)", en: "Save cancelled (duplicate)"),
        ["saved_auto"] = Tr("Guardado automaticamente en archivo", an: "Guardau automaticament en archibo", oc: "Guardat automaticament en archiu", ast: "Guardao automáticamente n'archivu", ca: "Desat automàticament a l'arxiu", eu: "Automatikoki gordeta artxiboan", ext: "Guardau automáticamente en archivu", gl: "Gardado automaticamente no arquivo", en: "Automatically saved to archive"),
        ["error_batch"] = Tr("Error en procesamiento por lotes", ca: "Error en processament per lots", eu: "Errorea sorta prozesatzean", gl: "Erro no procesamento por lotes", en: "Error in batch processing"),

        // === Formato resultado OCR ===
        ["fmt_kv"] = Tr("Pares Clave-Valor", ca: "Parells Clau-Valor", eu: "Gako-Balio Bikoteak", gl: "Pares Clave-Valor", en: "Key-Value Pairs"),
        ["fmt_key_no_value"] = Tr("Clave sin valor", ca: "Clau sense valor", eu: "Gakoa baliorik gabe", gl: "Clave sen valor", en: "Key without value"),
        ["fmt_fields"] = Tr("Campos del Documento", ast: "Campos del Documentu", ca: "Camps del Document", eu: "Dokumentuaren Eremuak", gl: "Campos do Documento", en: "Document Fields"),
        ["fmt_type"] = Tr("Tipo", an: "Tipo", oc: "Òrfo", ast: "Tipu", ca: "Tipus", eu: "Mota", ext: "Tipu", gl: "Tipo", en: "Type"),
        ["fmt_confidence"] = Tr("confianza", an: "confianza", oc: "confidòncia", ast: "confianza", ca: "confiança", eu: "konfiantza", ext: "confianza", gl: "confianza", en: "confidence"),
        ["fmt_pages"] = Tr("Paginas / Diseno", ast: "Páxines / Diseñu", ca: "Pàgines / Disseny", eu: "Orrialdeak / Diseinua", gl: "Páxinas / Deseño", en: "Pages / Layout"),
        ["fmt_page"] = Tr("Pagina", ast: "Páxina", ca: "Pàgina", eu: "Orrialdea", gl: "Páxina", en: "Page"),
        ["fmt_lines"] = Tr("lineas", ast: "llinies", ca: "línies", eu: "lerro", gl: "liñas", en: "lines"),
        ["fmt_words"] = Tr("palabras", ast: "pallabres", ca: "paraules", eu: "hitz", gl: "palabras", en: "words"),
        ["fmt_tables"] = Tr("Tablas", ast: "Tables", ca: "Taules", eu: "Taulak", gl: "Táboas", en: "Tables"),
        ["fmt_table"] = Tr("Tabla", ast: "Tabla", ca: "Taula", eu: "Taula", gl: "Táboa", en: "Table"),
        ["fmt_rows"] = Tr("filas", ast: "fileres", ca: "files", eu: "errenkada", gl: "filas", en: "rows"),
        ["fmt_cols"] = Tr("columnas", ast: "columnes", ca: "columnes", eu: "zutabe", gl: "columnas", en: "columns"),
        ["fmt_xml_title"] = Tr("Factura Electronica (XML)", ast: "Factura Electrónica (XML)", ca: "Factura Electrònica (XML)", eu: "Faktura Elektronikoa (XML)", gl: "Factura Electrónica (XML)", en: "Electronic Invoice (XML)"),
        ["fmt_xml_summary"] = Tr("Contenido XML (resumen)", ast: "Conteníu XML (resume)", ca: "Contingut XML (resum)", eu: "XML edukia (laburpena)", gl: "Contido XML (resumo)", en: "XML Content (summary)"),

        // === PAGINA AJUSTES ===
        ["settings_title"] = Tr("Ajustes", an: "Achustes", oc: "Ajustes", ast: "Axustes", ca: "Configuració", eu: "Ezarpenak", ext: "Ajustis", gl: "Axustes", en: "Settings"),
        ["azure_title"] = Tr("Azure Document Intelligence"),
        ["azure_desc"] = Tr("Datos del recurso Azure para el OCR. Los encontraras en portal.azure.com -> tu recurso -> 'Claves y punto de conexion'.", an: "Datos d'o recurso Azure pa l'OCR. Los trobarás en portal.azure.com -> o tuyo recurso -> 'Claus y punto de conexión'.", oc: "Dades der recòrs Azure entath OCR. Les trobaràs en portal.azure.com -> eth tòn recòrs -> 'Claus e punt de connexion'.", ast: "Datos del recursu Azure pal OCR. Atoparálos en portal.azure.com -> el to recursu -> 'Claves y puntu de conexón'.", ca: "Dades del recurs Azure per a l'OCR. Les trobaràs a portal.azure.com -> el teu recurs -> 'Claus i punt de connexió'.", eu: "Azure baliabidearen datuak OCR-rako. portal.azure.com -> zure baliabidea -> 'Gakoak eta konexio-puntua' aurkituko dituzu.", ext: "Datus del recursu Azure pal OCR. Los encontrarás en portal.azure.com -> tu recursu -> 'Clavis i puntu de conexión'.", gl: "Datos do recurso Azure para o OCR. Atoparalos en portal.azure.com -> o teu recurso -> 'Claves e punto de conexión'.", en: "Azure resource data for OCR. Find them at portal.azure.com -> your resource -> 'Keys and endpoint'."),
        ["api_key"] = Tr("Clave API (API Key)", an: "Clau API (API Key)", oc: "Clau API (API Key)", ast: "Clave API (API Key)", ca: "Clau API (API Key)", eu: "API Gakoa (API Key)", ext: "Clavi API (API Key)", gl: "Clave API (API Key)", en: "API Key"),
        ["saved_locally"] = Tr("Se guarda de forma local en el dispositivo.", an: "Se guarda de traza local en o dispositibo.", oc: "Se guòrde de fòrma locòla en eth dispositòr.", ast: "Guárdase de forma llocal nel dispositivu.", ca: "Es guarda de forma local al dispositiu.", eu: "Gailuan lokalki gordetzen da.", ext: "Se guarda de forma local en el dispositivu.", gl: "Gárdase de forma local no dispositivo.", en: "Saved locally on the device."),
        ["model_info"] = Tr("Modelo: prebuilt-invoice (extrae campos de factura automaticamente)", an: "Modelo: prebuilt-invoice (extrai campos de factura automaticament)", oc: "Modòr: prebuilt-invoice (extraòt camps de factura automaticament)", ast: "Modelu: prebuilt-invoice (estrái campos de factura automáticamente)", ca: "Model: prebuilt-invoice (extreu camps de factura automàticament)", eu: "Eredua: prebuilt-invoice (fakturaren eremuak automatikoki ateratzen ditu)", ext: "Modelu: prebuilt-invoice (extrai campus de fatura automáticamente)", gl: "Modelo: prebuilt-invoice (extrae campos de factura automaticamente)", en: "Model: prebuilt-invoice (extracts invoice fields automatically)"),
        ["btn_save_azure"] = Tr("Guardar Azure", an: "Guardar Azure", oc: "Guardar Azure", ast: "Guardar Azure", ca: "Desar Azure", eu: "Azure Gorde", ext: "Guardal Azure", gl: "Gardar Azure", en: "Save Azure"),
        ["btn_test"] = Tr("Probar conexion", an: "Prebar conexión", oc: "Provar connexion", ast: "Probar conexón", ca: "Provar connexió", eu: "Konexioa probatu", ext: "Probal conexión", gl: "Probar conexión", en: "Test connection"),
        ["btn_reset"] = Tr("Restaurar valores", an: "Restaurar valors", oc: "Restaurar valors", ast: "Restaurar valores", ca: "Restaurar valors", eu: "Balioak berrezarri", ext: "Restaural valoris", gl: "Restaurar valores", en: "Reset values"),
        ["fill_endpoint_key"] = Tr("Debes rellenar el endpoint y la clave.", ca: "Has d'omplir l'endpoint i la clau.", eu: "Endpoint-a eta gakoa bete behar dituzu.", gl: "Debes cubrir o endpoint e a clave.", en: "You must fill in the endpoint and API key."),
        ["azure_saved"] = Tr("Configuracion de Azure guardada.\nSe aplicara en el proximo analisis.", ast: "Configuración d'Azure guardada.\nAplicaráse nel próximu análisis.", ca: "Configuració d'Azure desada.\nS'aplicarà en la propera anàlisi.", eu: "Azure konfigurazioa gordeta.\nHurrengo azterketan aplikatuko da.", gl: "Configuración de Azure gardada.\nAplicarase na próxima análise.", en: "Azure configuration saved.\nWill apply on next analysis."),
        ["fill_first"] = Tr("Rellena el endpoint y la clave primero.", ca: "Omple l'endpoint i la clau primer.", eu: "Bete endpoint-a eta gakoa lehenik.", gl: "Cubre o endpoint e a clave primeiro.", en: "Fill in the endpoint and key first."),
        ["testing_azure"] = Tr("Probando conexion con Azure...", an: "Prebando conexión con Azure...", oc: "Provand connexion damb Azure...", ast: "Probando conexón con Azure...", ca: "Provant connexió amb Azure...", eu: "Azure konexioa probatzen...", ext: "Probandu conexión con Azure...", gl: "Probando conexión con Azure...", en: "Testing Azure connection..."),
        ["connection_ok"] = Tr("Conexion correcta. El endpoint y la clave son validos.", ast: "Conexón correuta. L'endpoint y la clave son válidos.", ca: "Connexió correcta. L'endpoint i la clau son vàlids.", eu: "Konexio zuzena. Endpoint-a eta gakoa baliozkoak dira.", gl: "Conexión correcta. O endpoint e a clave son válidos.", en: "Connection successful. Endpoint and key are valid."),
        ["restore_title"] = Tr("Restaurar", an: "Restaurar", oc: "Restaurar", ast: "Restaurar", ca: "Restaurar", eu: "Berrezarri", ext: "Restaural", gl: "Restaurar", en: "Restore"),
        ["restore_confirm"] = Tr("¿Volver a los valores por defecto?", ast: "¿Volver a los valores por defeuto?", ca: "Tornar als valors per defecte?", eu: "Balio lehenetsietara itzuli?", gl: "Volver aos valores por defecto?", en: "Restore default values?"),
        ["values_restored"] = Tr("Valores restaurados.", an: "Valors restauraus.", oc: "Valors restaurats.", ast: "Valores restauraos.", ca: "Valors restaurats.", eu: "Balioak berrezarriak.", ext: "Valoris restauraus.", gl: "Valores restaurados.", en: "Values restored."),

        // === Almacenamiento ===
        ["storage_desc"] = Tr("Carpeta donde se guardan la base de datos y las copias de las facturas. Puedes cambiarla a una carpeta mas accesible (ej: Escritorio).", an: "Carpeta do se guardan a base de datos y as copias d'as facturas. Puetz cambiarla ta una carpeta más accesible (ej: Escritorio).", oc: "Carpeta a on se guòrden la bòsa de dades e les còpies des factures. Pòdes cambiar-la entà ua carpeta mès accessibla (ex: Escritòri).", ast: "Carpeta onde se guarden la base de datos y les copies de les factures. Puedes cambiala a una carpeta más accesible (ex: Escritoriu).", ca: "Carpeta on es guarden la base de dades i les còpies de les factures. Pots canviar-la a una carpeta més accessible (ex: Escriptori).", eu: "Datu-basea eta fakturen kopiak gordetzen diren karpeta. Karpeta irisgarriago batera alda dezakezu (adib: Mahaigaina).", ext: "Carpeta ondi se guardan la basi de datus i las copias de las faturas. Pueis cambial-a a una carpeta más accesibli (ej: Escritoriu).", gl: "Carpeta onde se gardan a base de datos e as copias das facturas. Podes cambiala a unha carpeta máis accesible (ex: Escritorio).", en: "Folder where the database and invoice copies are stored. You can change it to a more accessible folder (e.g., Desktop)."),
        ["data_folder"] = Tr("Carpeta de datos", an: "Carpeta de datos", oc: "Carpeta de dades", ast: "Carpeta de datos", ca: "Carpeta de dades", eu: "Datu karpeta", ext: "Carpeta de datus", gl: "Carpeta de datos", en: "Data folder"),
        ["db_images_info"] = Tr("Aqui se guardaran invoices.db y la carpeta images/ con las facturas.", an: "Aqui se guardarán invoices.db y a carpeta images/ con as facturas.", oc: "Açí se guardaràn invoices.db e la carpeta images/ damb les factures.", ast: "Equí guardaránse invoices.db y la carpeta images/ coles factures.", ca: "Aquí es guardaran invoices.db i la carpeta images/ amb les factures.", eu: "Hemen gordeko dira invoices.db eta images/ karpeta fakturekin.", ext: "Aquí se guardarán invoices.db i la carpeta images/ con las faturas.", gl: "Aquí gardaranse invoices.db e a carpeta images/ coas facturas.", en: "invoices.db and the images/ folder with invoices will be saved here."),
        ["btn_pick_folder"] = Tr("Elegir carpeta", an: "Trigar carpeta", oc: "Causir carpeta", ast: "Escoyer carpeta", ca: "Triar carpeta", eu: "Karpeta aukeratu", ext: "Eligil carpeta", gl: "Elixir carpeta", en: "Choose folder"),
        ["btn_save_path"] = Tr("Guardar ruta", an: "Guardar ruta", oc: "Guardar camin", ast: "Guardar ruta", ca: "Desar ruta", eu: "Bidea gorde", ext: "Guardal ruta", gl: "Gardar ruta", en: "Save path"),
        ["btn_restore"] = Tr("Restaurar", an: "Restaurar", oc: "Restaurar", ast: "Restaurar", ca: "Restaurar", eu: "Berrezarri", ext: "Restaural", gl: "Restaurar", en: "Restore"),
        ["current_db"] = Tr("Base de datos actual:", an: "Base de datos autual:", oc: "Bòsa de dades actuòla:", ast: "Base de datos actual:", ca: "Base de dades actual:", eu: "Uneko datu-basea:", ext: "Basi de datus atual:", gl: "Base de datos actual:", en: "Current database:"),
        ["current_files"] = Tr("Carpeta de facturas actual:", an: "Carpeta de facturas autual:", oc: "Carpeta de factures actuòla:", ast: "Carpeta de factures actual:", ca: "Carpeta de factures actual:", eu: "Uneko faktura karpeta:", ext: "Carpeta de faturas atual:", gl: "Carpeta de facturas actual:", en: "Current invoices folder:"),
        ["btn_open_folder"] = Tr("Abrir carpeta de datos", an: "Ubrir carpeta de datos", oc: "Dubrir carpeta de dades", ast: "Abrir carpeta de datos", ca: "Obrir carpeta de dades", eu: "Datu karpeta ireki", ext: "Abril carpeta de datus", gl: "Abrir carpeta de datos", en: "Open data folder"),
        ["path_empty"] = Tr("La ruta no puede estar vacia.", ca: "La ruta no pot estar buida.", eu: "Bidea ezin da hutsik egon.", gl: "A ruta non pode estar baleira.", en: "Path cannot be empty."),
        ["folder_error"] = Tr("No se puede usar esa carpeta", ca: "No es pot usar aquesta carpeta", eu: "Ezin da karpeta hori erabili", gl: "Non se pode usar esa carpeta", en: "Cannot use that folder"),
        ["folder_saved"] = Tr("Carpeta de datos cambiada", ast: "Carpeta de datos cambiada", ca: "Carpeta de dades canviada", eu: "Datu karpeta aldatua", gl: "Carpeta de datos cambiada", en: "Data folder changed"),
        ["folder_saved_msg"] = Tr("La BD y las imagenes se guardaran ahi a partir de ahora.", ast: "La BD y les imáxenes guardaránse ehí a partir d'agora.", ca: "La BD i les imatges es guardaran allà a partir d'ara.", eu: "DB-a eta irudiak hemendik aurrera hor gordeko dira.", gl: "A BD e as imaxes gardaranse aí a partir de agora.", en: "DB and images will be saved there from now on."),
        ["restore_folder_confirm"] = Tr("¿Volver a la carpeta por defecto?", ca: "Tornar a la carpeta per defecte?", eu: "Karpeta lehenetsira itzuli?", gl: "Volver á carpeta por defecto?", en: "Restore default folder?"),
        ["open_folder_error"] = Tr("No se pudo abrir automaticamente.", ca: "No s'ha pogut obrir automàticament.", eu: "Ezin izan da automatikoki ireki.", gl: "Non se puido abrir automaticamente.", en: "Could not open automatically."),
        ["pick_folder_error"] = Tr("No se pudo seleccionar carpeta", ca: "No s'ha pogut seleccionar carpeta", eu: "Ezin izan da karpeta hautatu", gl: "Non se puido seleccionar carpeta", en: "Could not select folder"),

        // === Copia de seguridad ===
        ["backup_title"] = Tr("Copia de seguridad", an: "Copia de seguridat", oc: "Còpia de seguretat", ast: "Copia de seguridá", ca: "Còpia de seguretat", eu: "Segurtasun kopia", ext: "Copia de seguridá", gl: "Copia de seguridade", en: "Backup"),
        ["backup_desc"] = Tr("Copia automatica de las facturas a otra carpeta (puede ser OneDrive, Google Drive, Dropbox o cualquier carpeta sincronizada).", an: "Copia automatica d'as facturas ta unatra carpeta (puede estar OneDrive, Google Drive, Dropbox u cualsiquiera carpeta sincronizada).", oc: "Còpia automatica des factures entà ua auta carpeta (pòt èster OneDrive, Google Drive, Dropbox o quòu carpeta sincronizada).", ast: "Copia automática de les factures a otra carpeta (puede ser OneDrive, Google Drive, Dropbox o cualesquier carpeta sincronizada).", ca: "Còpia automàtica de les factures a una altra carpeta (pot ser OneDrive, Google Drive, Dropbox o qualsevol carpeta sincronitzada).", eu: "Fakturen kopia automatikoa beste karpeta batera (OneDrive, Google Drive, Dropbox edo edozein sinkronizatutako karpeta izan daiteke).", ext: "Copia automática de las faturas a otra carpeta (puei sel OneDrive, Google Drive, Dropbox u cualisquiera carpeta sincronizada).", gl: "Copia automática das facturas a outra carpeta (pode ser OneDrive, Google Drive, Dropbox ou calquera carpeta sincronizada).", en: "Automatic invoice backup to another folder (can be OneDrive, Google Drive, Dropbox or any synced folder)."),
        ["backup_enabled"] = Tr("Activar copia de seguridad", an: "Activar copia de seguridat", oc: "Activar còpia de seguretat", ast: "Activar copia de seguridá", ca: "Activar còpia de seguretat", eu: "Segurtasun kopia aktibatu", ext: "Actival copia de seguridá", gl: "Activar copia de seguridade", en: "Enable backup"),
        ["backup_folder"] = Tr("Carpeta de copia", an: "Carpeta de copia", oc: "Carpeta de còpia", ast: "Carpeta de copia", ca: "Carpeta de còpia", eu: "Kopia karpeta", ext: "Carpeta de copia", gl: "Carpeta de copia", en: "Backup folder"),
        ["backup_saved"] = Tr("Copia de seguridad configurada.", an: "Copia de seguridat configurada.", oc: "Còpia de seguretat configurada.", ast: "Copia de seguridá configurada.", ca: "Còpia de seguretat configurada.", eu: "Segurtasun kopia konfiguratua.", ext: "Copia de seguridá configurá.", gl: "Copia de seguridade configurada.", en: "Backup configured."),
        ["btn_save_backup"] = Tr("Guardar copia de seguridad", an: "Guardar copia de seguridat", oc: "Guardar còpia de seguretat", ast: "Guardar copia de seguridá", ca: "Desar còpia de seguretat", eu: "Segurtasun kopia gorde", ext: "Guardal copia de seguridá", gl: "Gardar copia de seguridade", en: "Save backup settings"),

        // === Idioma ===
        ["language_title"] = Tr("Idioma", an: "Idioma", oc: "Lengua", ast: "Idioma", ca: "Idioma", eu: "Hizkuntza", ext: "Ioma", gl: "Idioma", en: "Language"),
        ["language_desc"] = Tr("Cambia el idioma de la interfaz. Se aplica de inmediato.", an: "Cambia l'idioma de l'interfaz. S'aplica de inmediato.", oc: "Cambia la lengua dera interfaz. S'aplòque immediatament.", ast: "Cambia l'idioma de la interfaz. Aplícase de siguida.", ca: "Canvia l'idioma de la interfície. S'aplica immediatament.", eu: "Interfazearen hizkuntza aldatzen du. Berehala aplikatzen da.", ext: "Cambia el ioma de la interfaz. S'aplica de inmediatu.", gl: "Cambia o idioma da interface. Aplícase de inmediato.", en: "Change the interface language. Applied immediately."),

        // === Tema / Apariencia ===
        ["theme_title"] = Tr("Apariencia", an: "Apariencia", oc: "Aparéncia", ast: "Apariencia", ca: "Aparença", eu: "Itxura", ext: "Apariencia", gl: "Aparencia", en: "Appearance"),
        ["theme_desc"] = Tr("Elige el tema visual de la aplicación.", an: "Esfo l'aparencia visual de l'aplicación.", oc: "Causís era aparéncia visuala dera aplicacion.", ast: "Escueye'l tema visual de l'aplicación.", ca: "Tria el tema visual de l'aplicació.", eu: "Aukeratu aplikazioaren itxura bisuala.", ext: "Elige el tema visual de la aplicaión.", gl: "Escolle o tema visual da aplicación.", en: "Choose the visual theme of the app."),
        ["theme_light"] = Tr("Claro", an: "Claro", oc: "Clar", ast: "Claru", ca: "Clar", eu: "Argia", ext: "Claru", gl: "Claro", en: "Light"),
        ["theme_dark"] = Tr("Oscuro", an: "Oscuro", oc: "Escur", ast: "Escuru", ca: "Fosc", eu: "Iluna", ext: "Escuru", gl: "Escuro", en: "Dark"),
        ["theme_system"] = Tr("Seguir sistema", an: "Seguir sistema", oc: "Seguir sistèma", ast: "Siguir sistema", ca: "Seguir sistema", eu: "Sistemaren arabera", ext: "Seguil sistema", gl: "Seguir sistema", en: "Follow system"),

        // === PAGINA HISTORIAL ===
        ["history_title"] = Tr("Archivo", an: "Archibo", oc: "Archiu", ast: "Archivu", ca: "Arxiu", eu: "Artxiboa", ext: "Archivu", gl: "Arquivo", en: "Archive"),
        ["history_header"] = Tr("Archivo de facturas", an: "Archibo de facturas", oc: "Archiu de factures", ast: "Archivu de factures", ca: "Arxiu de factures", eu: "Fakturen artxiboa", ext: "Archivu de faturas", gl: "Arquivo de facturas", en: "Invoice archive"),
        ["history_hint"] = Tr("Toca una factura para ver los detalles.", an: "Toca una factura pa veyer os detalles.", oc: "Tòca ua factura entà véder es detalls.", ast: "Toca una factura pa ver los detalles.", ca: "Toca una factura per veure els detalls.", eu: "Sakatu faktura bat xehetasunak ikusteko.", ext: "Toca una fatura pa vel los detallis.", gl: "Toca unha factura para ver os detalles.", en: "Tap an invoice to view details."),
        ["history_empty"] = Tr("No hay facturas guardadas", an: "No bi ha facturas guardadas", oc: "Non i a factures guardades", ast: "Nun hai factures guardaes", ca: "No hi ha factures desades", eu: "Ez dago faktura gordeta", ext: "No hay faturas guardás", gl: "Non hai facturas gardadas", en: "No saved invoices"),
        ["history_empty_hint"] = Tr("Ve a la pestaña 'Analizar' y procesa una factura.\nSe guardara aqui automaticamente.", an: "Ves ta la pestaña 'Analisar' y procesa una factura.\nSe guardará aqui automaticament.", oc: "Vòi entara pestanha 'Analisar' e procèssa ua factura.\nSe guardarà açí automaticament.", ast: "Vete a la pestaña 'Analizar' y procesa una factura.\nGuardaráse equí automáticamente.", ca: "Ves a la pestanya 'Analitzar' i processa una factura.\nEs guardarà aquí automàticament.", eu: "Joan 'Aztertu' fitxara eta prozesatu faktura bat.\nHemen automatikoki gordeko da.", ext: "Vel a la pestaña 'Analizal' i procesa una fatura.\nSe guardará aquí automáticamente.", gl: "Vai á pestana 'Analizar' e procesa unha factura.\nGardarase aquí automaticamente.", en: "Go to the 'Analyze' tab and process an invoice.\nIt will be saved here automatically."),
        ["delete_confirm_msg"] = Tr("¿Eliminar la factura", an: "¿Eliminar a factura", oc: "Eliminar la factura", ast: "¿Desaniciar la factura", ca: "Eliminar la factura", eu: "Faktura ezabatu", ext: "¿Eliminal la fatura", gl: "Eliminar a factura", en: "Delete invoice"),

        // === PAGINA DETALLE ===
        ["detail_title"] = Tr("Detalle de Factura", an: "Detalle de Factura", oc: "Detall dera Factura", ast: "Detalle de Factura", ca: "Detall de Factura", eu: "Fakturaren Xehetasuna", ext: "Detalli de Fatura", gl: "Detalle de Factura", en: "Invoice Detail"),
        ["provider_label"] = Tr("Proveedor", an: "Proveedor", oc: "Òrnòr", ast: "Proveedor", ca: "Proveïdor", eu: "Hornitzailea", ext: "Proveol", gl: "Provedor", en: "Vendor"),
        ["invoice_num_label"] = Tr("N. Factura", ca: "N. Factura", eu: "Faktura Zk.", en: "Invoice #"),
        ["date_label"] = Tr("Fecha", an: "Calendata", oc: "Data", ast: "Fecha", ca: "Data", eu: "Data", ext: "Fecha", gl: "Data", en: "Date"),
        ["total_label"] = Tr("Total", eu: "Guztira", en: "Total"),
        ["btn_back"] = Tr("Volver", an: "Tornar", oc: "Tornar", ast: "Volver", ca: "Tornar", eu: "Itzuli", ext: "Golvel", gl: "Volver", en: "Back"),
        ["btn_share"] = Tr("Compartir", an: "Compartir", oc: "Compartir", ast: "Compartir", ca: "Compartir", eu: "Partekatu", ext: "Compartil", gl: "Compartir", en: "Share"),
        ["invoice_not_found"] = Tr("No se encontro la factura.", ast: "Nun s'atopó la factura.", ca: "No s'ha trobat la factura.", eu: "Faktura ez da aurkitu.", gl: "Non se atopou a factura.", en: "Invoice not found."),
    };
}
