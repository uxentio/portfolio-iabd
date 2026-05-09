# Guion del vídeo demo · Cosmic Briefing

Notas para mí, no para entregar. Pensado para 14-15 minutos siguiéndolo a rajatabla. Hablo en primera persona, frases cortas. El profesor pide que explique los nodos uno a uno y el código que tienen, así que entro en detalle en los `Code` y en el `Code.gs` del Apps Script.

---

## Antes de pulsar Grabar

### Comandos a lanzar antes (deja todo limpio)

> Esto en una PowerShell, **antes** de empezar a grabar.

**1. Arrancar el kit y parar Qdrant (que no uso):**

```powershell
cd C:\self-hosted-ai-starter-kit-main
docker compose up -d
docker stop qdrant
```

> El kit usa nombres internos para los servicios del compose, así que arranco todo y paro Qdrant después.

**2. Verificar que están los 3 contenedores que uso:**

```powershell
docker ps
```

Tienen que salir `n8n`, `ollama` y `postgres-1`. Sin Qdrant.

**3. Arrancar ngrok en otra PowerShell y dejarla abierta:**

```powershell
ngrok http 5678 --domain=tapping-widget-entering.ngrok-free.dev
```

**4. Verificar túnel:**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" | ConvertTo-Json -Depth 5
```

Tiene que devolver `public_url: https://tapping-widget-entering.ngrok-free.dev`.

**5. Una pasada de calentamiento del modelo:**

En n8n → Execute workflow desde el Schedule trigger una vez. Así Ollama carga el modelo en RAM y luego en cámara no tarda 30 s en frío.

**6. Borro el chat con el bot en Telegram** (menú → Eliminar chat) para que la demo se vea limpia.

**7. Mando un «Hola» al bot** para confirmar que responde antes de empezar. Si da 403, desactivo y reactivo el workflow en n8n.

### Pestañas del navegador en orden (de izquierda a derecha)

1. **n8n editor del workflow** → `http://localhost:5678/workflow/UCfHUxYvyeVrDHFP`
2. **Telegram Web** con el chat del bot Cosmic Briefing → `https://web.telegram.org/`
3. **Hoja de Sheets** «Cosmic Briefing»
4. **Panel HTML** → `https://script.google.com/macros/s/AKfycbxyxBY-ktwHwRxIDpdzS38CyVp7s-h7sJXN7QGONkiiOLCaAcvz2nr-qI3OcOJ0bG5MXQ/exec?action=dashboard`
5. **Editor de Apps Script** con `Code.gs` abierto

> n8n Executions no necesita pestaña aparte: es un botón dentro de n8n, cambias entre `Editor` y `Executions` en la barra superior.

### Otras ventanas

- **Docker Desktop** abierto, vista de Containers, con el toggle «Only show running containers» activado.
- **PowerShell con ngrok corriendo**, minimizada (no la cierro nunca). La enseño 5 segundos cuando hable de ngrok.
- **VSCode** con la carpeta `cosmic-briefing` abierta. Pestañas en VSCode:
  - `autor_readme.md`
  - `n8n/autor_workflow.json` (solo para enseñar que existe)
  - `google-apps-script/Code.gs`

### Lo que NO voy a mostrar en cámara

- API keys de Groq, Telegram, NASA.
- El `.env`.
- URLs largas pegadas a mano (las tengo en favoritos).

---

## Guion (14-15 min)

### 0:00 — 0:30 · Intro

**Pantalla**: portada con el título o cara mía.

> «Hola, soy autor, 1º de BDAT. Esta es la entrega de la Tarea de la Unidad 9 de Programación para IA. El proyecto se llama Cosmic Briefing. Os enseño qué hace, cómo está montado y una demo en directo».

### 0:30 — 1:30 · Qué es

**Pantalla**: VSCode con el README abierto en la sección 1.

> «Lo primero, qué hace esto. Es un workflow de n8n que cada mañana a las 8 me manda un mensaje de Telegram con lo que ha pasado en el espacio».

