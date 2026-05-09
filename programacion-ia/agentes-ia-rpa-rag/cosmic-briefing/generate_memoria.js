/* eslint-disable */
// Genera autor_memoria.docx (memoria estructurada según enunciado)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  TableOfContents
} = require('docx');

const ROOT = __dirname;
const SHOTS = path.join(ROOT, 'screenshots');
const FONT = 'Verdana';
const MONO = 'Consolas';
const ACCENT = '1F3A6B';

const border = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' };
const cellBorders = { top: border, bottom: border, left: border, right: border };

function p(text) {
  return new Paragraph({
    spacing: { after: 200, line: 360 },
    alignment: AlignmentType.LEFT,
    children: [new TextRun({ text, font: FONT, size: 24 })]
  });
}
function tldr(text) {
  return new Paragraph({
    spacing: { before: 80, after: 240, line: 360 },
    alignment: AlignmentType.LEFT,
    shading: { type: ShadingType.CLEAR, fill: 'EAF2FB' },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT } },
    indent: { left: 200 },
    children: [
      new TextRun({ text: 'En 30 segundos. ', font: FONT, size: 24, bold: true, color: ACCENT }),
      new TextRun({ text, font: FONT, size: 24 })
    ]
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 480, after: 240 },
    children: [new TextRun({ text, font: FONT, size: 36, bold: true, color: ACCENT })]
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, font: FONT, size: 28, bold: true, color: ACCENT })]
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: ACCENT })]
  });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    spacing: { after: 120, line: 340 },
    alignment: AlignmentType.LEFT,
    children: [new TextRun({ text, font: FONT, size: 24 })]
  });
}
function code(text) {
  return new Paragraph({
    spacing: { before: 120, after: 160, line: 280 },
    shading: { type: ShadingType.CLEAR, fill: 'F2F2F2' },
    border: { top: border, bottom: border, left: border, right: border },
    children: [new TextRun({ text, font: MONO, size: 20 })]
  });
}
function img(filename, widthPx) {
  const fp = path.join(SHOTS, filename);
  if (!fs.existsSync(fp)) return p(`[Captura no encontrada: ${filename}]`);
  return new Paragraph({
    spacing: { before: 120, after: 60 },
    alignment: AlignmentType.CENTER,
    children: [new ImageRun({
      type: 'png', data: fs.readFileSync(fp),
      transformation: { width: widthPx, height: Math.round(widthPx * 0.6) },
      altText: { title: filename, description: filename, name: filename }
    })]
  });
}
function caption(text) {
  return new Paragraph({
    spacing: { after: 280, line: 320 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, font: FONT, size: 20, color: '555555' })]
  });
}
function tableRow(cells, isHeader = false) {
  return new TableRow({
    tableHeader: isHeader,
    children: cells.map(c => new TableCell({
      borders: cellBorders,
      shading: isHeader ? { type: ShadingType.CLEAR, fill: 'D9E2F3' } : undefined,
      margins: { top: 120, bottom: 120, left: 160, right: 160 },
      width: c.width ? { size: c.width, type: WidthType.DXA } : undefined,
      children: [new Paragraph({
        spacing: { after: 0, line: 320 },
        children: [new TextRun({ text: c.text, font: FONT, size: 22, bold: isHeader })]
      })]
    }))
  });
}
function table(rowsData, columnWidths, headerRow) {
  const totalWidth = columnWidths.reduce((a, b) => a + b, 0);
  const rows = [];
  if (headerRow) rows.push(tableRow(headerRow.map((t, i) => ({ text: t, width: columnWidths[i] })), true));
  rowsData.forEach(rowData => rows.push(tableRow(rowData.map((t, i) => ({ text: t, width: columnWidths[i] })))));
  return new Table({ width: { size: totalWidth, type: WidthType.DXA }, columnWidths, rows });
}
function pageBreak() { return new Paragraph({ children: [new PageBreak()] }); }

// ── Contenido ─────────────────────────────────────────────────────────
const c = [];

// Portada
c.push(
  new Paragraph({ spacing: { before: 2400 }, children: [] }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: 'Cosmic Briefing', font: FONT, size: 60, bold: true, color: ACCENT })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 1000 },
    children: [new TextRun({ text: 'Tarea 9. Workflow inteligente con n8n, Ollama y Groq', font: FONT, size: 28, color: '666666' })]
  }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: 'Programación de Inteligencia Artificial', font: FONT, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 800 },
    children: [new TextRun({ text: 'CE en Inteligencia Artificial y Big Data', font: FONT, size: 22, color: '666666' })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: 'autor', font: FONT, size: 26, bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: '1.º BDAT', font: FONT, size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: 'Abril 2026', font: FONT, size: 22 })] }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 600 },
    children: [
      new TextRun({ text: 'Vídeo demo: ', font: FONT, size: 20, color: '666666' }),
      new TextRun({ text: 'https://www.youtube.com/watch?v=JRhiNauBYrM', font: FONT, size: 20, color: '0563C1', underline: {} })
    ]
  }),
  pageBreak()
);

// Índice
c.push(h1('Índice de contenidos'),
  new TableOfContents('Tabla de contenidos', { hyperlink: true, headingStyleRange: '1-3' }),
  pageBreak());

// Glosario rápido
c.push(h1('Glosario rápido'),
  p('Palabras técnicas que se repiten en el documento. Si te pierdes con alguna, vuelve aquí.'),
  table([
    ['n8n', 'Plataforma de automatización en la que se construye el flujo de trabajo conectando nodos visuales.'],
    ['Workflow', 'El flujo en sí: el conjunto de nodos conectados que componen el proyecto.'],
    ['Nodo', 'Cada bloque del workflow. Hay nodos de trigger, HTTP, Code, etc.'],
    ['Trigger', 'Nodo que arranca el workflow: por horario (Schedule), al recibir un mensaje (Telegram Trigger) o al producirse un error (Error Trigger).'],
    ['LLM', 'Large Language Model. Modelo de lenguaje generativo que redacta texto a partir de un prompt.'],
    ['Prompt', 'Instrucciones más datos que se le pasan al LLM para que escriba la respuesta.'],
    ['Embedding', 'Representación numérica de un texto como un vector (768 números en este proyecto). Textos parecidos tienen vectores parecidos.'],
    ['Clustering', 'Agrupación. En este proyecto se agrupan los titulares parecidos para que el LLM los trate como un solo tema.'],
    ['Coseno', 'Forma de medir cuánto se parecen dos vectores. Va de -1 a 1; cuanto más cerca de 1, más parecidos.'],
    ['Ollama', 'Servidor local de modelos LLM. Ejecuta modelos open-source en mi propio ordenador.'],
    ['Groq', 'Servicio en la nube que ejecuta modelos LLM muy rápido. Tiene tier gratuito.'],
    ['AI Agent', 'Nodo de n8n que combina un LLM, una memoria y unas herramientas. Decide solo cuándo invocar cada cosa.'],
    ['Tool', 'Función que el LLM puede llamar (function calling). En este proyecto, dos: ultimos_briefings y buscar_briefing.'],
    ['Webhook', 'URL pública a la que un servicio externo (Telegram en este caso) hace POST cuando ocurre algo.'],
    ['ngrok', 'Programa que abre un túnel desde una URL pública hasta un puerto local de mi ordenador.'],
    ['Docker', 'Sistema para ejecutar aplicaciones en contenedores aislados. n8n, Ollama, Postgres y Qdrant corren cada uno en su contenedor.'],
    ['Apps Script', 'Lenguaje de Google para programar acciones sobre Sheets, Docs, Drive, etc.'],
    ['RAG', 'Retrieval-Augmented Generation. Técnica de IA que indexa documentos y los recupera por similitud. Este proyecto NO es un RAG.']
  ], [2200, 7160], ['Término', 'Qué significa']),
  pageBreak());

