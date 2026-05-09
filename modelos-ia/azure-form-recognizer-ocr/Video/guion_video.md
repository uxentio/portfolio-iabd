# Guion Video - Tarea 7

SCROLL LOCK = empezar/parar grabacion
PAUSE = pausar/reanudar (usalo sin miedo)

---

## INTRO

(Visual Studio 2022 abierto con el proyecto FacturasOCR)

"Buenas, voy a ensenar la tarea 7. Es una app .NET MAUI que usa
Azure Document Intelligence para extraer datos de facturas.
Primero enseno el codigo y luego la demo."

---

## 1. ESTRUCTURA DEL PROYECTO

(Muestra el Explorador de Soluciones)

"El proyecto se llama FacturasOCR. Tiene la pantalla principal
PaginaPrincipal, tres paginas en Paginas (Historial, Detalle y
Ajustes), tres servicios en Servicios (Azure, base de datos e
idiomas) y el modelo de datos en Modelos."

---

## 2. SERVICIO DE AZURE

(Abre Servicios/ServicioAnalisis.cs, ve a linea 11)

"Este es el servicio que conecta con Azure. Aqui estan el
endpoint y la API key por defecto del recurso que he creado."

(Baja a linea 16)

"En el constructor se crea el DocumentAnalysisClient con la URI
y la AzureKeyCredential, igual que en el ejemplo de clase pero
metido en un servicio separado."

(Baja a linea 29)

"AnalizarDocumentoAsync es el metodo principal. Llama a
AnalyzeDocumentAsync con el modelo prebuilt-invoice, que esta
optimizado para facturas. En el ejemplo del profesor se usa
prebuilt-document que es generico, pero este detecta campos
especificos como VendorName o InvoiceTotal."

---

## 3. PAGINA PRINCIPAL - INTERFAZ

(Abre PaginaPrincipal.xaml, ve a linea 23)

"La interfaz tiene tres botones arriba: Tomar Foto (con la
camara), Elegir Archivo (del sistema de archivos) y Procesar
Lote (varios archivos a la vez)."

(Baja a linea 73)

"Aqui esta la ficha visual que muestra el resumen de la factura:
proveedor, numero de factura, fecha y total. Se rellena
automaticamente cuando Azure termina de analizar."

(Baja a linea 119)

"Y abajo un Editor de solo lectura con todos los datos
completos del OCR: pares clave-valor, campos del documento,
lineas de texto y tablas."

---

## 4. PAGINA PRINCIPAL - PROCESAMIENTO

(Abre PaginaPrincipal.xaml.cs, ve a linea 260)

"ProcesarConOCR es el metodo que se llama cuando eliges una
imagen o PDF. Abre el stream del archivo, llama al servicio
de Azure, y cuando recibe el AnalyzeResult lo formatea con
FormatearResultado y extrae los campos con ExtraerCampo."

(Baja a linea 522)

"ExtraerCampo es donde busco cada dato de la factura. Primero
mira en Documents[].Fields, que son los campos que Azure detecta
automaticamente del modelo prebuilt-invoice."

(Baja a linea 537)

"Si no lo encuentra ahi, ExtraerKeyValue busca en los pares
clave-valor. Compara las claves con palabras como 'total',
'importe total', 'amount due', etc. Es lo mismo que
ShowKeyValuePairsSummary del ejemplo de clase pero buscando
campos concretos."

(Baja a linea 588)

"ExtraerProveedor busca el nombre del proveedor. Primero
en el campo VendorName, luego en los pares clave-valor con
palabras como 'empresa', 'emisor', 'vendor', 'company'."

"Este sistema de fallback en cascada hace que funcione con
cualquier tipo de factura, no solo con las que Azure reconoce
bien."

---

## 5. FORMATEO DEL RESULTADO

(Ve a linea 687 en PaginaPrincipal.xaml.cs)

"FormatearResultado coge el AnalyzeResult entero y lo convierte
a texto plano. Muestra los pares clave-valor, los campos del
documento con su tipo y confianza, las lineas de cada pagina
y las tablas. Es equivalente a las funciones Show del ejemplo
de clase: ShowKeyValuePairsSummary, ShowEntitiesSummary,
ShowLayoutAndMarksSummary y ShowTablesSummary."

---

## 6. PROCESAMIENTO XML

(Ve a linea 321 en PaginaPrincipal.xaml.cs)

"Si el archivo es un XML de factura electronica FacturaE, no
hace falta Azure. ProcesarXML parsea las etiquetas directamente:
RazonSocial, NumeroFactura, FechaExpedicion y TotalFactura."

---

## 7. PROCESAMIENTO POR LOTES

(Ve a linea 121 en PaginaPrincipal.xaml.cs)

"OnBatchClicked permite seleccionar varios archivos a la vez.
Los procesa uno por uno, detecta duplicados automaticamente
comparando el nombre y el contenido, y al final muestra un
resumen."

---

## 8. GUARDADO AUTOMATICO

(Ve a linea 415 en PaginaPrincipal.xaml.cs)

"GuardarAutomatico se llama despues de cada procesamiento.
Copia el archivo original a la carpeta de datos, comprueba
que no sea un duplicado con FindDuplicateAsync y guarda el
resultado en SQLite."

---

## 9. MODELO DE DATOS

(Abre Modelos/ResultadoFactura.cs, ve a linea 6)

"ResultadoFactura es la tabla de SQLite. Tiene el atributo
[Table("InvoiceResult")] para que la tabla se llame siempre
igual. Los campos son: Id, fecha de analisis, ruta de la
imagen, texto completo del OCR, nombre del archivo y los
cuatro campos principales: proveedor, numero, fecha y total."

(Senala linea 18)

"Los guardo como string porque Azure devuelve las fechas y
los importes en formatos distintos segun el idioma de la
factura."