> «Cojo datos de 8 fuentes públicas: NASA APOD, la Estación Espacial Internacional, asteroides cercanos, próximos lanzamientos, condiciones del cielo, atardecer, papers de astrofísica de arXiv y noticias de SpaceNews».

> «Esos titulares pasan por un modelo de embeddings local, los agrupo por tema con un clustering, y le pido a un LLM que escriba un resumen en castellano».

> «Aparte tengo un chatbot del mismo bot de Telegram con el que puedo hablar y consultar los briefings antiguos. Tiene memoria, así que recuerda lo que le he preguntado antes».

> «No es un RAG. No hay vector store ni indexación de documentos. Lo que hago es mezclar 8 fuentes en directo, agruparlas por tema con clustering y narrarlas con un LLM».

### 1:30 — 2:30 · Los 4 contenedores del kit

**Pantalla**: ventana de Docker Desktop, vista de Containers.

> «Antes de meternos en el workflow, esto es lo que tengo corriendo en Docker. Uso el `self-hosted-ai-starter-kit`, que es un docker-compose con cuatro servicios. Os los presento uno a uno».

(Apunto a cada contenedor en la lista.)

> «**n8n**. Es el motor de automatización donde vive el workflow. Lo accedo en `http://localhost:5678`. Otros contenedores le hablan por su nombre interno, `n8n`».

> «**ollama**. Servidor local de modelos de lenguaje y embeddings. Lo uso para el briefing: los nodos de embeddings y de LLM le hablan por la red interna de Docker, en `http://ollama:11434`. Dentro de este contenedor están los dos modelos descargados, `qwen2.5:1.5b` y `nomic-embed-text`».

> «**postgres-1**. Es la base de datos que usa el propio n8n por dentro para guardar los workflows, las ejecuciones y las credenciales. No la toco yo desde mi código, pero n8n la necesita».

> «**qdrant**. Es una base de datos vectorial que el kit incluye por defecto pensada para hacer RAG. Yo no hago RAG, así que no la uso. La he parado a mano con `docker stop qdrant` para no malgastar RAM».

### 2:30 — 3:00 · ngrok como puente al exterior

**Pantalla**: PowerShell donde corre ngrok.

> «Y aquí en paralelo tengo ngrok corriendo. Veis la línea de Forwarding: la URL pública `tapping-widget-entering.ngrok-free.dev` apunta a mi `localhost:5678`. Eso es lo que permite que Telegram pueda mandarle mensajes al chatbot a mi n8n local».

> «Aquí abajo el log de HTTP Requests de los últimos mensajes que Telegram ha entregado a n8n: todos `200 OK`. Confirma que el túnel está vivo y el chatbot recibe bien».

### 3:00 — 9:00 · Recorrido del workflow nodo a nodo

**Pantalla**: navegador en n8n, pestaña Editor del workflow.

> «Aquí está el workflow entero. Como pedía el enunciado, va todo en un único fichero: `autor_workflow.json`».

(`Ctrl + 0` para hacer fit view. Se ve todo. Hago zoom in en la sticky de cabecera.)

> «Tiene tres ramas independientes, cada una con su propio trigger. Las separo en pantalla para que se vean mejor».

#### Rama A — Briefing diario

(Zoom in al lado izquierdo de la rama A.)

**Nodo 1 — Schedule 08:00 diario**

> «Empieza con un Schedule trigger con cron `0 8 * * *`, o sea, todos los días a las 8 de la mañana. No tiene código, solo el cron».

**Nodo 2 — Configuración (Code)**

(Doble clic en el nodo. Se abre el editor de código.)

> «Es un nodo Code de n8n. Devuelve un JSON con la configuración del briefing».

```javascript
return [{
  json: {
    lat: 37.608,
    lon: -0.987,
    ciudad: 'Cartagena, España',
    tono: 'divulgativo',
    hoy: new Date().toISOString().slice(0, 10)
  }
}];
```

> «`lat` y `lon` son mis coordenadas, las usa Open-Meteo y Sunrise-Sunset. `ciudad` aparece en el prompt y en el mensaje. `tono` da estilo al briefing. Y `hoy` es la fecha en formato ISO recortada a YYYY-MM-DD, la necesita la API de NeoWs».