// ════════════════════════════════════════════════════════════════════════
// 1. OBJETIVO DEL WORKFLOW
// ════════════════════════════════════════════════════════════════════════
c.push(h1('1. Objetivo del workflow'),
  tldr('Cosmic Briefing es un workflow de n8n que cada mañana mezcla 8 fuentes de astronomía y espacio en un mensaje de Telegram. Aparte tiene un chatbot que responde a preguntas sobre los briefings antiguos.'),
  p('Esta tarea plantea construir un workflow inteligente en n8n que integre componentes de Inteligencia Artificial y resuelva un problema realista. El enunciado pide un nodo LLM, una fuente de datos externa, una salida útil, al menos cinco nodos sin contar el trigger y un mecanismo básico de manejo de errores. Avisa expresamente de que no vale presentar un RAG simple (es el ejemplo de clase) y propone varias ideas como punto de partida.'),
  p('Mi proyecto se llama Cosmic Briefing. Cada mañana a las 08:00 manda al móvil por Telegram un boletín de astronomía y espacio armado con ocho fuentes públicas en directo: NASA APOD para la imagen del día, Where-ISS para la posición de la Estación Espacial, NASA NeoWs para los asteroides cercanos, Launch Library 2 para los próximos lanzamientos, Open-Meteo y Sunrise-Sunset para las condiciones del cielo esta noche, arXiv para los papers de astrofísica del día y SpaceNews para las noticias periodísticas.'),
  p('Esos titulares no se mandan tal cual al LLM. Pasan por un modelo de embeddings (`nomic-embed-text`) que devuelve vectores de 768 dimensiones. Después se agrupan con un clustering greedy por similitud coseno con umbral 0,70. Los grupos resultantes se inyectan en el prompt junto con los datos crudos, y un LLM local de Ollama (`qwen2.5:1.5b`) escribe el briefing en castellano. El mensaje llega a Telegram con la imagen del APOD incrustada y el enlace a un panel HTML público con el histórico. Cada briefing también se persiste en Google Sheets vía un Apps Script propio.'),
  p('A la rama del briefing diario le añadí una segunda rama: un chatbot que escucha al mismo bot de Telegram. Cuando le mandas un mensaje, un AI Agent (Groq, `llama-3.3-70b-versatile`) decide si es small talk o si tiene que invocar alguna de las dos herramientas que tiene a mano: `ultimos_briefings` y `buscar_briefing`. Las dos tiran del Apps Script para consultar la hoja de Sheets. El agente tiene memoria conversacional por chat, así que recuerda lo que le has preguntado antes en el mismo hilo.'),
  p('Y una tercera rama, la C, que es un Error Trigger global: si cualquier nodo del workflow falla, me llega un mensaje de aviso a Telegram con el nombre del nodo y el error. Las tres ramas viven en el mismo fichero JSON, comparten bot, hoja y modelo de embeddings.'),
  p('El proyecto NO es un RAG. No hay vector store ni indexación de documentos. Lo que hago es coger ocho fuentes en directo, agruparlas por tema con embeddings y narrar el conjunto con un LLM. La sección 5 del enunciado proponía como ejemplo un «resumidor de noticias» con cron + RSS + LLM + Telegram, y esa fue la chispa de la idea, pero el proyecto la extiende bastante.'),

  h2('1.1 Objetivos específicos del proyecto'),
  bullet('Que un workflow se ejecute solo cada día a las 08:00 sin intervención manual.'),
  bullet('Combinar ocho fuentes científicas reales en un único mensaje legible y compacto.'),
  bullet('Aplicar IA de verdad y no de adorno: embeddings semánticos para detectar temas comunes y un LLM local para escribir el briefing.'),
  bullet('Construir un chatbot del mismo bot de Telegram con AI Agent, memoria conversacional y herramientas reales que consulten el histórico de briefings.'),
  bullet('Usar el menor número de servicios de pago posible: todo el briefing diario corre en local con Ollama, y el chatbot va por Groq que es gratuito.'),
  bullet('Tolerar fallos parciales: si una API se cae, el resto del briefing se entrega igual con los datos disponibles.'),
  bullet('Mantener todo en un único fichero `apellido_nombre_workflow.json` como pide el enunciado, sin sub-workflows ni infraestructura accesoria.'),
  bullet('Documentar el proceso (este documento) y los problemas encontrados, para que otra persona pueda reproducir el proyecto a partir de aquí.')
);

