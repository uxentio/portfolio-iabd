# Guion Video - Tarea 5 RAG

SCROLL LOCK = empezar/parar grabacion
PAUSE = pausar/reanudar (usalo sin miedo)

---

## INTRO

(Pantalla con Visual Studio abierto)

"Buenas, voy a ensenar la tarea 5. App en .NET MAUI que se conecta
con AnythingLLM y LM Studio para hacer consultas RAG (Retrieval-Augmented
Generation, basicamente buscar en documentos y responder con esa info).
Primero codigo, luego demo."

---

## 1. ESTRUCTURA Y MVVM

(Muestra el Explorador de Soluciones)

"El proyecto sigue el patron MVVM. Tengo estas carpetas:
- Modelos: las clases de datos (WorkspaceItem, DocumentoItem, MensajeChat, ChunkInfo)
- ViewModels: la logica de cada pantalla (ChatViewModel, WorkspacesViewModel, etc.)
- Pages: las vistas XAML
- Servicios: ApiService para la API, ImageProcessorService para imagenes
  y PythonProcessorService para preprocesar PDFs y videos de YouTube

La app tiene 4 pestanas con iconos: Chat, Workspaces, Documentos y Config."

(Abre AppShell.xaml, linea 11)

"Aqui en AppShell defino las 4 pestanas con TabBar. Cada ShellContent
apunta a su pagina."

(Abre BaseViewModel.cs)

"BaseViewModel es la clase base. Implementa INotifyPropertyChanged
para que la interfaz se actualice cuando cambian los datos.
El metodo SetProperty compara el valor nuevo con el viejo y solo
notifica si cambian, asi no se actualiza por gusto."

---

## 2. APISERVICE - WORKSPACES

(Abre ApiService.cs, ve a linea 8)

"ApiService es una clase estatica con todos los metodos que llaman
a la API de AnythingLLM. Tiene 3 propiedades: BaseUrl, ApiKey y
SystemPrompt, que se cambian desde la pantalla de Config."

(Baja a linea 16)

"GetClient crea un HttpClient con el token Bearer para que la API
acepte las peticiones."

(Baja a linea 26)

"ObtenerWorkspaces hace un GET a /v1/workspaces y devuelve la lista."

(Baja a linea 36)

"CrearWorkspace hace un POST a /v1/workspace/new con el nombre en JSON."

(Baja a linea 50)

"RenombrarWorkspace hace POST a /v1/workspace/{slug}/update."

(Baja a linea 61)

"EliminarWorkspace hace DELETE a /v1/workspace/{slug}."

---

## 3. APISERVICE - DOCUMENTOS

(Ve a linea 70 de ApiService.cs)

"SubirDocumento usa MultipartFormDataContent para enviar el fichero
a /v1/document/upload. Lee los bytes y los mete en el form."

(Baja a linea 86)

"Si la subida va bien, devuelvo documents[0] con su location
(la ruta interna en AnythingLLM)."

(Baja a linea 91)

"ActualizarEmbeddings hace POST a /v1/workspace/{slug}/update-embeddings.
Le paso la location del documento. Esto genera los vectores para
que el RAG pueda buscar en ese documento."

(Baja a linea 117, EliminarDocumentos)

"EliminarDocumentos usa un DELETE con body para borrar documentos
del sistema. Es un SendAsync porque DELETE con cuerpo necesita
construir el HttpRequestMessage a mano."

---

## 4. APISERVICE - CHAT

(Ve a linea 223 de ApiService.cs, EnviarMensaje)

"EnviarMensaje recibe el slug del workspace, el mensaje, el modo
(chat o query) y el sessionId. Armo el payload con un Dictionary
y si hay SystemPrompt lo anado tambien."

"Hace POST a /v1/workspace/{slug}/chat y deserializa la respuesta.
La respuesta trae un textResponse con la contestacion del modelo
y un sources con los chunks que ha usado."

---

## 5. IMAGEPROCESSORSERVICE

(Abre ImageProcessorService.cs)

"Esta clase procesa imagenes para meterlas en el RAG. AnythingLLM
no acepta imagenes directamente, asi que las convierto a texto."

(Baja a linea 27, ProcesarImagen)

"ProcesarImagen hace varias cosas: saca la info del archivo,
extrae los metadatos EXIF con MetadataExtractor, luego llama
al modelo de vision de LM Studio para que describa la imagen,
y por ultimo hace OCR para detectar texto."