(Cierro el modal.)

**Nodos 3 a 10 — 8 fuentes externas**

(Paso por encima rápido, nombrando cada uno.)

> «Después vienen los 8 nodos HTTP de las 8 fuentes externas, en cadena: NASA APOD para la imagen del día, Where-ISS para la posición de la Estación Espacial, NASA NeoWs para asteroides cercanos hoy, Launch Library 2 de TheSpaceDevs para los próximos tres lanzamientos, Open-Meteo para nubosidad, Sunrise-Sunset para el crepúsculo, arXiv RSS para papers de astrofísica y SpaceNews RSS para noticias».

> «Todos llevan `onError: continueRegularOutput`. Si una API se cae, las demás siguen y la consolidación se adapta sin romper el workflow».

**Nodo 11 — Consolidar datos (Code)**

(Doble clic. Se abre el editor de código grande.)

> «Aquí va el primer Code grande. Lo que hago es coger las salidas de las 8 APIs, parsearlas y dejar todo preparado para el embedding y el LLM».

> «Primero un helper para leer cada nodo de forma defensiva, así si un nodo no devolvió nada me da `{}` en lugar de petar».

```javascript
const getJson = (nodo) => {
  try { return $(nodo).first().json || {}; }
  catch(e) { return {}; }
};
```

> «Luego saco la imagen astronómica del día y la corto a 400 caracteres. Después la ISS: calculo la distancia en kilómetros entre la ISS y mi ciudad con la fórmula del haversine, y marco una bandera `sobre_zona` si está a menos de 2 000 km. Esto es 100 % JavaScript, sin dependencias».

```javascript
const dLat = toRad(iss.lat - ubic.lat);
const dLon = toRad(iss.lon - ubic.lon);
const hav = Math.sin(dLat/2)**2 + Math.cos(toRad(ubic.lat)) * Math.cos(toRad(iss.lat)) * Math.sin(dLon/2)**2;
iss.distancia_a_ti_km = Math.round(6371 * 2 * Math.atan2(Math.sqrt(hav), Math.sqrt(1-hav)));
```

> «Después extraigo los asteroides de NeoWs (nombre, diámetro medio, distancia en distancias lunares, si es peligroso), los lanzamientos de Launch Library 2 (nombre, cohete, fecha, sitio), las nubes nocturnas medias entre las 21 y las 3, y el crepúsculo astronómico».

> «Al final tengo un parser RSS sencillo con regex porque arXiv y SpaceNews vienen en XML. Solo extraigo el campo title de cada item».

> «Y junto todo en una lista plana de titulares prefijados con PAPER, NOTICIA, LANZAMIENTO o ASTEROIDE. Esa lista la mando al embedding».

(Cierro el modal.)

**Nodo 12 — Embeddings Ollama**

(Doble clic.)

> «Es un HTTP Request a `http://ollama:11434/api/embed`. El body manda el modelo `nomic-embed-text` y la lista de titulares. La respuesta es un array de vectores de 768 dimensiones, uno por titular. Esto NO usa credencial de n8n, llama directo por la red interna de Docker».

(Cierro.)

**Nodo 13 — Clustering y prompt (Code)**

(Doble clic.)

> «Segundo Code grande. Hace dos cosas: el clustering y construir el prompt».

> «El clustering es greedy: voy uno a uno por los titulares, calculo la similitud coseno con el centroide de cada cluster existente, y si supera 0,70 lo añado al cluster y recalculo el centroide. Si no, abro un cluster nuevo».

```javascript
function cos(a, b) {
  let dot=0, na=0, nb=0;
  for (let i=0; i<a.length; i++) { dot+=a[i]*b[i]; na+=a[i]*a[i]; nb+=b[i]*b[i]; }
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}
```

> «Después construyo el prompt para el LLM. Le paso reglas estrictas (que use solo los datos que le doy, que no invente, sin emojis ni asteriscos, máximo 9 frases) y los datos reales: APOD, ISS, asteroides, lanzamientos, condiciones del cielo y los grupos temáticos detectados. La gracia de meter los grupos en el prompt es que el LLM detecta que tres noticias hablan del mismo tema y no las repite tres veces».