// ════════════════════════════════════════════════════════════════════════
// 2. ARQUITECTURA (qué nodos uso y por qué)
// ════════════════════════════════════════════════════════════════════════
c.push(pageBreak(), h1('2. Arquitectura: qué nodos uso y por qué'),
  tldr('Un único workflow con tres ramas: A (briefing diario por cron, 16 nodos), B (chatbot por Telegram, 7 nodos) y C (errores, 2 nodos). Todo corre en un Docker local con n8n + Ollama + Postgres y un ngrok que expone el puerto 5678.'),

  h2('2.1 Visión general en tres ramas'),
  p('El sistema vive en un único workflow de n8n con tres ramas independientes que no se cruzan. Cada una tiene su propio trigger:'),
  table(
    [
      ['A — Briefing diario', 'Schedule cron 0 8 * * *', '8 APIs → consolidar → embeddings → clustering → LLM Ollama → Telegram + Sheets'],
      ['B — Chatbot', 'Telegram Trigger', 'AI Agent (Groq) con memoria + 2 tools que consultan Sheets → respuesta a Telegram'],
      ['C — Errores', 'Error Trigger', 'Si cualquier nodo del workflow falla, aviso por Telegram al admin']
    ],
    [2200, 2400, 4760],
    ['Rama', 'Trigger', 'Lo que hace']
  ),
  p('Las tres ramas comparten bot, hoja y modelo de embeddings. El briefing diario escribe en Sheets; el chatbot lee de Sheets a través de las herramientas. La rama de errores notifica fallos del propio workflow.'),
  p('Todo esto corre encima del `self-hosted-ai-starter-kit`, un docker-compose oficial mantenido por el equipo de n8n que despliega cuatro servicios: n8n (motor de workflows), Ollama (servidor local de modelos), Postgres (base de datos interna que usa el propio n8n) y Qdrant (base vectorial que el kit incluye por defecto y que en este proyecto NO uso, ya que no hago RAG; el contenedor lo dejo parado para no malgastar memoria).'),
  p('La instancia de n8n se expone al exterior con ngrok, usando un dominio estático del plan gratuito (`tapping-widget-entering.ngrok-free.dev`), para que Telegram pueda entregar los mensajes del chatbot al webhook local.'),

  h2('2.2 Tecnologías que enchufa el workflow'),

  h3('2.2.1 n8n'),
  p('n8n es una plataforma de automatización tipo low-code en la que dibujas el flujo nodo a nodo. Cada nodo encapsula una operación: un trigger temporal, una llamada HTTP, ejecutar JavaScript, un nodo de IA, etc. Los datos fluyen entre nodos como objetos JSON, y puedes inspeccionar lo que entra y lo que sale en cada paso. La instancia que uso es local, dentro de un Docker, con la última versión LTS. Accedo por el puerto 5678 en el navegador.'),

  h3('2.2.2 Ollama y los modelos descargados'),
  p('Ollama es un servidor de modelos LLM y embeddings que se ejecuta en local. Una vez instalado (en este caso, dentro del contenedor del kit), descargo modelos open-source con `ollama pull <nombre>` y los sirvo por su API HTTP en el puerto 11434.'),
  bullet('`qwen2.5:1.5b` — modelo de generación de texto de 1.5B de parámetros. Lo uso para escribir el briefing en castellano. Lo elegí porque encaja en CPU sin tener que cargar gigas de VRAM y narra bien en español sin alucinar demasiado.'),
  bullet('`nomic-embed-text` — modelo de embeddings con dimensión 768. Lo uso para vectorizar los titulares antes de hacer el clustering. Pesa unos 270 MB y es rápido en CPU.'),
  p('Probé `qwen2.5:3b` para el chatbot pensando en function calling, pero en CPU tarda entre 30 y 60 segundos por respuesta y eso rompe el webhook de Telegram. Por eso al final el chatbot lo movile a Groq.'),

  h3('2.2.3 Groq'),
  p('Groq es un proveedor de inferencia LLM en la nube famoso por su velocidad: usa hardware especializado (LPUs) y responde en milisegundos. Tiene un tier gratuito de 14400 peticiones al día con `llama-3.3-70b-versatile`, que es el modelo que uso para el chatbot. La API key se saca de `https://console.groq.com/keys`. En n8n se configura como credencial de tipo «Groq» y queda disponible para los nodos langchain.'),

  h3('2.2.4 Telegram Bot API'),
  p('El bot de Telegram lo creé con BotFather. Me da un token tipo `8642010850:AAH_...` que es lo que usan tanto la rama del briefing (para enviar mensajes con `sendMessage`) como el Telegram Trigger del chatbot (para recibir webhooks). Para que Telegram pueda entregar webhooks a una n8n local, necesito una URL pública. Eso lo resuelve ngrok.'),

  h3('2.2.5 Google Apps Script'),
  p('Apps Script es el motor de scripting de Google Workspace. En este proyecto lo uso para añadir cuatro endpoints sobre la hoja Cosmic Briefing:'),
  bullet('`POST` — añade una fila al final de la hoja con los datos del briefing.'),
  bullet('`GET ?action=last&n=N` — devuelve las últimas N filas en JSON, para la tool `ultimos_briefings`.'),
  bullet('`GET ?action=search&q=X` — devuelve las filas que contienen `X` en briefing/papers/noticias/título APOD, para la tool `buscar_briefing`.'),
  bullet('`GET ?action=dashboard` — devuelve un panel HTML con tarjetas, una por briefing.'),

  h2('2.3 Las 8 fuentes de datos externas'),

  h3('2.3.1 NASA APOD'),
  p('Imagen astronómica del día. Devuelve título, fecha, URL de la imagen y explicación. La API necesita una API key gratuita que se saca en `https://api.nasa.gov/`.'),
  code(`https://api.nasa.gov/planetary/apod?api_key=<KEY>`),
  p('De la respuesta cojo `title`, `date`, `url` y los primeros 400 caracteres de `explanation`. La URL es la que pego en el mensaje de Telegram, y Telegram la incrusta como imagen automáticamente.'),

  h3('2.3.2 Where the ISS at'),
  p('Devuelve la posición de la Estación Espacial Internacional en tiempo real. Es gratuita y no necesita clave.'),
  code(`https://api.wheretheiss.at/v1/satellites/25544`),
  p('Con la lat/lon de la ISS y la lat/lon de Cartagena calculo la distancia entre ambas con la fórmula del haversine. Si la ISS está a menos de 2000 km marco una bandera `sobre_zona = true`, que después aparece como etiqueta amarilla en el panel HTML.'),

  h3('2.3.3 NASA NeoWs'),
  p('Asteroides que se acercan a la Tierra hoy. Misma API key que APOD. La URL la parametrizo con la fecha de hoy:'),
  code(`https://api.nasa.gov/neo/rest/v1/feed?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&api_key=<KEY>`),
  p('De cada asteroide saco nombre, diámetro medio, distancia en distancias lunares (más fácil de visualizar que en km) y la bandera `is_potentially_hazardous_asteroid`. Con tres me basta para el briefing.'),

  h3('2.3.4 Launch Library 2 (TheSpaceDevs)'),
  p('Lista los próximos lanzamientos espaciales. Es gratuita y no hace falta clave.'),
  code(`https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=3&mode=list`),
  p('De cada lanzamiento extraigo el nombre, el cohete, la fecha y el sitio.'),

  h3('2.3.5 Open-Meteo'),
  p('Pronóstico horario de nubosidad. Gratuito y sin clave.'),
  code(`https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=cloud_cover&timezone=auto&forecast_days=1`),
  p('De la respuesta me quedo solo con las horas nocturnas (de 21:00 a 03:00), saco la media y la categorizo en despejado, parcialmente nublado o cubierto. Si la cobertura nocturna es menor del 40% pongo además una recomendación: «cielo favorable para observación astronómica».'),

  h3('2.3.6 Sunrise-Sunset.org'),
  p('Devuelve las horas de salida y puesta del sol y, lo más interesante para mí, las del crepúsculo astronómico:'),
  code(`https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0`),

  h3('2.3.7 arXiv astro-ph (RSS)'),
  p('Feed RSS oficial de papers de astrofísica de arXiv. Me quedo con los seis primeros.'),
  code(`https://rss.arxiv.org/rss/astro-ph`),

  h3('2.3.8 SpaceNews (RSS)'),
  p('Feed RSS de noticias del sector espacial. Cojo cinco titulares.'),
  code(`https://spacenews.com/feed/`),

  h2('2.4 Rama A — Briefing diario nodo a nodo'),

  h3('2.4.1 Nodo 1 — Schedule 08:00 diario'),
  p('Trigger temporal con expresión cron `0 8 * * *`. Dispara el resto de la rama todos los días a las 8 de la mañana.'),

  h3('2.4.2 Nodo 2 — Configuración (Code)'),
  p('Devuelve un JSON con la configuración del día.'),
  code(`return [{
  json: {
    lat: 37.608,
    lon: -0.987,
    ciudad: 'Cartagena, España',
    tono: 'divulgativo',
    hoy: new Date().toISOString().slice(0, 10)
  }
}];`),
  p('`lat` y `lon` las consumen Open-Meteo y Sunrise-Sunset. `ciudad` aparece en el prompt y en el mensaje de Telegram. `hoy` es la fecha en formato ISO recortada a YYYY-MM-DD, que es lo que necesita NeoWs en su URL.'),

  h3('2.4.3 Nodos 3 a 10 — 8 nodos HTTP a las fuentes externas'),
  p('Una serie de ocho nodos HTTP Request en cadena, cada uno consulta una fuente distinta (descritas en §2.3). Todos llevan `User-Agent` puesto a un valor explícito (algunas APIs como NASA APOD rechazan peticiones sin user-agent), un `timeout` de 30 segundos y, sobre todo, la opción `onError: continueRegularOutput`. Si una API se cae, el siguiente nodo se ejecuta igual y la consolidación se adapta.'),

  h3('2.4.4 Nodo 11 — Consolidar datos (Code)'),
  p('Recibe la salida de los ocho HTTP previos y produce una estructura unificada. Es el primer nodo grande del workflow.'),
  p('Lo primero es un helper para leer cada nodo de forma defensiva. Como las APIs llevan `onError: continueRegularOutput`, una de ellas puede haber fallado y la respuesta llegar vacía. Si simplemente accedo a un campo inexistente, el nodo Code peta. Por eso uso esto:'),
  code(`const getJson = (nodo) => {
  try { return $(nodo).first().json || {}; }
  catch(e) { return {}; }
};`),
  p('Después limpia el APOD, calcula la distancia ISS-Cartagena con haversine, extrae los asteroides, los lanzamientos, las nubes nocturnas y el crepúsculo. La parte del haversine es:'),
  code(`const toRad = d => d * Math.PI / 180;
const dLat = toRad(iss.lat - ubic.lat);
const dLon = toRad(iss.lon - ubic.lon);
const hav = Math.sin(dLat/2)**2
          + Math.cos(toRad(ubic.lat))
          * Math.cos(toRad(iss.lat))
          * Math.sin(dLon/2)**2;
iss.distancia_a_ti_km = Math.round(
  6371 * 2 * Math.atan2(Math.sqrt(hav), Math.sqrt(1-hav))
);
iss.sobre_zona = iss.distancia_a_ti_km < 2000;`),
  p('La fórmula del haversine es la estándar para calcular la distancia entre dos puntos sobre una esfera dadas sus latitudes y longitudes. 6371 es el radio medio de la Tierra en kilómetros.'),
  p('Para los asteroides hago un .slice(0, 3) para quedarme solo con los tres más relevantes y de cada uno saco diámetro medio, distancia en distancias lunares y la bandera de potencialmente peligroso. Para los lanzamientos paso por `slice(0, 3)` también y extraigo nombre, cohete, fecha y lugar.'),
  p('Las nubes nocturnas las saco filtrando las horas entre 21 y 03 y haciendo la media. El crepúsculo astronómico lo formateo a HH:MM.'),
  p('El parser RSS para arXiv y SpaceNews es un regex sencillo que extrae solo el `<title>` de cada `<item>`:'),
  code(`function parseRss(xml, maxItems) {
  if (!xml || typeof xml !== 'string') return [];
  const items = [];
  const re = /<item[^>]*>([\\s\\S]*?)<\\/item>/g;
  let m, c = 0;
  while ((m = re.exec(xml)) && c < maxItems) {
    const tit = (m[1].match(/<title[^>]*>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?<\\/title>/) || [,''])[1].trim();
    if (tit) items.push({ titulo: tit });
    c++;
  }
  return items;
}`),
  p('Al final del nodo se construye una lista plana de titulares prefijados que es lo que se mandará al embedding:'),
  code(`const titulos = [
  ...arxiv.map(i => 'PAPER: ' + i.titulo),
  ...space.map(i => 'NOTICIA: ' + i.titulo),
  ...lanzamientos.map(l => 'LANZAMIENTO: ' + l.nombre + ' (' + l.cohete + ')'),
  ...asteroides.map(a => 'ASTEROIDE: ' + a.nombre + ' a ' + a.distancia_lunar + ' distancias lunares')
];`),

  h3('2.4.5 Nodo 12 — Embeddings Ollama'),
  p('HTTP Request a la API de embeddings de Ollama:'),
  code(`POST http://ollama:11434/api/embed
{
  "model": "nomic-embed-text",
  "input": ["PAPER: ...", "NOTICIA: ...", ...]
}`),
  p('La respuesta tiene un campo `embeddings` con un array de vectores, uno por cada string de entrada. Cada vector es un array de 768 números reales. Este nodo NO usa credencial de n8n. Llama directo por HTTP a la red interna de Docker.'),

  h3('2.4.6 Nodo 13 — Clustering y prompt (Code)'),
  p('Segundo nodo Code grande. Hace dos cosas: el clustering y la construcción del prompt. La similitud coseno está implementada manualmente:'),
  code(`function cos(a, b) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na  += a[i] * a[i];
    nb  += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}`),
  p('El clustering greedy: voy uno a uno por los titulares; para cada uno calculo la similitud con el centroide de cada cluster que ya tenga; si supera 0,70, lo añado a ese cluster y recalculo el centroide; si no, abro cluster nuevo:'),
  code(`const UMBRAL = 0.70;
const clusters = [];
for (let i = 0; i < titulos.length; i++) {
  let asignado = false;
  for (const c of clusters) {
    if (cos(embs[i], c.centroide) > UMBRAL) {
      c.items.push(titulos[i]);
      for (let j = 0; j < c.centroide.length; j++) {
        c.centroide[j] = (c.centroide[j] * (c.items.length - 1)
                       + embs[i][j]) / c.items.length;
      }
      asignado = true;
      break;
    }
  }
  if (!asignado) clusters.push({ centroide: [...embs[i]], items: [titulos[i]] });
}`),
  p('El umbral 0,70 lo elegí probando: con 0,60 metía cosas no tan parecidas en el mismo cluster, y con 0,80 casi ningún titular se agrupaba. Con 0,70 se forman entre 4 y 8 grupos típicos, que es lo que tiene sentido para 16-20 titulares.'),
  p('Después se construye el prompt para el LLM con reglas estrictas y los datos reales del día:'),
  code(`Eres un asistente de ciencia y espacio. Hablas en castellano a un usuario en {ciudad}.

REGLAS ESTRICTAS:
- Usa SOLO los datos que te paso abajo. NO inventes nada.
- La ISS es un satélite, no un observatorio en tierra.
- No uses emojis ni asteriscos ni markdown. Texto plano.
- Máximo 9 frases.
- Cubre: imagen del día, ISS, asteroides si los hay, lanzamientos
  si los hay, condiciones del cielo, 1-2 noticias o papers destacados.`),
  p('Después del bloque de reglas viene el bloque de datos: APOD con título y descripción, ISS con coordenadas y distancia, asteroides cercanos, próximos lanzamientos, condiciones del cielo, y los grupos temáticos detectados por el clustering.'),

  h3('2.4.7 Nodo 14 — LLM Ollama (qwen2.5:1.5b)'),
  p('HTTP Request a la API de generación de Ollama:'),
  code(`POST http://ollama:11434/api/generate
{
  "model": "qwen2.5:1.5b",
  "prompt": "<prompt completo>",
  "stream": false,
  "keep_alive": "30m",
  "options": {
    "temperature": 0.5,
    "num_predict": 500,
    "num_ctx": 3072,
    "num_gpu": 0
  }
}`),
  bullet('`stream: false` para que la respuesta llegue de golpe en lugar de en chunks.'),
  bullet('`keep_alive: 30m` para que el modelo se quede cargado en RAM durante media hora. Sin esto, Ollama lo descarga después de 5 minutos y la siguiente ejecución tarda 10 segundos extra.'),
  bullet('`temperature: 0.5` — equilibrio entre coherencia y variedad.'),
  bullet('`num_predict: 500` — máximo 500 tokens en la respuesta.'),
  bullet('`num_ctx: 3072` — contexto de 3072 tokens.'),
  bullet('`num_gpu: 0` — fuerza CPU porque mi GPU GTX 960M ya no la soporta Ollama.'),

  h3('2.4.8 Nodo 15 — Telegram (briefing)'),
  p('HTTP POST a la API de Telegram con el texto del briefing. Le quito asteriscos por si el modelo se ha pasado con markdown, y al final pego la URL del panel HTML del Apps Script. Telegram detecta la URL del APOD y la incrusta como imagen automáticamente.'),

  h3('2.4.9 Nodo 16 — Google Sheets (log)'),
  p('Otro HTTP POST, esta vez al endpoint del Apps Script. Manda un JSON con timestamp, fecha, ciudad, datos del APOD, papers, noticias, bandera de visibilidad de la ISS, briefing completo y tokens consumidos.'),

  h2('2.5 Rama B — Chatbot nodo a nodo'),

  h3('2.5.1 Nodo 17 — Telegram Trigger (chatbot)'),
  p('Configurado para escuchar updates de tipo `message`. Cuando se activa el workflow, n8n registra automáticamente el webhook con Telegram a través de la URL pública de ngrok.'),

  h3('2.5.2 AI Agent y sub-nodos'),
  p('El nodo central de la rama es el AI Agent (`@n8n/n8n-nodes-langchain.agent`). Acepta el mensaje del usuario, decide qué hacer (responder directo o invocar herramientas) y produce la respuesta final. Tiene cuatro sub-nodos enchufados:'),
  bullet('Modelo: Groq Chat Model con `llama-3.3-70b-versatile`.'),
  bullet('Memoria: Window Buffer de 6 turnos con `chat.id` como sessionKey, así cada usuario tiene su propio hilo aislado.'),
  bullet('Tool `ultimos_briefings(n)`: HTTP GET al Apps Script con `?action=last&n={n}`.'),
  bullet('Tool `buscar_briefing(q)`: HTTP GET con `?action=search&q={q}`.'),
  p('El system message del agente le marca el comportamiento:'),
  code(`Eres COSMIC, un asistente conversacional experto en astronomía,
espacio y ciencia. Hablas en castellano con tono cercano pero
riguroso. Ayudas al usuario a consultar el histórico de Cosmic
Briefings.

REGLAS:
- Si el usuario pregunta por contenido del briefing, USA las
  herramientas. NO inventes contenido.
- Si te saludan o hacen small talk, responde sin llamar herramientas.
- Cuando devuelvas resultados de herramientas, RESÚMELOS de forma
  natural, no pegues JSON crudo.
- Máximo 6 frases por respuesta. Sin markdown, sin asteriscos.
- Si no sabes algo, dilo. No alucines.`),

  h3('2.5.3 Nodo 18 — Telegram (respuesta chatbot)'),
  p('HTTP POST que manda la respuesta del agente al chat de Telegram, con la misma limpieza de asteriscos que la rama del briefing.'),

  h2('2.6 Rama C — Manejo de errores'),
  p('La rama C es un Error Trigger global y un nodo HTTP a Telegram. Si cualquier nodo del workflow falla y no se gestiona localmente (por ejemplo, un error de programación en un Code, o que la API de Groq devuelva 500), el Error Trigger se activa y manda un mensaje al chat del administrador con el texto del error y el nombre del nodo que falló. Esta rama es complementaria a los `onError: continueRegularOutput` de los nodos HTTP de la rama A.'),

  h2('2.7 Apps Script (Code.gs)'),
  p('El Apps Script `Code.gs` es la capa que comunica n8n con Google Sheets. Vive como Web App pública desplegada con `Deploy → New deployment` desde el editor de Apps Script.'),

  h3('2.7.1 doPost: cómo se guarda un briefing'),
  p('Recibe el JSON del nodo 16 y añade una fila a la hoja activa. Aplica una limpieza importante: si n8n ha enviado el JSON con un `=` al principio (un comportamiento conocido de las expresiones de n8n), lo elimina, y la función `c()` quita ese mismo `=` de cada valor individual antes de escribirlo. Sin esto, Sheets interpreta el contenido como una fórmula y muestra `#NAME?` en lugar del valor real.'),
  code(`function doPost(e) {
  var raw = e.postData.contents;
  if (raw.charAt(0) === '=') raw = raw.substring(1);
  var datos = JSON.parse(raw);

  var c = function(v) {
    if (v === null || v === undefined || v === 'null') return 'N/A';
    var s = String(v);
    while (s.charAt(0) === '=') s = s.substring(1);
    return s;
  };

  var hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  hoja.appendRow([
    c(datos.timestamp), c(datos.fecha), c(datos.ciudad),
    c(datos.apod_titulo), c(datos.apod_url),
    c(datos.papers), c(datos.noticias),
    c(datos.iss_visible), c(datos.briefing_llm), c(datos.tokens)
  ]);
  ...
}`),

  h3('2.7.2 doGet: tres acciones en un solo endpoint'),
  p('Lee el parámetro `action` y bifurca:'),
  bullet('`?action=last&n=N`: devuelve las últimas N filas en formato JSON.'),
  bullet('`?action=search&q=X`: filtra las filas en las que la cadena `X` aparezca (case-insensitive) en cualquier campo de texto relevante (briefing, noticias, papers o título APOD).'),
  bullet('`?action=dashboard`: invoca la función `renderDashboard`, que construye una página HTML con tarjetas, una por briefing.'),

  h3('2.7.3 renderDashboard: el panel HTML'),
  p('Cuando llega `?action=dashboard`, en lugar de devolver JSON se devuelve una página HTML completa con tarjetas. Cada tarjeta tiene cabecera con título APOD y metadatos, la imagen del APOD enlazada a su URL original, y el texto del briefing con saltos de línea convertidos a `<br>`. La etiqueta amarilla «ISS sobre tu zona» se muestra solo si en esa fila el campo `ISS_Visible` es `SI`.'),

  h2('2.8 Decisiones técnicas y trazabilidad de ideas'),

  h3('2.8.1 Origen del proyecto'),
  p('De dónde viene cada pieza importante del proyecto:'),
  bullet('Idea base. La sección 5 del enunciado de la tarea propone como ejemplo un «resumidor de noticias» con cron + RSS + LLM + Telegram. Esa fue mi punto de partida. Lo cambié de tema (de noticias generales a astronomía y espacio) y lo amplié con más fuentes, embeddings, clustering, panel HTML y un chatbot.'),
  bullet('Ejemplo de RAG visto en clase. El RAG sobre Google Drive que vimos no encajaba con lo que pedía el enunciado para nota máxima, así que lo descarté como núcleo. Pero me sirvió para entender cómo se enchufan embeddings, memoria y herramientas a un agente, y eso lo aproveché en la rama B.'),
  bullet('Self-hosted-ai-starter-kit. Kit oficial de n8n que reúne en un docker-compose los servicios típicos para experimentar con IA local. Lo bajé de https://github.com/n8n-io/self-hosted-ai-starter-kit.'),
  bullet('Modelos de Ollama. qwen2.5:1.5b lo elegí del catálogo público de Ollama (https://ollama.com/library) tras probar varios para el español. nomic-embed-text es el modelo de embeddings recomendado en la documentación oficial.'),
  bullet('Groq. La API key se saca en https://console.groq.com/keys. El modelo llama-3.3-70b-versatile lo elegí porque su tier gratuito permite tool calling sin restricciones.'),
  bullet('Fórmula del haversine. La estándar para calcular distancia entre dos puntos sobre la esfera terrestre. La implementé yo en JavaScript a partir de la fórmula matemática, no de un paquete.'),
  bullet('Clustering greedy. Algoritmo simple que se me ocurrió tras ver que un k-means o un HDBSCAN eran excesivos para 16-20 titulares.'),
  p('Resumen: la chispa es del enunciado, la estructura del agente bebe del ejemplo de clase, el resto sale de mí o de la documentación oficial.'),

  h3('2.8.2 Local en lugar del n8n del profesor'),
  p('La práctica daba acceso a una instancia compartida de n8n en `progian8n.duckdns.org`. En la fase final del proyecto ese servidor estuvo varias horas inaccesible. Para no depender de un servicio fuera de mi control con la fecha de entrega encima, monté toda la infraestructura en mi máquina con el `self-hosted-ai-starter-kit`. La sección 4 del enunciado contempla esta configuración para usuarios que quieran trabajar en local.'),

  h3('2.8.3 Groq para el chatbot, Ollama para el briefing'),
  p('La GPU disponible es una NVIDIA GTX 960M con 2 GB de VRAM y compute capability 5.0. Las versiones actuales de Ollama ya no soportan esa arquitectura, así que toda la inferencia ocurre en CPU. Eso afecta a las dos ramas de forma distinta: el briefing diario tarda 5-10 segundos en CPU con `qwen2.5:1.5b` (asumible), pero el chatbot necesita tool calling fiable y rapidez.'),
  p('Probé `qwen2.5:3b` en CPU y tardaba 30-60 segundos por respuesta, rompiendo el webhook de Telegram. Por eso muevo el chatbot a Groq, que es API gratuita y responde en milisegundos. La pieza que más se ejecuta (el briefing) se mantiene 100% local; solo lo interactivo va por la nube.'),

  h3('2.8.4 Un solo workflow'),
  p('La instrucción de entrega del enunciado pide un único fichero llamado `apellido_nombre_workflow.json`. Las tres ramas caben perfectamente en el mismo fichero compartiendo bot, hoja y modelo de embeddings.'),

  h3('2.8.5 onError: continueRegularOutput en las 8 fuentes'),
  p('Si el workflow se rompe cuando una API falla, el briefing diario se queda sin entregar. Para evitarlo, los ocho nodos HTTP llevan activado `onError: continueRegularOutput`. La consolidación se ha programado de forma defensiva (con try/catch en cada bloque) y pone valores por defecto cuando no hay datos. El briefing siempre llega, aunque sea con menos información.')
);