"Lo de la descripcion es lo mas interesante. Convierte la imagen
a base64, la manda a LM Studio por la API de chat con el formato
de vision de OpenAI, y el modelo devuelve una descripcion en
texto de lo que ve. Asi el RAG puede responder preguntas tipo
'que se ve en la foto' o 'hay personas en la imagen'."

(Baja a linea 178, ExtraerTextoOCR)

"El OCR usa la API de Windows que viene con el sistema. Esta
compilado con #if WINDOWS. Abre la imagen y extrae el texto."

(Baja a linea 206, GuardarComoTexto)

"Todo se junta en un .txt con secciones: info del archivo,
EXIF, descripcion de la IA y OCR. Se sube a AnythingLLM como
documento normal."

---

## 6. PYTHONPROCESSORSERVICE

(Abre PythonProcessorService.cs)

"Esta es la clase nueva que he hecho para integrar los scripts
de Python dentro de la app. Sigue el mismo patron que
ImageProcessorService pero en vez de procesar imagenes, llama
a scripts de Python para preprocesar PDFs y videos de YouTube."

(Senala lineas 10-11, propiedades ScriptsPath y PythonExePath)

"Tiene dos propiedades estaticas: ScriptsPath, que es la carpeta
donde estan los scripts .py, y PythonExePath, que es la ruta
del ejecutable de Python. Las dos se configuran desde la
pestana Config."

(Baja a lineas 13 y 19, EsPdf y EsUrlYouTube)

"EsPdf comprueba si el archivo es un PDF por la extension.
EsUrlYouTube detecta si una URL es de YouTube, acepta
varios formatos: youtube.com/watch, youtu.be, shorts, etc."

(Baja a linea 27, ProcesarPdf)

"ProcesarPdf llama al script segmentar_pdf_por_pagina.py
pasandole la ruta del PDF. El script extrae el texto pagina
a pagina y mete [Pagina XX] al inicio de cada linea. Devuelve
la ruta del .txt generado."

(Baja a linea 47, ProcesarYouTube)

"ProcesarYouTube hace lo mismo pero con el script de YouTube.
Primero extrae el ID del video de la URL, luego llama al
script transcribir_video_youtube.py pasandole la URL y el
idioma. Devuelve la ruta del .txt con la transcripcion."

(Baja a linea 95, EjecutarPython)

"EjecutarPython es el metodo que realmente ejecuta Python.
Usa Process.Start con RedirectStandardOutput y StandardError.
Si el script falla, lanza excepcion con el stderr para que
el usuario vea el error en la app."

---

## 7. CONFIGVIEWMODEL

(Abre ConfigViewModel.cs, lineas 8-48)

"El ViewModel de Config tiene las propiedades BaseUrl, ApiKey,
SystemPrompt, y ahora tambien ScriptsPath y PythonExePath
para los scripts de Python."

(Ve a linea 80, CargarPreferencias)

"Todo se guarda y carga de Preferences."

(Ve a linea 91, Guardar)

"Al guardar, actualiza tanto las propiedades de ApiService
como las de PythonProcessorService."

(Ve a linea 112, ProbarConexion)

"ProbarConexion intenta hacer un GET a la API y muestra si la
conexion es correcta o no. Util para verificar antes de empezar."

---

## 8. WORKSPACESVIEWMODEL

(Abre WorkspacesViewModel.cs, linea 11)

"WorkspacesViewModel tiene una ObservableCollection de WorkspaceItem."

(Ve a linea 29, CargarWorkspaces)

"CargarWorkspaces llama a la API, deserializa con dynamic y rellena
la coleccion. La interfaz se actualiza sola por el binding."

(Ve a lineas 54, 73, 84)

"CrearWorkspace, RenombrarWorkspace y EliminarWorkspace llaman a
ApiService y recargan la lista."

---

## 9. DOCUMENTOSVIEWMODEL

(Abre DocumentosViewModel.cs)

"DocumentosViewModel maneja la subida de archivos. Tiene tres
flujos de procesamiento segun el tipo de archivo:"

(Ve a linea 210, SubirDocumento)

(Ve a linea 223, la rama de imagen)

"Si es una imagen, la procesa con ImageProcessorService igual
que antes: EXIF, vision, OCR, genera un .txt."

(Ve a linea 234, la rama de PDF)

"Si es un PDF y el usuario ha marcado el checkbox 'Procesar
con marcas de pagina', llama a PythonProcessorService.ProcesarPdf
que ejecuta el script de Python. Si no marca el checkbox, el
PDF se sube directamente tal cual."