(Cierro.)

**Nodo 14 — LLM Ollama (qwen2.5:1.5b)**

(Doble clic.)

> «Otro HTTP Request, esta vez a `http://ollama:11434/api/generate`. El body manda el modelo `qwen2.5:1.5b`, el prompt, `stream: false`, `keep_alive: 30m` para que el modelo se quede en RAM media hora, y `num_gpu: 0` para forzar CPU porque mi GPU no la soporta Ollama».

(Cierro.)

**Nodos 15 y 16 — Salidas Telegram y Sheets**

> «Al terminar el LLM, dos salidas en paralelo. El nodo 15 es un HTTP POST a la API de Telegram con el texto del briefing y el enlace al panel HTML. El nodo 16 es otro POST al endpoint del Apps Script con el JSON que se guarda en la hoja».

#### Rama B — Chatbot

(Zoom out, paso a la zona de la rama B.)

**Nodo 17 — Telegram Trigger (chatbot)**

> «Cuando le mando un mensaje al bot, este Telegram Trigger lo recibe. Está configurado para escuchar updates de tipo `message`. Al activar el workflow, n8n registra automáticamente el webhook con Telegram a través de la URL pública de ngrok».

**AI Agent**

> «Este es el nodo AI Agent de n8n. Tiene cuatro cosas enchufadas debajo».

> «Uno: el modelo. Aquí pongo Groq con `llama-3.3-70b-versatile`. Mi GPU no soporta Ollama y en CPU el tool calling es flojo, así que el chatbot va por Groq, que es API gratuita».

> «Dos: la memoria. Window Buffer de 6 turnos con `chat.id` como sessionKey, así cada usuario tiene su propio hilo».

> «Tres y cuatro: las dos tools. `ultimos_briefings(n)` hace un GET al Apps Script con `?action=last`. `buscar_briefing(q)` hace otro GET con `?action=search`. El propio LLM decide cuál llamar según lo que le pregunte el usuario».

> «Las descripciones de las tools están en castellano. El LLM las lee como parte del prompt para decidir cuál usar».

> «El system message del agente le explica cómo comportarse: castellano, máximo 6 frases, sin markdown, usar las tools si pregunta por algo del histórico, no inventar».

**Nodo 18 — Telegram (respuesta chatbot)**

> «Cuando el agente termina, este HTTP POST manda la respuesta al chat de Telegram, también con limpieza de asteriscos por si el modelo se ha pasado de markdown».

#### Rama C — Errores

> «La rama C es un Error Trigger global. Si cualquier nodo del workflow petara, este trigger se dispara y me llega un mensaje a Telegram con el error y el nodo que ha fallado».

### 9:00 — 10:00 · El Apps Script

**Pantalla**: pestaña del editor de Apps Script con `Code.gs`.

> «El Apps Script es la capa que hace de pegamento entre n8n y la hoja de Sheets, y además sirve el panel HTML».

(Hago scroll a `doPost`.)

```javascript
function doPost(e) {
  var raw = e.postData.contents;
  if (raw.charAt(0) === '=') raw = raw.substring(1);
  var datos = JSON.parse(raw);
  ...
  hoja.appendRow([c(datos.timestamp), c(datos.fecha), ...]);
}
```

> «`doPost` recibe el JSON del nodo 16 y añade una fila a la hoja. Hay un detalle: si el JSON viene con un `=` al principio (un bug de n8n con expresiones), lo strippeo. La función `c` también lo quita de cada valor para que Sheets no lo trate como fórmula y meta `#NAME?`».

(Hago scroll a `doGet`.)

```javascript
if (action === 'dashboard') return renderDashboard(datos);
if (action === 'search') {
  var filtradas = rows.filter(...);
  return respond({ ok: true, count: filtradas.length, rows: filtradas });
}
// por defecto: ?action=last
var ultimas = rows.slice(-n);
return respond({ ok: true, count: ultimas.length, rows: ultimas });
```