// ════════════════════════════════════════════════════════════════════════
// 3. INSTRUCCIONES DE CONFIGURACIÓN
// ════════════════════════════════════════════════════════════════════════
c.push(pageBreak(), h1('3. Instrucciones de configuración'),
  tldr('Para reproducir el proyecto: Docker Desktop + ngrok + el self-hosted-ai-starter-kit + dos credenciales en n8n (Telegram y Groq) + el Apps Script desplegado + importar el workflow JSON y activarlo.'),

  h2('3.1 Requisitos previos'),
  bullet('Docker Desktop instalado y arrancado.'),
  bullet('ngrok instalado, autenticado con la cuenta personal y con un dominio estático del plan gratuito (`https://ngrok.com/download`).'),
  bullet('El kit `self-hosted-ai-starter-kit` clonado en local (`https://github.com/n8n-io/self-hosted-ai-starter-kit`).'),

  h2('3.2 Arranque del kit en Docker'),
  p('El kit trae 4 contenedores: `n8n`, `ollama`, `postgres-1` y `qdrant`. Solo uso los tres primeros (no hago RAG, así que Qdrant sobra). Como el kit usa nombres internos distintos para los servicios del compose, lo más práctico es arrancar todo y parar Qdrant a mano:'),
  code(`cd C:\\self-hosted-ai-starter-kit-main
docker compose up -d
docker stop qdrant`),
  p('Compruebo que quedan los 3 en marcha:'),
  code(`docker ps`),
  p('n8n queda accesible en `http://localhost:5678`. La primera vez crea usuario y contraseña, las siguientes login normal.'),

  h2('3.3 Descarga de modelos en Ollama'),
  p('El kit ya trae un contenedor llamado `ollama` con el binario instalado. En estos comandos, el primer `ollama` es el nombre del contenedor, el segundo es el binario:'),
  code(`docker exec -it ollama ollama pull qwen2.5:1.5b
docker exec -it ollama ollama pull nomic-embed-text`),
  p('Para comprobar que están:'),
  code(`Invoke-RestMethod -Uri "http://localhost:11434/api/tags" | ConvertTo-Json -Depth 4`),

  h2('3.4 Túnel ngrok'),
  p('El chatbot recibe mensajes de Telegram y para eso n8n tiene que estar accesible desde fuera. Abro una PowerShell aparte y la dejo abierta mientras uso el chatbot:'),
  code(`ngrok http 5678 --domain=tapping-widget-entering.ngrok-free.dev`),
  p('Si cierro esa ventana, el chatbot deja de funcionar. El briefing diario y el panel HTML van por su cuenta, no dependen de ngrok.'),
  p('Para verificar que el túnel está vivo:'),
  code(`Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" | ConvertTo-Json -Depth 5`),

  h2('3.5 Credenciales en n8n'),
  p('Solo hacen falta dos credenciales. En `http://localhost:5678` → menú lateral → `Credentials` → `New`:'),
  bullet('**Telegram API**: token del bot que me dio BotFather.'),
  bullet('**Groq**: API key gratis sacada en `https://console.groq.com/keys`. Importante copiarla en cuanto la genera, después solo se ve el prefijo.'),
  p('Pulso **Test** en las dos. Si pasan, sigo. Los nodos del briefing diario (`Embeddings Ollama` y `LLM Ollama`) NO necesitan credencial: llaman a Ollama por HTTP directo a `http://ollama:11434` (la URL interna de Docker).'),

  h2('3.6 Despliegue del Apps Script'),
  p('Abro la hoja Cosmic Briefing en Google Sheets → `Extensiones` → `Apps Script`. Pego el contenido de `google-apps-script/Code.gs` en el editor y le doy a:'),
  code(`Deploy → Manage deployments → (lápiz para editar) → Version: New version → Deploy`),
  p('La URL `/exec` no cambia entre versiones. Para comprobar que el panel HTML responde, la pego en el navegador con `?action=dashboard` al final.'),

  h2('3.7 Importación y activación del workflow'),
  p('En n8n → arriba a la izquierda → `+` → `Import from File` → selecciono `autor_workflow.json`.'),
  p('Asigno credenciales en los dos nodos que las piden:'),
  bullet('`17. Telegram Trigger (chatbot)` → Telegram API.'),
  bullet('`Groq Chat Model (llama-3.3-70b)` → Groq.'),
  p('El resto de nodos HTTP no necesitan credencial, llaman a APIs públicas. Activo el workflow con el toggle de arriba a la derecha. Al activarse, n8n registra solo el webhook con Telegram a través de la URL de ngrok.')
);