---

## 10. SERVICIO DE BASE DE DATOS

(Abre Servicios/ServicioBaseDatos.cs, ve a linea 40)

"SaveInvoiceAsync guarda o actualiza una factura. Si el Id
es 0 hace INSERT, si no UPDATE."

(Baja a linea 73)

"FindDuplicateAsync busca duplicados comparando el nombre
de archivo y los primeros 200 caracteres del texto. Asi no
se guarda la misma factura dos veces."

---

## 11. SISTEMA MULTIIDIOMA

(Abre Servicios/ServicioIdiomas.cs, ve a linea 26)

"ServicioIdiomas tiene el metodo T que devuelve la traduccion
de una clave segun el idioma actual. Soporta 9 idiomas:
castellano, ingles, catalan, euskara, gallego, aragones,
aranes, asturiano y extremeno."

(Ve a linea 41)

"Cuando se cambia el idioma se lanza el evento IdiomaChanged
y todas las paginas lo escuchan para actualizar sus textos
al momento."

(Abre AppShell.xaml.cs, ve a linea 15)

"Aqui por ejemplo, AppShell se suscribe al evento y actualiza
los titulos de las pestanas."

---

## 12. AJUSTES Y TEMA

(Abre Paginas/PaginaAjustes.xaml.cs, ve a linea 78)

"AplicarTema cambia el tema visual: Claro, Oscuro o Seguir
sistema. Usa Application.Current.UserAppTheme y se guarda
en las preferencias para que se aplique al arrancar."

(Ve a linea 46)

"CargarPickerIdioma rellena el selector de idioma con los
9 idiomas disponibles."

---

## 13. DEMO - PANTALLA PRINCIPAL

(Cierra Visual Studio. Ejecuta la app)

"Ahora la demo. Esta es la pantalla principal. Voy a elegir
una factura de ejemplo."

(Pulsa Elegir Archivo, selecciona una factura)

"Mientras procesa se ve el spinner y el mensaje 'Analizando
documento con Azure OCR'. Cuando termina sale la ficha con
los datos: proveedor, numero, fecha y total."

(Senala la ficha visual)

"Azure ha detectado IBA International, factura 2019/11,
fecha 02/11/2019 y total 1.250 euros."

(Haz scroll en el editor de texto)

"Y aqui abajo estan todos los datos completos que ha
devuelto Azure: los pares clave-valor, los campos del
documento con sus tipos y confianza, las lineas de texto
y las tablas."

---

## 14. DEMO - HISTORIAL

(Ve a la pestana Archivo)

"En el historial se ven las facturas guardadas. Si toco
una se abre el detalle."

(Toca la factura)

"Aqui se ve la imagen original, los campos extraidos y el
texto completo. Puedo compartir o eliminar."

---

## 15. DEMO - AJUSTES

(Ve a la pestana Ajustes)

"En Ajustes se puede cambiar el endpoint y la API key de
Azure, el tema visual y el idioma."

(Cambia el idioma a Euskara)

"Si cambio a euskara se traduce todo al momento: las
pestanas, los botones, los textos. Sin reiniciar."

(Cambia de vuelta a Castellano)

---

## 16. CIERRE

"En resumen: la app usa Azure Document Intelligence con el
modelo prebuilt-invoice para extraer datos de facturas. Tiene
un sistema de fallback en cascada basado en las funciones
Show del ejemplo de clase, base de datos SQLite, soporte
para 9 idiomas y cambio de tema. Y eso seria todo. Gracias."

---

## ANTES DE GRABAR

- Cierra notificaciones
- Guion en el otro monitor
- App compilada y lista para ejecutar
- Factura de prueba preparada

### Pestanas abiertas en Visual Studio (de izquierda a derecha):

1. ServicioAnalisis.cs         → posicionar en linea 11
2. PaginaPrincipal.xaml        → posicionar en linea 23
3. PaginaPrincipal.xaml.cs     → posicionar en linea 260
4. ResultadoFactura.cs         → posicionar en linea 6
5. ServicioBaseDatos.cs        → posicionar en linea 40
6. ServicioIdiomas.cs          → posicionar en linea 26
7. AppShell.xaml.cs            → posicionar en linea 15
8. PaginaAjustes.xaml.cs       → posicionar en linea 78

### Lineas importantes por archivo (para navegar rapido con Ctrl+G):

**ServicioAnalisis.cs:**
- L11: endpoint y API key
- L16: constructor (crea el client)
- L29: AnalizarDocumentoAsync (llama a Azure)

**PaginaPrincipal.xaml:**
- L23: botones (Tomar Foto, Elegir Archivo, Procesar Lote)
- L73: ficha visual (resumen factura)
- L119: editor texto completo OCR

**PaginaPrincipal.xaml.cs:**
- L121: OnBatchClicked (lotes)
- L260: ProcesarConOCR (metodo principal)
- L321: ProcesarXML (factura electronica)
- L415: GuardarAutomatico
- L522: ExtraerCampo (Fields)
- L537: ExtraerKeyValue (pares clave-valor)
- L588: ExtraerProveedor (busca vendor)
- L687: FormatearResultado (texto completo)

**ResultadoFactura.cs:**
- L6: [Table("InvoiceResult")]
- L10-21: campos del modelo

**ServicioBaseDatos.cs:**
- L40: SaveInvoiceAsync
- L73: FindDuplicateAsync

**ServicioIdiomas.cs:**
- L26: metodo T() (traduccion)
- L41: evento IdiomaChanged
- L68: diccionario de traducciones

**AppShell.xaml.cs:**
- L15: suscripcion a IdiomaChanged

**PaginaAjustes.xaml.cs:**
- L46: CargarPickerIdioma
- L78: AplicarTema