> «`doGet` mira el parámetro `action`. Si es `last` devuelve las últimas N filas, si es `search` filtra por palabra clave, si es `dashboard` llama a `renderDashboard` que monta un HTML con tarjetas».

> «`renderDashboard` recorre las filas y crea un `<article class="card">` por cada una con la imagen APOD, fecha, ciudad, tokens y el texto del briefing. La etiqueta amarilla "ISS sobre tu zona" sale solo si en esa fila el campo `ISS_Visible` es `SI`».

### 10:00 — 13:00 · Demo en directo

**Pantalla**: pestaña del editor de n8n.

> «Vale, vamos a verlo funcionando».

**Briefing diario manual**

> «Pulso "Execute workflow" desde el Schedule trigger para forzar el briefing en directo».

(Click. Espero. Voy narrando.)

> «Mientras corre, se va viendo cada nodo en verde. Pasa por las 8 APIs, consolida, embeddings, clustering, LLM (esto es lo que más tarda) y al final manda a Telegram y a Sheets».

(Cuando termina.)

(Cambio a Telegram.)

> «Aquí está el briefing. Tiene la imagen del día, ISS, asteroides cercanos, próximos lanzamientos, condiciones del cielo, papers, noticias y el enlace al panel».

(Click en el enlace.)

> «Y este es el dashboard. Cabecera con el contador de briefings, y debajo las tarjetas con cada uno».

(Cambio a Sheets.)

> «Y en Sheets tengo la nueva fila con todos los datos».

**Chatbot**

(Cambio a Telegram.)

> «Ahora pruebo el chatbot. Le mando "Hola"».

(Escribo «Hola».)

> «Saludo simple. El agente decide que no necesita tool y me contesta directamente».

(Espero respuesta.)

(Escribo «¿Qué dijo el último briefing?».)

> «Vamos a Executions en n8n mientras piensa».

(Cambio a Executions, abro la última ejecución.)

> «Aquí se ve cómo el AI Agent ha tirado de la tool `ultimos_briefings`, el modelo de Groq se ha llamado dos veces (una para decidir tool y otra para redactar) y la memoria se ha actualizado».

(Vuelvo a Telegram.)

> «Y aquí está la respuesta resumiendo el último briefing con datos reales».

(Escribo «Busca algo sobre SpaceX».)

> «La otra tool, búsqueda por palabra clave».

(Leo respuesta.)

(Escribo «¿Qué te he preguntado hasta ahora?».)

> «Y para demostrar la memoria conversacional, le pregunto qué le he preguntado antes».

(Leo respuesta.)

> «Recuerda los tres turnos: hola, último briefing y SpaceX. La memoria está enchufada».

### 13:00 — 14:00 · Decisiones técnicas

**Pantalla**: VSCode con el README en §3.

> «Algunas decisiones rápidas y por qué».

> «Local en lugar del n8n del profesor, porque el servidor estuvo varias horas caído cerca del deadline. Lo monté con el `self-hosted-ai-starter-kit` que trae n8n, Ollama y Postgres. Qdrant también lo trae el kit pero como no hago RAG no lo uso».

> «Groq en el chatbot y Ollama en el briefing por la limitación de mi GPU».

> «Todo en un único workflow porque el enunciado pide en singular `apellido_nombre_workflow.json`, y las tres ramas caben perfectamente compartiendo bot y hoja».

### 14:00 — 14:30 · Cierre

> «Y eso es todo. En el README tengo los problemas que me han salido con sus soluciones, las páginas que he consultado y todas las capturas».

> «Cualquier cosa, en el README está».

> «Gracias por el tiempo».

(Fin de grabación.)

---

## Después de grabar

- Revisar audio en las 3 zonas (intro, recorrido, demo).
- Recortar lo que sobre.
- Subir el vídeo (MP4 o el formato que pida) o compartir el enlace.
- **Borrar la API key de Groq y crear otra**: la actual la pegué en una conversación de IA durante el desarrollo. Por seguridad la rotamos.