// ════════════════════════════════════════════════════════════════════════
// 4. CAPTURAS DE PANTALLA
// ════════════════════════════════════════════════════════════════════════
c.push(pageBreak(), h1('4. Capturas de pantalla'),
  p('Capturas del workflow en n8n y de varias ejecuciones exitosas, agrupadas por ámbito.'),

  h2('4.1 Vistas del workflow'),
  img('01a_workflow_rama_A_izq.png', 580),
  caption('Figura 1.A. Workflow — Rama A (parte izquierda). Cabecera, sticky de las 8 fuentes y nodos 1-11 (Schedule, Configuración, las 8 APIs y Consolidar datos).'),
  img('01b_workflow_rama_A_dcha.png', 580),
  caption('Figura 1.B. Workflow — Rama A (parte derecha). Sticky de IA local con Ollama, sticky de la salida del briefing y los nodos 12-16 (Embeddings, Clustering, LLM, Telegram briefing y Sheets).'),
  img('01c_workflow_rama_B_chatbot.png', 580),
  caption('Figura 2. Workflow — Rama B (chatbot). Telegram Trigger → AI Agent → Telegram (respuesta), con los cuatro sub-nodos enchufados al agente: Groq Chat Model, memoria conversacional, tool ultimos_briefings y tool buscar_briefing.'),
  img('01d_workflow_rama_C_errores.png', 580),
  caption('Figura 3. Workflow — Rama C (errores). Error Trigger global y el nodo que avisa por Telegram al admin.'),

  h2('4.2 Ejecución exitosa'),
  img('02_execution_chatbot.png', 580),
  caption('Figura 4. Ejecución del chatbot funcionando. Pregunta «Busca algo sobre SpaceX»: todos los nodos en verde, Groq se llama dos veces (decidir tool y redactar) y buscar_briefing lanza una petición al Apps Script.'),

  h2('4.3 Mensajes en Telegram'),
  img('03a_telegram_briefing_1.png', 580),
  caption('Figura 5.A. Briefing diario en Telegram (parte superior). Cabecera con la ciudad, saludo, imagen astronómica del día (APOD), posición de la ISS, asteroides cercanos detectados (NeoWs), próximos lanzamientos (Launch Library 2) y comienzo de las condiciones del cielo.'),
  img('03b_telegram_briefing_2.png', 580),
  caption('Figura 5.B. Briefing diario en Telegram (parte inferior). Continuación con las condiciones de observación nocturnas, pie con la URL del APOD, enlace al panel HTML y la línea de métricas. Telegram incrusta automáticamente la imagen del APOD.'),
  img('04_telegram_chatbot.png', 580),
  caption('Figura 6. Conversación con el chatbot. El bot recibe «¿Qué dijo el último briefing?» y resume el contenido (ha llamado a ultimos_briefings). Después se le pregunta qué se le ha preguntado antes y lo recuerda, lo que confirma la memoria.'),

  h2('4.4 Persistencia y panel'),
  img('05_dashboard.png', 580),
  caption('Figura 7. Panel HTML del histórico. Salida del endpoint ?action=dashboard del Apps Script: cabecera con los contadores y, debajo, una tarjeta por briefing.'),
  img('06_sheets.png', 580),
  caption('Figura 8. Hoja de Google Sheets con las cabeceras correctas y los briefings persistidos. Esta misma hoja la consultan después las dos tools del chatbot.'),

  h2('4.5 ngrok funcionando'),
  img('07_ngrok_tunnel.png', 580),
  caption('Figura 9. ngrok exponiendo n8n al exterior. Sesión activa con el dominio estático apuntando a localhost:5678. El log de HTTP Requests muestra los POST de Telegram entregándose con 200 OK.')
);