(Ve a linea 325, ProcesarYSubirYouTube)

"Y aqui tengo ProcesarYSubirYouTube, que es el metodo nuevo.
Recibe la URL de YouTube, llama a PythonProcessorService.ProcesarYouTube,
y sube la transcripcion generada al workspace. Todo automatico."

"Tambien tiene la logica de seleccion con checkboxes para poder
eliminar documentos marcados."

---

## 10. CHATVIEWMODEL Y MAINPAGE

(Abre ChatViewModel.cs, lineas 16-18)

"ChatViewModel tiene ObservableCollections para los Mensajes y
los Chunks."

(Ve a linea 93, EnviarMensaje)

"EnviarMensaje llama a la API y anade los mensajes
a la coleccion, la interfaz los muestra automaticamente."

(Ve a lineas 101-103)

"El truco de los modos: si es Chat, el sessionId se mantiene.
Si es Query, se genera uno nuevo cada vez. Asi en Query cada
pregunta es independiente."

(Abre MainPage.xaml)

"La interfaz usa CollectionView con DataTemplate para los mensajes
y los chunks. Binding a las propiedades del ViewModel."

(Senala lineas 53-88, la trazabilidad)

"Los chunks se muestran en un panel oscuro redimensionable.
Se puede arrastrar el handle para hacerlo mas grande o pequeno.
Cada chunk se puede tocar para expandirlo y ver el texto completo."

---

## 11. DEMO - ARRANQUE

(Deja Visual Studio. Muestra LM Studio con el servidor)

"Ahora la demo. LM Studio corriendo con el modelo cargado y
el servidor local activo en el puerto 1234."

(Muestra AnythingLLM abierto)

"AnythingLLM configurado para usar LM Studio como proveedor
de LLM y embeddings."

(Ejecuta la app)

"Arranco la app de MAUI."

---

## 12. DEMO - CONFIG

(En la app, ve a la pestana Config)

"Primero la configuracion. Pongo la URL base de AnythingLLM,
pego la API key y pongo un system prompt."

(Senala los campos de Python)

"Aqui abajo estan los campos nuevos de Python: la ruta donde
tengo los scripts .py y el ejecutable de Python. Esto es para
que la app pueda llamar a los scripts automaticamente cuando
subo un PDF o un video de YouTube."

"Le doy a Probar Conexion para verificar que conecta bien.
Sale verde, perfecto. Guardo."

---

## 13. DEMO - WORKSPACES

(Ve a la pestana Workspaces)

"Aqui se ven los workspaces que ya existen en AnythingLLM.
Puedo crear uno nuevo, renombrarlo o eliminarlo."

(Crear un workspace si no existe)

---

## 14. DEMO - SUBIR DOCUMENTOS

(Ve a la pestana Documentos)

"Selecciono el workspace, pulso Seleccionar Archivo, elijo el
PDF de Historial de empleados. Le doy a Subir y Procesar."

(Esperar a que suba y muestre verde)

"Se ve el mensaje naranja 'Subiendo...' y luego verde cuando
termina. Ahora el PDF esta en el workspace con sus embeddings."

(Repetir con el CSV si quieres)

---

## 15. DEMO - SUBIR PDF CON MARCAS DE PAGINA

(Ve a la pestana Documentos)

"Ahora voy a subir un PDF pero con el preprocesado de paginas.
Selecciono un PDF..."

(Seleccionar un PDF - se ve que aparece "PDF detectado" y el checkbox)

"Se ve que detecta que es un PDF y aparece el checkbox
'Procesar PDF con marcas [Pagina XX]'. Si lo marco, la app
va a llamar al script de Python que extrae el texto pagina
a pagina y mete [Pagina XX] en cada linea. Si no lo marco,
se sube el PDF tal cual."

(Marcar el checkbox y pulsar Subir y Procesar)

"Le doy a Subir y Procesar. Se ve 'Procesando PDF con marcas...'
en naranja. Esta ejecutando el script de Python por detras
con Process.Start. Cuando termina, sube el .txt generado
y actualiza los embeddings. Verde."

---

## 16. DEMO - SUBIR IMAGEN

(Ve a la pestana Documentos)

"Ahora subo una imagen. Selecciono un JPG. Se ve que detecta
que es una imagen. Le doy a Subir y Procesar."

(Esperar al procesamiento - puede tardar un poco por el modelo de vision)

"Primero dice 'Procesando imagen...' porque esta sacando los
metadatos EXIF, pidiendo al modelo de vision de LM Studio que
describa lo que ve, y haciendo OCR. Tarda un poco mas que un
documento normal porque el modelo tiene que analizar la imagen.
Luego sube el .txt generado y actualiza los embeddings. Verde."

---

## 17. DEMO - PROCESAR VIDEO DE YOUTUBE

(Ve a la pestana Documentos, baja a la seccion de YouTube)

"Ahora lo del video de YouTube. Aqui abajo hay una seccion
para pegar una URL de YouTube."

(Pegar la URL: https://www.youtube.com/watch?v=SI7O81GMG2A)

"Pego la URL del video. Pulso 'Procesar y Subir'."

(Esperar a que procese)

"Se ve 'Descargando subtitulos de YouTube...' La app esta
llamando al script de Python que descarga los subtitulos
con youtube-transcript-api, los agrupa en bloques de 30
segundos y les pone marcas [Minuto XX:XX - YY:YY].
Cuando termina, sube la transcripcion al workspace y
actualiza los embeddings. Todo automatico, sin tocar
la terminal. Verde."

---

## 18. DEMO - CHAT CON PDF

(Ve a la pestana Chat, selecciona el workspace del PDF)

"Selecciono el workspace donde subi el PDF. Modo Chat."

(Escribe: Quien es el empleado con mas experiencia?)

"Pregunto quien tiene mas experiencia. Se ve la respuesta
con la hora, y abajo en trazabilidad aparece el chunk con
el documento, el texto y el score."

(Toca un chunk para expandirlo)

"Si toco un chunk se expande y puedo ver el texto completo.
Lo toco otra vez y se contrae."

(Escribe: Y en que se ha especializado?)

"Hago una pregunta de seguimiento. Como estoy en modo Chat,
mantiene el contexto y sabe de quien hablo."

---

## 19. DEMO - QUERY CON CSV

(Cambia al workspace del CSV, selecciona modo Query)

"Ahora cambio al workspace del CSV y pongo modo Query."

(Escribe: Cual es el salario mas alto?)

"En Query cada pregunta es independiente. Se ve en la
trazabilidad que el chunk viene del CSV."

---

## 20. DEMO - TRAZABILIDAD

(Senala la seccion de trazabilidad)

"Lo importante es la trazabilidad. Para cada respuesta se ve:
el documento de donde viene, el trozo de texto que ha usado,
y el score de similitud."

(Arrastra el handle para redimensionar)

"El panel se puede hacer mas grande arrastrando desde aqui."

(Toca chunks para expandir/contraer)

"Y los chunks se pueden expandir para ver el texto entero.
Si pregunto sobre el video de YouTube, se ven las marcas
[Minuto XX:XX] en los chunks. Y si pregunto sobre los apuntes
de Java, se ven las marcas [Pagina XX]. Asi siempre sabes
de donde viene la informacion."

---

## 21. CIERRE

"Y eso seria todo. Resumiendo: app MAUI con patron MVVM, 4
pestanas, se conecta a AnythingLLM por API REST, gestiona
workspaces, sube documentos con embeddings, procesa imagenes
con modelo de vision, OCR y EXIF, tiene preprocesado integrado
de PDFs con marcas de pagina y transcripcion de videos de YouTube,
modo Chat con contexto y modo Query sin contexto, y trazabilidad
con chunks expandibles y panel redimensionable.
Gracias."

---

## ANTES DE GRABAR

- LM Studio con servidor arrancado y modelo cargado
- AnythingLLM corriendo (localhost:3001)
- Python 3 instalado con youtube-transcript-api y PyPDF2
- Visual Studio con las pestanas de codigo abiertas:
  - AppShell.xaml
  - BaseViewModel.cs
  - ApiService.cs
  - ImageProcessorService.cs
  - PythonProcessorService.cs
  - ConfigViewModel.cs
  - WorkspacesViewModel.cs
  - DocumentosViewModel.cs
  - ChatViewModel.cs
  - MainPage.xaml
- Tener el PDF, el CSV y una imagen a mano para subirlos en la demo
- Tener una URL de YouTube a mano (ej: https://www.youtube.com/watch?v=SI7O81GMG2A)
- Ruta de los scripts configurada en la pestana Config
- Cierra notificaciones
- Guion en el otro monitor