// ════════════════════════════════════════════════════════════════════════
// 5. PROBLEMAS ENCONTRADOS Y CÓMO LOS RESOLVÍ
// ════════════════════════════════════════════════════════════════════════
c.push(pageBreak(), h1('5. Problemas encontrados y cómo los resolví'),
  p('Lista de los problemas reales que aparecieron durante el desarrollo, con la solución aplicada en cada caso.'),
  table([
    ['Las celdas de Sheets se llenaban con #NAME?', 'n8n insertaba un = al inicio de los valores. Se elimina en el Apps Script y en la consolidación.'],
    ['Los \\n aparecían como literal en Telegram', 'En las expresiones de n8n hay que escapar dos veces: \\\\n.'],
    ['Ollama crasheaba al usar GPU', 'La GTX 960M (compute 5.0) ya no la soporta. Forzado CPU con options.num_gpu: 0.'],
    ['Modelos 3B no entraban en VRAM', 'Cambiado a qwen2.5:1.5b para el briefing y a Groq para el chatbot.'],
    ['El modelo se descargaba de RAM entre ejecuciones', 'Activado keep_alive: 30m en el body de la petición.'],
    ['El LLM ponía asteriscos pese al prompt', 'Post-procesado con regex en el nodo Telegram para quitarlos.'],
    ['El briefing salía cortado a mitad de frase', 'Ampliado num_predict a 500 y num_ctx a 3072.'],
    ['Tool calling con qwen pequeño no era fiable', 'Movido el chatbot a Groq con llama-3.3-70b-versatile.'],
    ['Si una API caía, se rompía toda la cadena', 'Añadido onError: continueRegularOutput en los 8 nodos HTTP.'],
    ['El n8n del profesor no respondía', 'Migrado a un n8n local en Docker expuesto con ngrok.'],
    ['ngrok hay que arrancarlo a mano cada vez', 'Documentado en §3.4. Mejora pendiente: meterlo como contenedor del kit con NGROK_AUTHTOKEN en .env.'],
    ['Cabeceras de Sheets desplazadas una columna', 'Faltaba la columna Timestamp al inicio. Corregidas las cabeceras de la fila 1.'],
    ['Webhook de Telegram daba 404', 'La URL pública apuntaba a un path que no existía. Forzado el setWebhook con la URL correcta.'],
    ['Webhook de Telegram daba 403', 'Falta el secret token de n8n. Solución: desactivar y reactivar el workflow para que n8n re-registre el webhook.']
  ], [4400, 5000], ['Problema', 'Solución'])
);

// ════════════════════════════════════════════════════════════════════════
// 6. PRUEBAS FUNCIONALES
// ════════════════════════════════════════════════════════════════════════
c.push(pageBreak(), h1('6. Pruebas funcionales'),
  p('Todas las pruebas que cito a continuación están grabadas en el vídeo demostrativo del proyecto, disponible en https://www.youtube.com/watch?v=JRhiNauBYrM. Resumido por escrito, las pruebas son:'),
  bullet('Ejecución manual del briefing desde el editor de n8n. El workflow recorre los 16 nodos en cadena, todos terminan en verde, y un mensaje completo llega a Telegram con todos los bloques (APOD, ISS, asteroides, lanzamientos, cielo, papers y noticias).'),
  bullet('Verificación de la persistencia. Después de la ejecución manual, una nueva fila aparece en Sheets con todas las columnas correctamente rellenadas.'),
  bullet('Verificación del panel HTML. El enlace «Panel completo de briefings» que viene en cada mensaje de Telegram abre la página con todas las tarjetas históricas.'),
  bullet('Saludo simple al chatbot («Hola»). El agente responde sin invocar herramientas. En Executions se ve que la rama B se disparó pero no hay tick verde en las tools.'),
  bullet('Pregunta por el último briefing («¿Qué dijo el último briefing?»). El agente invoca `ultimos_briefings`, recibe la última fila y la resume.'),
  bullet('Búsqueda por palabra clave («Busca algo sobre SpaceX»). El agente invoca `buscar_briefing` con `q=SpaceX`, recibe los hits y los resume.'),
  bullet('Verificación de la memoria conversacional («¿Qué te he preguntado hasta ahora?»). El agente recuerda los turnos previos del mismo `chat.id` y los enumera.'),
  bullet('Verificación del túnel ngrok. El panel local de ngrok en `127.0.0.1:4040` muestra el túnel activo y los logs de POST entregados a `/webhook/cosmic-chatbot/webhook` con código 200 OK.')
);

// ════════════════════════════════════════════════════════════════════════
// 7. CONCLUSIONES
// ════════════════════════════════════════════════════════════════════════
c.push(h1('7. Conclusiones y trabajos futuros'),

  h2('7.1 Conclusiones'),
  p('El proyecto cumple con los objetivos planteados en §1.1. El briefing diario se entrega de forma autónoma sin intervención humana, integra ocho fuentes científicas reales, aplica embeddings y clustering para mejorar la coherencia narrativa, y produce un texto natural en castellano. El chatbot responde a consultas sobre el histórico mediante function calling y memoria conversacional, demostrando el uso del nodo AI Agent de n8n con varias herramientas.'),
  p('A nivel personal el proyecto me ha permitido tocar de cerca tecnologías de IA generativa con una práctica real (no un ejemplo de juguete) y enfrentarme a problemas técnicos concretos: limitaciones de hardware, peculiaridades de las APIs externas, formatos de datos heterogéneos, gestión de webhooks, comportamiento de los LLM pequeños frente a function calling, etc. La separación entre Ollama local para tareas controladas (briefing) y Groq en la nube para la pieza interactiva (chatbot) ha sido la decisión más útil del proyecto.'),
  p('La principal lección aprendida es que la robustez en pipelines con muchas dependencias externas se consigue con tolerancia a fallos a nivel de cada llamada (`onError`, `try/catch`, defaults defensivos), no esperando a que todo vaya perfecto. Un solo `onError: continueRegularOutput` bien colocado evita una cantidad importante de incidentes.'),

  h2('7.2 Trabajos futuros'),
  p('El proyecto se entrega funcional, pero quedan mejoras anotadas para una próxima iteración:'),
  bullet('Contenerizar ngrok dentro del propio docker-compose del kit, usando una variable NGROK_AUTHTOKEN en el .env, de forma que el túnel arranque junto al resto de servicios y desaparezca el paso manual.'),
  bullet('Sustituir la búsqueda por palabra clave del chatbot por una búsqueda semántica real, embedando también las preguntas y comparando con los embeddings de los briefings persistidos.'),
  bullet('Soportar varias ciudades simultáneamente, parametrizando la rama A para que un mismo workflow pueda generar briefings personalizados para distintos chats de Telegram.'),
  bullet('Añadir métricas de seguimiento (tiempo de cada nodo, número de hits a cada API, tokens consumidos por modelo) en una hoja aparte para detectar degradaciones.'),
  bullet('Sustituir el clustering greedy por uno aglomerativo o basado en HDBSCAN, que daría mejores agrupaciones cuando el número de titulares crezca.')
);

// ════════════════════════════════════════════════════════════════════════
// 8. RECURSOS Y REFERENCIAS
// ════════════════════════════════════════════════════════════════════════
c.push(pageBreak(), h1('8. Recursos y referencias'),
  p('Lista de páginas que he tenido abiertas mientras montaba el proyecto.'),

  h2('8.1 Plataforma y entorno'),
  bullet('n8n self-hosted-ai-starter-kit — https://github.com/n8n-io/self-hosted-ai-starter-kit'),
  bullet('Documentación oficial de n8n — https://docs.n8n.io/'),
  bullet('AI Agent en n8n — https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/'),
  bullet('Window Buffer Memory — https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.memorybufferwindow/'),
  bullet('Tool HTTP Request — https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolhttprequest/'),
  bullet('ngrok — https://ngrok.com/download'),

  h2('8.2 Modelos y LLM'),
  bullet('Ollama — https://ollama.com'),
  bullet('Catálogo de modelos de Ollama — https://ollama.com/library'),
  bullet('API de Ollama — https://github.com/ollama/ollama/blob/main/docs/api.md'),
  bullet('Groq — https://console.groq.com/docs/quickstart'),

  h2('8.3 APIs de datos del briefing'),
  bullet('NASA APOD y NeoWs — https://api.nasa.gov/'),
  bullet('Where the ISS at — https://wheretheiss.at/w/developer'),
  bullet('Launch Library 2 (TheSpaceDevs) — https://ll.thespacedevs.com/2.2.0/swagger/'),
  bullet('Open-Meteo — https://open-meteo.com/en/docs'),
  bullet('Sunrise-Sunset.org — https://sunrise-sunset.org/api'),
  bullet('arXiv RSS feeds — https://info.arxiv.org/help/rss.html'),
  bullet('SpaceNews RSS — https://spacenews.com/feed/'),

  h2('8.4 Telegram y Apps Script'),
  bullet('Telegram Bot API — https://core.telegram.org/bots/api'),
  bullet('Google Apps Script HtmlService — https://developers.google.com/apps-script/reference/html/html-service'),

  h2('8.5 Inspiración para el formato del proyecto'),
  bullet('Ejemplo «Resumidor de noticias» propuesto en la sección 5 del enunciado de la tarea (cron + RSS + LLM + Telegram), adaptado a astronomía y ampliado.'),
  bullet('Ejemplo de RAG visto en clase, que sirvió como referencia para entender cómo se enchufan embeddings, memoria y herramientas a un agente — aunque deliberadamente NO se ha realizado un RAG.')
);

// ── Documento ─────────────────────────────────────────────────────────
const doc = new Document({
  creator: 'autor',
  title: 'Cosmic Briefing — Memoria técnica',
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 36, bold: true, font: FONT, color: ACCENT },
        paragraph: { spacing: { before: 480, after: 240 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: ACCENT },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: FONT, color: ACCENT },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    }]
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: 'Cosmic Briefing · autor · Programación para IA · Unidad 9', font: FONT, size: 18, color: '888888' })]
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: 'Página ', font: FONT, size: 18, color: '888888' }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: '888888' }),
        new TextRun({ text: ' de ', font: FONT, size: 18, color: '888888' }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 18, color: '888888' })
      ]
    })] }) },
    children: c
  }]
});

const out = path.join(ROOT, 'autor_memoria.docx');
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(out, buf);
  console.log('OK ->', out, '(' + buf.length + ' bytes)');
}).catch(err => { console.error('ERROR:', err); process.exit(1); });
