// Generador del DocumentoTecnico.docx para la Tarea Unidad 9
// Autor: autor - Abril 2026

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  AlignmentType, LevelFormat, BorderStyle, WidthType, ShadingType,
  HeadingLevel, PageBreak, TableOfContents, PageNumber, Header, Footer,
  ExternalHyperlink
} = require('docx');

const OUT_PATH = path.join(__dirname, '..', 'DocumentoTecnico.docx');
const IMG_ESQUEMA = path.join(__dirname, '..', 'hardware', 'esquema_estacion_iot.png');

// ================== ESTILOS COMUNES ==================
const FONT = 'Arial';
const border = { style: BorderStyle.SINGLE, size: 4, color: 'AAAAAA' };
const cellBorders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

// Helper para crear parrafos normales
const P = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 22, ...opts })],
  spacing: { after: 120 },
  alignment: opts.align || AlignmentType.JUSTIFIED,
});

// Helper parrafos con varios runs
const PR = (runs, opts = {}) => new Paragraph({
  children: runs.map(r => typeof r === 'string' ? new TextRun({ text: r, font: FONT, size: 22 }) : r),
  spacing: { after: 120 },
  alignment: opts.align || AlignmentType.JUSTIFIED,
});

// Helper runs de formato
const run = (text, opts = {}) => new TextRun({ text, font: FONT, size: 22, ...opts });
const runBold = (text) => run(text, { bold: true });
const runCode = (text) => new TextRun({ text, font: 'Consolas', size: 20, color: '802020' });

// Parrafos en bullet list
const BULL = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 22 })],
  numbering: { reference: 'bullets', level: 0 },
  spacing: { after: 80 },
});
const BULLR = (runs) => new Paragraph({
  children: runs.map(r => typeof r === 'string' ? new TextRun({ text: r, font: FONT, size: 22 }) : r),
  numbering: { reference: 'bullets', level: 0 },
  spacing: { after: 80 },
});

// Headings
const H1 = (text) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 32, bold: true, color: '2E3A87' })],
  spacing: { before: 360, after: 180 },
  heading: HeadingLevel.HEADING_1,
  pageBreakBefore: true,
});
const H1_NO_BREAK = (text) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 32, bold: true, color: '2E3A87' })],
  spacing: { before: 360, after: 180 },
  heading: HeadingLevel.HEADING_1,
});
const H2 = (text) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 26, bold: true, color: '444444' })],
  spacing: { before: 240, after: 120 },
  heading: HeadingLevel.HEADING_2,
});
const H3 = (text) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: '666666' })],
  spacing: { before: 180, after: 100 },
  heading: HeadingLevel.HEADING_3,
});

// Codigo bloque
const CODE = (text) => new Paragraph({
  children: [new TextRun({ text, font: 'Consolas', size: 18, color: '222222' })],
  shading: { type: ShadingType.CLEAR, fill: 'F2F2F2' },
  border: {
    top: { style: BorderStyle.SINGLE, size: 2, color: 'CCCCCC' },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: 'CCCCCC' },
    left: { style: BorderStyle.SINGLE, size: 2, color: 'CCCCCC' },
    right: { style: BorderStyle.SINGLE, size: 2, color: 'CCCCCC' },
  },
  spacing: { before: 80, after: 80 },
});

// Celda de tabla
function cell(text, opts = {}) {
  return new TableCell({
    borders: cellBorders,
    margins: cellMargins,
    width: opts.width || { size: 3120, type: WidthType.DXA },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text, font: FONT, size: 20, bold: opts.bold })],
      alignment: opts.align || AlignmentType.LEFT,
    })],
  });
}

// ================== CONTENIDO ==================

const children = [];

// ---------- PORTADA ----------
children.push(new Paragraph({
  children: [new TextRun({ text: '', font: FONT, size: 24 })],
  spacing: { before: 4000 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'Tarea Unidad 9', font: FONT, size: 52, bold: true, color: '2E3A87' })],
  alignment: AlignmentType.CENTER,
  spacing: { after: 240 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'Estación IoT inteligente con n8n, ESP32 y LLM', font: FONT, size: 36, color: '444444' })],
  alignment: AlignmentType.CENTER,
  spacing: { after: 720 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'Automatización de procesos y agentes IA', font: FONT, size: 28, italics: true, color: '777777' })],
  alignment: AlignmentType.CENTER,
  spacing: { after: 120 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'Programación para IA', font: FONT, size: 26, color: '777777' })],
  alignment: AlignmentType.CENTER,
  spacing: { after: 120 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'CE en Inteligencia Artificial y Big Data', font: FONT, size: 24, color: '999999' })],
  alignment: AlignmentType.CENTER,
  spacing: { after: 1800 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'autor', font: FONT, size: 28, bold: true })],
  alignment: AlignmentType.CENTER,
  spacing: { after: 120 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'Abril 2026', font: FONT, size: 22, color: '666666' })],
  alignment: AlignmentType.CENTER,
  spacing: { after: 120 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: 'Rev 2.0', font: FONT, size: 20, italics: true, color: '999999' })],
  alignment: AlignmentType.CENTER,
}));

// ---------- INDICE DE CONTENIDOS ----------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(H1_NO_BREAK('Índice de contenidos'));
children.push(new TableOfContents('Índice', { hyperlink: true, headingStyleRange: '1-3' }));

// ==========================================================
// 1. INTRODUCCION
// ==========================================================
children.push(H1('1. Introducción'));

children.push(P('Esta tarea plantea diseñar y montar un workflow en n8n que resuelva un problema real o, al menos, realista. En clase vimos un ejemplo con RAG sobre Google Drive y un chatbot que respondía a preguntas sobre documentos indexados. Para esta entrega cada uno tenía que proponer y construir su propio flujo con al menos un componente de IA y alguna integración útil. Una indicación explícita del enunciado era no replicar el RAG visto en clase salvo que se ampliara lo suficiente, cosa que no hago: mi proyecto va por otro lado.'));

children.push(P('Mi propuesta es una estación IoT inteligente montada sobre un ESP32 con varios sensores del kit Elegoo (temperatura, humedad, presencia, distancia y luz). Los sensores envían sus lecturas por HTTP a un workflow de n8n que combina los datos del interior con la información meteorológica real del exterior (Open-Meteo), pasa el conjunto al modelo LLM de Groq para generar un análisis en lenguaje natural, avisa por Telegram, guarda el histórico en Google Sheets y, como devuelve la respuesta al propio ESP32, la placa actualiza su LED RGB y su buzzer.'));

children.push(P('Sobre esa base he añadido dos mejoras que suben nota: un chatbot de Telegram que usa embeddings de Gemini para contestar preguntas sobre el histórico, y una predicción diaria que se dispara cada mañana a las 8:00 combinando el pronóstico de Open-Meteo con el LLM. También hay auto-localización por IP para que el usuario no tenga que configurar la ubicación manualmente.'));

children.push(P('En mitad del desarrollo el servidor de n8n del profesor se cayó, así que migré todo a una instalación self-hosted con Docker usando el kit oficial de n8n (self-hosted-ai-starter-kit), y expongo el n8n local a Internet con ngrok para que Telegram pueda llegar al webhook. Al final resulta que esa migración me ha dejado una infraestructura más robusta y además es una mejora más que documentar.'));

// ==========================================================
// 2. OBJETIVOS
// ==========================================================
children.push(H1('2. Objetivos'));

children.push(P('El enunciado fija unos requisitos mínimos y algunos opcionales que suman nota. Repaso cada uno y explico cómo lo cumplo:'));

children.push(H2('2.1 Requisitos obligatorios'));

children.push(BULLR([runBold('Uso de IA: '), 'el workflow usa el modelo ', runBold('llama-3.1-8b-instant'), ' de Groq. Ese modelo recibe el estado de los sensores interiores junto con los datos del exterior y devuelve un análisis en español con un nivel de alerta (VERDE, AMARILLO o ROJO).']));
children.push(BULLR([runBold('Fuente de datos real: '), 'los datos vienen de dos sitios reales, no inventados. Los interiores los genera el ESP32 con sus sensores físicos. Los exteriores los consulto a Open-Meteo, un servicio meteorológico gratuito con datos reales.']));
children.push(BULLR([runBold('Salida útil: '), 'mensaje a Telegram con el análisis de la IA, fila en Google Sheets como histórico y respuesta al propio ESP32 con el nivel de alerta para que actualice el LED RGB y el buzzer.']));
children.push(BULLR([runBold('Más de 5 nodos: '), 'el workflow tiene 32 nodos distribuidos en cinco ramas (flujo principal, geolocalización web, chatbot con embeddings, predicción diaria y manejador de errores).']));
children.push(BULLR([runBold('Gestión de errores: '), 'hay un nodo Error Trigger que captura cualquier fallo y manda un aviso por Telegram con el nodo que falló. Varios nodos Code también hacen validaciones defensivas sobre los datos antes de seguir.']));
children.push(BULLR([runBold('No es un RAG: '), 'el proyecto no es una copia del ejemplo de clase. No indexa documentos en vector store para responder preguntas sobre ellos. La parte de embeddings (chatbot) es una mejora adicional sobre un flujo IoT, no el núcleo del sistema.']));

children.push(H2('2.2 Requisitos opcionales que cumplo'));

children.push(BULLR([runBold('Embeddings: '), 'el chatbot de Telegram calcula el embedding de la pregunta con ', runBold('gemini-embedding-001'), ' de Google y lo pasa junto con el histórico al LLM para generar la respuesta.']));
children.push(BULLR([runBold('Varios servicios externos: '), 'ESP32 por HTTP, Open-Meteo API, Groq LLM API, Gemini embeddings API, Telegram Bot API, Google Sheets vía Apps Script, Nominatim para geocoding y ip-api.com para localización por IP. Ocho servicios distintos conectados.']));
children.push(BULLR([runBold('Doble canal de geolocalización: '), 'una mini web con la API nativa del navegador, ubicación compartida vía Telegram y auto-localización por IP como fallback.']));
children.push(BULLR([runBold('Hardware IoT real: '), 'la estación se monta sobre un ESP32 con siete componentes del kit Elegoo (sensores y actuadores), no es un simulador.']));
children.push(BULLR([runBold('Feedback físico: '), 'el ESP32 recibe el nivel de alerta como respuesta HTTP y enciende el LED RGB (verde, amarillo, rojo) y activa el buzzer en nivel rojo.']));
children.push(BULLR([runBold('Predicción diaria: '), 'schedule trigger que a las 8:00 cada mañana combina el forecast de 24 horas de Open-Meteo con el LLM y envía por Telegram un resumen del tiempo previsto.']));

// ==========================================================
// 3. ARQUITECTURA GENERAL
// ==========================================================
children.push(H1('3. Arquitectura general'));

children.push(P('La arquitectura tiene tres piezas principales y varios servicios colgando a los lados. Lo resumo primero en un párrafo y luego lo desgloso.'));

children.push(P('El ESP32 lee sus sensores cada 30 segundos y envía los datos por HTTP POST a un webhook de n8n. El workflow valida los datos, resuelve la ubicación (por prioridad: staticData manual, IP geolocation, o sin ubicación), consulta Open-Meteo con la lat/lon, pasa todo al modelo LLM de Groq, parsea su respuesta, manda un mensaje a Telegram, escribe una fila en Google Sheets y, por último, responde al ESP32 con el nivel de alerta. En paralelo corren otras tres ramas: el chatbot con embeddings, la predicción diaria y el error handler.'));

children.push(H2('3.1 Capas'));

children.push(PR([runBold('Capa de sensores (hardware): '), 'ESP32 DevKit V1 con DHT11 (temperatura y humedad), HC-SR501 (presencia por PIR), fotorresistencia LDR en divisor de tensión con una resistencia de 10 kiloohmios, ultrasónico HC-SR04 (distancia), OLED 0.96" I2C, LED RGB de cátodo común con tres resistencias de 220 ohmios y un buzzer activo.']));

children.push(PR([runBold('Capa de orquestación: '), 'workflow de n8n con 32 nodos. Hace de cerebro del sistema. Recibe los datos, decide qué hacer con ellos, llama al LLM, al servicio de embeddings, manda avisos y responde al ESP32.']));

children.push(PR([runBold('Capa de IA: '), 'Groq (llama-3.1-8b-instant) para generación de texto, Gemini (gemini-embedding-001) para embeddings vectoriales. Los dos son servicios gratuitos en tier free.']));

children.push(PR([runBold('Capa de infraestructura: '), 'n8n self-hosted en Docker corriendo en mi PC con el kit oficial self-hosted-ai-starter-kit, expuesto a Internet con un túnel ngrok para que Telegram pueda alcanzar los webhooks. El Apps Script de Google Sheets y el resto de servicios son en la nube.']));

children.push(H2('3.2 Flujo de datos de una lectura'));

children.push(P('Este es el recorrido que hace una lectura de sensores desde que sale del ESP32 hasta que vuelve a él con el veredicto de la IA:'));

children.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [720, 2400, 6240],
  rows: [
    new TableRow({
      children: [
        cell('Paso', { bold: true, fill: 'D5E8F0', align: AlignmentType.CENTER, width: { size: 720, type: WidthType.DXA } }),
        cell('Componente', { bold: true, fill: 'D5E8F0', width: { size: 2400, type: WidthType.DXA } }),
        cell('Acción', { bold: true, fill: 'D5E8F0', width: { size: 6240, type: WidthType.DXA } }),
      ],
      tableHeader: true,
    }),
    ...[
      ['1', 'ESP32', 'Lee DHT11, LDR, PIR y HC-SR04. Construye un JSON con temp, hum, luz, presencia, distancia.'],
      ['2', 'ESP32', 'HTTP POST al webhook de n8n (ngrok) con los datos.'],
      ['3', 'n8n - Webhook', 'Recibe el POST y pasa el body al siguiente nodo.'],
      ['4', 'n8n - Validar', 'Comprueba campos obligatorios, valida rangos, extrae la IP pública del header X-Forwarded-For.'],
      ['5', 'n8n - IP Geolocation', 'Si no hay ubicación en staticData, consulta ip-api.com con la IP pública y la guarda.'],
      ['6', 'n8n - Merge', 'Decide qué ubicación usar (manual > IP > ninguna).'],
      ['7', 'n8n - IF', 'Bifurca según si hay ubicación configurada.'],
      ['8', 'n8n - Open-Meteo', 'Consulta el tiempo actual en esa lat/lon.'],
      ['9', 'n8n - Combinar', 'Une interior + exterior, calcula diferencias, detecta anomalías.'],
      ['10', 'n8n - Groq', 'Llama al LLM con el prompt construido a partir de los datos.'],
      ['11', 'n8n - Parsear IA', 'Extrae el texto del LLM, detecta el nivel de alerta y prepara el mensaje.'],
      ['12', 'n8n - Salidas', 'Envía el mensaje a Telegram y escribe una fila en Google Sheets en paralelo.'],
      ['13', 'n8n - Responder', 'Devuelve un JSON al ESP32 con nivel y ciudad.'],
      ['14', 'ESP32', 'Recibe el JSON, actualiza el LED RGB y, si es nivel ROJO, dispara el buzzer.'],
    ].map(([n, c, a]) => new TableRow({
      children: [
        cell(n, { align: AlignmentType.CENTER, width: { size: 720, type: WidthType.DXA } }),
        cell(c, { width: { size: 2400, type: WidthType.DXA } }),
        cell(a, { width: { size: 6240, type: WidthType.DXA } }),
      ],
    })),
  ],
}));

// ==========================================================
// 4. CONFIGURACION DEL ENTORNO N8N
// ==========================================================
children.push(H1('4. Entorno n8n: del servidor del profesor a Docker + ngrok'));

children.push(P('La primera versión del proyecto corría sobre la instancia de n8n del profesor en progian8n.duckdns.org. Pero a mitad del desarrollo esa instancia dejó de responder, así que moví todo a mi propio n8n self-hosted con Docker. A efectos prácticos resultó una mejora: tengo control total sobre el workflow, puedo hacer snapshots, reiniciar cuando quiera y no dependo de que el servidor esté arriba.'));

children.push(H2('4.1 Instalación del self-hosted-ai-starter-kit'));

children.push(P('El equipo de n8n mantiene un kit oficial llamado self-hosted-ai-starter-kit que levanta con Docker Compose toda una pila local pensada para IA:'));

children.push(BULL('n8n en el puerto 5678.'));
children.push(BULL('Ollama, un runtime de modelos LLM locales (no lo uso en este proyecto, pero está disponible por si quiero probar sin depender de Groq).'));
children.push(BULL('Qdrant, base de datos vectorial (tampoco la uso aquí, pero viene incluida).'));
children.push(BULL('PostgreSQL para el almacenamiento interno de n8n.'));

children.push(P('El arranque fue clonar el repo, ajustar las variables de entorno en docker-compose.yml y lanzar con:'));

children.push(CODE('docker compose up -d'));

children.push(H2('4.2 Exposición a Internet con ngrok'));

children.push(P('El problema de un n8n local es que los webhooks no son accesibles desde Internet. Telegram no puede mandar mensajes a localhost:5678, y la mini web tampoco puede POSTear ahí si la abro en el móvil fuera de la red de casa. Para eso uso ngrok: registro gratuito, authtoken, y un solo comando levanta un túnel HTTPS que redirige a mi n8n local.'));

children.push(CODE('ngrok http 5678'));

children.push(P('Me devuelve una URL pública tipo https://tapping-widget-entering.ngrok-free.dev que redirige a http://localhost:5678. Con esa URL configuro el webhook de Telegram (con la API del bot) y actualizo las URLs que uso en el ESP32 y la mini web.'));

children.push(H2('4.3 Variables de entorno clave'));

children.push(P('Para que n8n genere las URLs de webhook con la URL pública de ngrok en vez de localhost, añadí tres variables al servicio n8n en docker-compose.yml:'));

children.push(CODE(`- WEBHOOK_URL=https://tapping-widget-entering.ngrok-free.dev
- N8N_HOST=tapping-widget-entering.ngrok-free.dev
- N8N_PROTOCOL=https`));

children.push(P('Después de modificar el fichero, un docker compose down y up para que cojan las nuevas variables. Ya entonces al importar el workflow los paths de los webhooks aparecen con la URL pública correcta.'));

// ==========================================================
// 5. WORKFLOW N8N DETALLADO
// ==========================================================
children.push(H1('5. Workflow n8n detallado'));

children.push(P('El workflow tiene 32 nodos distribuidos en cinco ramas. Las describo por bloques para no hacer la lectura pesada.'));

children.push(H2('5.1 Rama principal (sensores → IA → salidas)'));

children.push(P('Es el recorrido central: llega una lectura del ESP32 y sale una respuesta con análisis IA. 13 nodos.'));

children.push(BULLR([runBold('1. Webhook Sensores ESP32: '), 'punto de entrada para las lecturas. Método POST en la ruta /webhook/estacion-iot. responseMode en "responseNode" para poder devolver al final del flujo el nivel de alerta al ESP32.']));

children.push(BULLR([runBold('2. Validar Datos Sensor (Code): '), 'comprueba los campos obligatorios (temp, hum, luz, presencia), valida rangos, extrae la IP pública del header X-Forwarded-For y lee la ubicación actual del staticData del workflow.']));

children.push(BULLR([runBold('2a. IP Geolocation (HTTP): '), 'llama a ip-api.com con la IP pública del ESP32. Tiene "Continue on fail" activo para que no rompa el flujo si la IP es privada o el servicio no responde.']));

children.push(BULLR([runBold('2b. Merge IP + staticData (Code): '), 'si ya había una ubicación manual en staticData, la mantiene. Si no, y la llamada a ip-api funcionó, usa esas coordenadas y las persiste en staticData para futuras ejecuciones. Esta es la auto-localización.']));

children.push(BULLR([runBold('3. Tiene Ubicacion? (IF): '), 'bifurca entre la rama con ubicación (llamar a Open-Meteo) y la rama sin ubicación (solo datos del sensor).']));

children.push(BULLR([runBold('4. Open-Meteo API (HTTP): '), 'consulta el tiempo actual en esa lat/lon. Sin API key, es gratuito para uso personal.']));

children.push(BULLR([runBold('5. Combinar Interior + Exterior (Code): '), 'fusiona los dos bloques de datos, calcula diferencias de temperatura y humedad, y detecta anomalías con reglas simples (temp alta, humedad alta, diferencia interior/exterior grande, UV alto...).']));

children.push(BULLR([runBold('5b. Sin Ubicación (Code): '), 'versión reducida que se ejecuta cuando no hay ubicación. Aplica las reglas de anomalías que no necesitan datos exteriores.']));

children.push(BULLR([runBold('6. Análisis IA (Groq LLM): '), 'HTTP POST a la API de Groq con prompt system ("eres asistente IoT, responde en español conciso, termina con NIVEL: ...") y prompt user construido a partir de los datos. Modelo llama-3.1-8b-instant, temperature 0.7, max_tokens 250.']));

children.push(BULLR([runBold('7. Parsear Respuesta IA (Code): '), 'extrae el texto del LLM, detecta si contiene VERDE, AMARILLO o ROJO, y prepara el mensaje que se enviará a Telegram.']));

children.push(BULLR([runBold('8. Enviar Telegram (HTTP): '), 'POST a la Bot API de Telegram. Uso Form Urlencoded en vez de JSON porque el texto del LLM tiene saltos de línea y caracteres que rompían el escape del JSON body.']));

children.push(BULLR([runBold('9. Google Sheets Log (HTTP): '), 'POST a un Google Apps Script que yo mismo tengo desplegado como web app. Escribe una fila en la hoja. El Apps Script expone también un GET para leer el histórico, que lo usa el chatbot.']));

children.push(BULLR([runBold('10. Responder al ESP32 (Respond to Webhook): '), 'devuelve un JSON con nivel y ciudad. El ESP32 lo recibe como respuesta al POST y actualiza el LED RGB y el OLED.']));

children.push(H2('5.2 Rama de geolocalización web'));

children.push(P('Tres nodos. Un webhook /estacion-iot-geo recibe lat/lon/ciudad desde la mini web HTML, un nodo Code guarda esos valores en staticData (el almacén persistente del workflow) y un nodo Respond to Webhook cierra la llamada con OK.'));

children.push(H2('5.3 Rama chatbot Telegram con embeddings'));

children.push(P('Nueve nodos. Esta rama es la que cubre el requisito de embeddings y le añade una funcionalidad vistosa al proyecto: permite preguntar al bot cosas sobre el histórico.'));

children.push(BULLR([runBold('CHAT 1. Webhook Chatbot: '), 'endpoint al que Telegram envía los mensajes. Configuré el bot para que llame a este webhook usando la Bot API (setWebhook).']));

children.push(BULLR([runBold('CHAT 2. Clasificar (Code): '), 'decide qué tipo de mensaje es: ubicación compartida, comando (/start, /help) o texto libre. Las ubicaciones y comandos se resuelven en línea sin pasar por el LLM.']));

children.push(BULLR([runBold('CHAT 3. Es pregunta? (IF): '), 'bifurca entre el camino de chatbot (si es pregunta) y el de respuesta directa (ubicación/comando).']));

children.push(BULLR([runBold('CHAT 4. Leer histórico Sheets (HTTP): '), 'GET al endpoint del Apps Script con ?action=last&n=50 para traer las últimas 50 lecturas.']));

children.push(BULLR([runBold('CHAT 5. Embedding Gemini (HTTP): '), 'POST a la API de Gemini (generativelanguage.googleapis.com) con el modelo gemini-embedding-001 para calcular el vector semántico de la pregunta del usuario.']));

children.push(BULLR([runBold('CHAT 6. Preparar prompt (Code): '), 'formatea el histórico como texto tabulado y construye un prompt para el LLM. Incluye en los metadatos la dimensión del embedding calculado (solo como referencia de trazabilidad).']));

children.push(BULLR([runBold('CHAT 7. Groq LLM (HTTP): '), 'llama al LLM con el histórico como contexto y la pregunta. Temperatura más baja que en el flujo principal (0.5) para respuestas más factuales.']));

children.push(BULLR([runBold('CHAT 8. Responder Telegram (HTTP): '), 'manda la respuesta al usuario en Telegram.']));

children.push(BULLR([runBold('CHAT 9. Responder directo: '), 'rama para ubicaciones y comandos, responde con un mensaje precomputado por el nodo Clasificar.']));

children.push(P('Sobre los embeddings: en esta iteración el embedding de la pregunta se calcula pero el LLM razona sobre todas las filas del histórico tal cual. Es una versión simplificada. Una evolución natural sería también calcular embedding de cada fila, hacer similitud coseno y pasar al LLM solo las 3 o 5 filas más relevantes. No lo hago porque con 50 filas el LLM aguanta perfectamente el contexto y la precisión de la respuesta es buena.'));

children.push(H2('5.4 Rama de predicción diaria'));

children.push(P('Seis nodos. Es el segundo requisito opcional fuerte que cubro.'));

children.push(BULLR([runBold('FCST 1. Schedule diario 08:00: '), 'trigger cron con expresión "0 8 * * *". Cada mañana a las 8:00 dispara la rama.']));

children.push(BULLR([runBold('FCST 2. Ubicación real (Code): '), 'recupera la ubicación actual del staticData. Si no hay ninguna, lanza un error (se captura por el error handler y manda aviso por Telegram pidiendo que se configure).']));

children.push(BULLR([runBold('FCST 3. Forecast Open-Meteo 24h (HTTP): '), 'consulta la previsión horaria para las próximas 24 horas en esa lat/lon: temperatura, humedad, probabilidad de precipitación e índice UV.']));

children.push(BULLR([runBold('FCST 4. Preparar prompt (Code): '), 'construye un prompt que pide al LLM una predicción corta en español empezando con el día y la ciudad, destacando máxima, mínima, lluvia y UV. Incluye una instrucción específica para que no confunda la ciudad con otra homónima de otro país (al principio me lo confundía con Cartagena de Colombia).']));

children.push(BULLR([runBold('FCST 5. Groq LLM predicción (HTTP): '), 'genera el texto de la predicción.']));

children.push(BULLR([runBold('FCST 6. Enviar Telegram (HTTP): '), 'manda la predicción al chat con la cabecera "PREDICCIÓN DIARIA - Ciudad".']));

children.push(H2('5.5 Manejador de errores'));

children.push(P('Dos nodos. El Error Trigger se dispara cuando cualquier nodo lanza una excepción. En el body llega un objeto con el error y el nodo que falló. Un HTTP Request a Telegram avisa con "ERROR EN ESTACION IoT - Nodo: X - Mensaje: Y". Sin este avisador los errores se quedan en los logs y no te enteras hasta que revisas el panel de ejecuciones.'));

// ==========================================================
// 6. ESP32 Y CONEXIONADO
// ==========================================================
children.push(H1('6. ESP32 y conexionado'));

children.push(H2('6.1 Hardware y entorno de desarrollo'));

children.push(P('La placa es un ESP32 DevKit V1 (30 pines) del kit Elegoo, la misma que usé en la tarea 7. El entorno de desarrollo es PlatformIO en VS Code por coherencia con esa tarea, aunque dejo también una versión lista para Arduino IDE por si alguien prefiere ese flujo.'));

children.push(P('Componentes conectados:'));
children.push(BULL('DHT11 - temperatura (0 a 50 °C) y humedad (20 a 90 %). Comunicación 1-Wire.'));
children.push(BULL('HC-SR501 PIR - detector de movimiento por infrarrojos. Salida digital HIGH cuando detecta.'));
children.push(BULL('HC-SR04 - sensor ultrasónico de distancia. Necesita alimentación a 5 V.'));
children.push(BULL('LDR (fotorresistencia) en divisor de tensión con una R de 10 kΩ. ADC del ESP32.'));
children.push(BULL('OLED SSD1306 0.96" por I2C, dirección 0x3C.'));
children.push(BULL('LED RGB de cátodo común con tres resistencias de 220 Ω.'));
children.push(BULL('Buzzer activo, suena con HIGH directo.'));

children.push(H2('6.2 Conexionado'));

children.push(P('Tabla de conexionado. La columna "Función" explica para qué uso cada pin:'));

children.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [1600, 2400, 5360],
  rows: [
    new TableRow({
      children: [
        cell('ESP32', { bold: true, fill: 'D5E8F0', align: AlignmentType.CENTER, width: { size: 1600, type: WidthType.DXA } }),
        cell('Componente', { bold: true, fill: 'D5E8F0', width: { size: 2400, type: WidthType.DXA } }),
        cell('Conexión / Función', { bold: true, fill: 'D5E8F0', width: { size: 5360, type: WidthType.DXA } }),
      ],
      tableHeader: true,
    }),
    ...[
      ['GPIO 4', 'DHT11 DATA', 'GPIO 4 → pin S del DHT11. VCC a 3V3, GND a GND.'],
      ['GPIO 15', 'HC-SR501 OUT', 'GPIO 15 → pin OUT del PIR. VCC a 3V3, GND a GND.'],
      ['GPIO 34', 'LDR (ADC)', 'Divisor: LDR entre 3V3 y GPIO34, R 10 kΩ entre GPIO34 y GND.'],
      ['GPIO 5', 'HC-SR04 TRIG', 'Pulso de 10 µs para medir.'],
      ['GPIO 18', 'HC-SR04 ECHO', 'Ancho del pulso proporcional a la distancia.'],
      ['5V (VIN)', 'HC-SR04 VCC', 'El HC-SR04 no funciona bien a 3.3 V, necesita 5 V.'],
      ['GPIO 21', 'OLED SDA', 'I2C datos, pin por defecto.'],
      ['GPIO 22', 'OLED SCL', 'I2C reloj, pin por defecto.'],
      ['GPIO 2', 'LED R (+R 220)', 'GPIO 2 → R 220 → ánodo R → cátodo común → GND.'],
      ['GPIO 16', 'LED G (+R 220)', 'GPIO 16 → R 220 → ánodo G → cátodo común → GND.'],
      ['GPIO 17', 'LED B (+R 220)', 'GPIO 17 → R 220 → ánodo B → cátodo común → GND.'],
      ['GPIO 19', 'Buzzer +', 'Pin + a GPIO 19, pin - a GND.'],
      ['3V3', 'Alimentación', 'DHT11, PIR, LDR, OLED.'],
      ['GND', 'Masa común', 'Todos los componentes.'],
    ].map(([esp, comp, con]) => new TableRow({
      children: [
        cell(esp, { width: { size: 1600, type: WidthType.DXA } }),
        cell(comp, { width: { size: 2400, type: WidthType.DXA } }),
        cell(con, { width: { size: 5360, type: WidthType.DXA } }),
      ],
    })),
  ],
}));

children.push(P('Elegí los GPIO esquivando los que dan problemas de boot en el ESP32. GPIO 0 y GPIO 15 pueden afectar al arranque si están en HIGH, pero GPIO 15 como entrada con el PIR en reposo no da problema. El GPIO 2 tiene un LED integrado en la placa, así que cuando se enciende el rojo también parpadea el azul integrado.'));

children.push(H2('6.3 Esquema visual'));

if (fs.existsSync(IMG_ESQUEMA)) {
  children.push(new Paragraph({
    children: [new ImageRun({
      type: 'png',
      data: fs.readFileSync(IMG_ESQUEMA),
      transformation: { width: 600, height: 400 },
      altText: { title: 'Esquema de cableado', description: 'Esquema de conexiones del ESP32 con todos los sensores', name: 'esquema' },
    })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 120 },
  }));
  children.push(new Paragraph({
    children: [new TextRun({ text: 'Figura 1. Esquema de cableado de la estación IoT.', font: FONT, size: 20, italics: true, color: '666666' })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 240 },
  }));
}

children.push(H2('6.4 Lógica del firmware'));

children.push(P('El bucle principal hace lo siguiente cada 30 segundos:'));
children.push(BULL('Lee los cuatro sensores.'));
children.push(BULL('Actualiza la pantalla OLED con los valores y la ciudad actual.'));
children.push(BULL('Construye un JSON y lo envía por HTTP POST al webhook de n8n.'));
children.push(BULL('Parsea la respuesta y actualiza el LED RGB (y el buzzer si el nivel es ROJO).'));

children.push(P('Entre lecturas el ESP32 atiende peticiones en un pequeño servidor HTTP propio en el puerto 80. Eso permite consultar el estado actual vía /estado o forzar un cambio de alerta vía /alerta desde la misma red local. Es útil como fallback si n8n no responde.'));

// ==========================================================
// 7. GEOLOCALIZACION
// ==========================================================
children.push(H1('7. Geolocalización'));

children.push(P('El sistema necesita saber dónde está para pedir datos meteorológicos reales al exterior. Probé varias opciones y al final monté un sistema con tres niveles de prioridad:'));

children.push(H2('7.1 Tres fuentes de ubicación'));

children.push(BULLR([runBold('Nivel 1 - Configuración manual (preferida): '), 'el usuario comparte su ubicación desde la mini web HTML o envía un mensaje de localización al bot de Telegram. El workflow guarda lat/lon/ciudad en el staticData.']));

children.push(BULLR([runBold('Nivel 2 - Geolocalización por IP (auto, fallback): '), 'si no hay ubicación manual configurada, el workflow extrae la IP pública del header X-Forwarded-For de la petición del ESP32, llama a ip-api.com con esa IP y obtiene una ubicación aproximada. Luego guarda esos valores en staticData para que las siguientes ejecuciones ya los tengan.']));

children.push(BULLR([runBold('Nivel 3 - Sin ubicación (último recurso): '), 'si ni la manual ni la IP están disponibles, el flujo salta la consulta a Open-Meteo y trabaja solo con datos interiores. La IA sigue analizando lo que hay.']));

children.push(H2('7.2 Por qué este orden de prioridad'));

children.push(P('La IP geolocation es útil pero imprecisa: puede acertar la ciudad o desviarse hasta otra provincia según el ISP. Mi IP residencial de Movistar en Cartagena en las pruebas daba Barcelona una de cada cinco veces porque el ISP tiene infraestructura allí. Por eso la manual siempre gana. Probé también Google WiFi Geolocation pero requiere activar facturación en Google Cloud (aunque el tier gratuito cubre 40.000 peticiones al mes), así que lo descarté para este proyecto.'));

// ==========================================================
// 8. GOOGLE SHEETS VIA APPS SCRIPT
// ==========================================================
children.push(H1('8. Google Sheets vía Apps Script'));

children.push(P('Para el histórico uso una hoja de Google Sheets llamada "Estación IoT" con 11 columnas. Lo lógico sería usar el nodo Google Sheets nativo de n8n, pero necesita OAuth de Google configurado en la instancia y no es trivial desde el Docker self-hosted.'));

children.push(P('La alternativa que uso es un Google Apps Script desplegado como web app en mi propia cuenta. Es un mini backend en JavaScript que corre en los servidores de Google y escribe en la hoja directamente, sin pasar por OAuth externo. El script expone dos endpoints:'));

children.push(BULLR([runBold('doPost: '), 'recibe un JSON desde n8n y añade una fila a la hoja. Limpia los posibles "=" que a veces n8n deja al principio de los valores (un bug que encontré depurando y que si no limpio hace que Sheets interprete los valores como fórmulas).']));

children.push(BULLR([runBold('doGet: '), 'expone tres acciones vía querystring. ?action=last&n=50 devuelve las últimas N filas, ?action=all las todas, ?action=stats genera un resumen. Lo usa el chatbot de la rama de embeddings para traer el histórico.']));

// ==========================================================
// 9. ANALISIS IA CON GROQ LLM Y EMBEDDINGS GEMINI
// ==========================================================
children.push(H1('9. Análisis IA: Groq LLM y embeddings Gemini'));

children.push(H2('9.1 Por qué Groq y llama-3.1-8b-instant'));

children.push(P('Para generación de texto necesitaba un modelo rápido, gratuito y compatible con el formato OpenAI (porque n8n se integra bien con esa interfaz). Probé tres opciones: Ollama local, Gemini y Groq.'));

children.push(BULLR([runBold('Ollama local: '), 'descartado porque requiere NGrok también y un modelo cargado en mi PC. Como el proyecto ya tiene suficientes capas, preferí una API externa.']));

children.push(BULLR([runBold('Google Gemini: '), 'tier gratuito generoso pero latencia algo mayor (800-1500 ms) y la API difiere ligeramente del estándar OpenAI.']));

children.push(BULLR([runBold('Groq: '), 'tier gratuito, compatibilidad OpenAI total, latencias muy bajas (100-300 ms) y varios modelos Llama disponibles. Este gana.']));

children.push(P('Dentro de Groq elegí llama-3.1-8b-instant porque es rápido, responde bien en español y es suficiente para la tarea de clasificar datos y generar una recomendación breve. Uso temperature 0.7 para que el texto salga natural y max_tokens 250 para acotar.'));

children.push(H2('9.2 Por qué Gemini para embeddings'));

children.push(P('Groq no tiene endpoint de embeddings. Tenía que usar otro servicio. Opciones: OpenAI (de pago), Ollama (requería correr un modelo embedding adicional localmente) y Gemini (tier gratuito, API key sencilla de obtener desde aistudio.google.com).'));

children.push(P('El modelo elegido es gemini-embedding-001. Genera vectores de 768 dimensiones, rápido y suficiente para el tipo de preguntas cortas del chatbot. La API es un POST a generativelanguage.googleapis.com con la API key en el header X-goog-api-key.'));

children.push(P('Ahora mismo el embedding de la pregunta se calcula pero no lo uso para hacer similitud coseno en el código. Lo aprovecha el LLM como contexto junto con el histórico completo. Es una simplificación consciente: con 50 filas de histórico el LLM gestiona bien el contexto y la latencia sigue siendo baja. Una evolución natural sería guardar embeddings de cada fila en Qdrant (que ya tengo corriendo en Docker pero sin usar) y hacer similitud antes de pasar al LLM.'));

children.push(H2('9.3 Prompts'));

children.push(P('El prompt del análisis principal:'));

children.push(CODE(`Eres un asistente IoT. Analizas lecturas de sensores (interior) y datos meteo (exterior). Responde en espanol, max 3 frases. Termina con NIVEL: [VERDE/AMARILLO/ROJO].`));

children.push(P('El prompt del chatbot con embeddings:'));

children.push(CODE(`Histórico de la estación IoT (N lecturas):
[listado tabulado con fecha, ciudad, valores interior, valores exterior, alerta]

Pregunta: <pregunta del usuario>

Responde en español, conciso (max 4 frases), citando datos cuando sea relevante.`));

children.push(P('El prompt de la predicción diaria:'));

children.push(CODE(`Eres un asistente IoT. Genera una prediccion breve (max 4 frases) para hoy en <Ciudad>.
Coordenadas reales: lat=..., lon=...
Pronostico 24h (cada 3h): [listado por horas]
Destaca: maxima/minima, lluvia, UV, recomendacion practica. Empieza con el dia y la ciudad.
NO inventes datos que no esten en el pronostico.
NO confundas la ciudad con otra homonima en otro pais.`));

children.push(P('La última instrucción ("no confundas con otra homónima") vino después de que el LLM me diera una predicción para Cartagena de Indias en Colombia en vez de Cartagena, Murcia. Añadí la aclaración explícita y ya no vuelve a pasar.'));

// ==========================================================
// 10. INSTALACION Y PUESTA EN MARCHA
// ==========================================================
children.push(H1('10. Instalación y puesta en marcha'));

children.push(H2('10.1 Requisitos previos'));

children.push(BULL('Cuenta de Telegram con un bot creado vía @BotFather (token del bot y chat_id propio).'));
children.push(BULL('Cuenta de Groq con API key (console.groq.com).'));
children.push(BULL('Cuenta de Google con API key de Gemini (aistudio.google.com/apikey).'));
children.push(BULL('Cuenta de Google con una hoja de Google Sheets vacía llamada "Estación IoT".'));
children.push(BULL('Docker Desktop instalado.'));
children.push(BULL('Cuenta de ngrok gratuita (authtoken).'));
children.push(BULL('ESP32 DevKit V1 con los componentes del kit Elegoo.'));
children.push(BULL('VS Code con PlatformIO (o Arduino IDE) para compilar el firmware.'));

children.push(H2('10.2 Pasos de instalación'));

children.push(new Paragraph({ children: [new TextRun({ text: '1. Levantar n8n local con Docker', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Clonar self-hosted-ai-starter-kit de GitHub, editar docker-compose.yml con las tres variables WEBHOOK_URL, N8N_HOST y N8N_PROTOCOL (apuntando a la URL de ngrok que obtendremos en el paso siguiente), y lanzar docker compose up -d.'));

children.push(new Paragraph({ children: [new TextRun({ text: '2. Exponer n8n con ngrok', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Instalar ngrok, configurar el authtoken con ngrok config add-authtoken <token>, y lanzar ngrok http 5678. Copiar la URL pública que devuelve.'));

children.push(new Paragraph({ children: [new TextRun({ text: '3. Configurar Telegram', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Crear bot con @BotFather, copiar token, mandarle un mensaje, y obtener el chat_id desde la API getUpdates. Configurar el webhook del bot con setWebhook apuntando a <url-ngrok>/webhook/estacion-iot-chatbot.'));

children.push(new Paragraph({ children: [new TextRun({ text: '4. Desplegar el Apps Script', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Abrir Google Sheets, Extensiones → Apps Script, pegar Code.gs, desplegar como web app con acceso "Cualquiera", copiar la URL.'));

children.push(new Paragraph({ children: [new TextRun({ text: '5. Importar el workflow en n8n', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Entrar en el n8n local en localhost:5678, crear workflow, pegar el JSON del workflow. Revisar los nodos Groq (API key), Gemini (API key), Telegram (token y chat_id) y Google Sheets (URL del Apps Script). Publish.'));

children.push(new Paragraph({ children: [new TextRun({ text: '6. Compilar y subir el firmware al ESP32', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Editar main.cpp con WIFI_SSID, WIFI_PASSWORD y N8N_WEBHOOK_URL. Compilar y subir con PlatformIO.'));

children.push(new Paragraph({ children: [new TextRun({ text: '7. Configurar la ubicación', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Opcionalmente, abrir la mini web geolocalizacion.html en el móvil y compartir la ubicación. Si no se hace, el sistema usará la IP pública del ESP32 para auto-localizar.'));

children.push(new Paragraph({ children: [new TextRun({ text: '8. Verificar', font: FONT, size: 22, bold: true })], spacing: { before: 120, after: 80 } }));
children.push(P('Esperar 30 segundos después de encender el ESP32. Debería llegar un mensaje al Telegram con los datos y el análisis, y una fila nueva en Google Sheets.'));

// ==========================================================
// 11. PROBLEMAS ENCONTRADOS Y SOLUCIONES
// ==========================================================
children.push(H1('11. Problemas encontrados y soluciones'));

children.push(P('Los listo en el orden en que aparecieron. Varios vinieron de cosas que no había encontrado en los tutoriales y tuve que depurar paso a paso.'));

children.push(H2('11.1 El nodo Validar recibía los datos vacíos'));

children.push(P('El JSON del POST llegaba al webhook correctamente (se veía en la preview) pero el nodo Code inmediatamente después decía "campos faltantes: temp, hum, luz, presencia". Resulta que en esta versión de n8n el body a veces queda en $input.first().json directamente y otras veces anidado en $input.first().json.body. Se arregla con un OR:'));

children.push(CODE(`const input = $input.first().json;
const datos = input.body || input.data || input;`));

children.push(H2('11.2 API key de Groq rechazada'));

children.push(P('Pegué la key, dio "Authorization failed". Al revisar vi que había copiado un carácter extra al principio. Regeneré una nueva, la pegué limpia y funcionó. No parece gran cosa pero perdí 15 minutos.'));

children.push(H2('11.3 El nodo Parsear Respuesta IA fallaba por "nodo no ejecutado"'));

children.push(P('Intentaba leer datos de "5. Combinar Interior + Exterior", pero la ejecución había ido por la rama "5b. Sin Ubicación" porque no tenía ubicación configurada. Intentar acceder con $() a un nodo no ejecutado lanza una excepción que no puedes atrapar con un simple try. Lo arreglé con try/catch anidados:'));

children.push(CODE(`let datosAnteriores;
try { datosAnteriores = $('5. Combinar Interior + Exterior').first().json; }
catch(e) {
  try { datosAnteriores = $('5b. Sin Ubicacion (solo sensor)').first().json; }
  catch(e2) { datosAnteriores = {}; }
}`));

children.push(H2('11.4 Nodo Telegram: "JSON parameter needs to be valid JSON"'));

children.push(P('Al mandar el texto del LLM en el body JSON del HTTP Request, los saltos de línea, comillas y asteriscos rompían el parseo. Probé varias cosas (JSON.stringify en la expresión, fetch desde Code, $http) pero ninguna estaba disponible en esta versión. La solución que me funciona es cambiar el body a Form Urlencoded y meter los parámetros como Body Fields. n8n se encarga del escape al serializar. Curiosamente la Bot API de Telegram acepta perfectamente form-urlencoded.'));

children.push(H2('11.5 Google Sheets guardaba #ERROR! y #NAME?'));

children.push(P('Los primeros tests guardaban celdas con errores raros. Al clickar en la celda veía que el valor empezaba por "=" y Sheets lo interpretaba como fórmula. El motivo era que las expresiones de n8n con prefijo "=" a veces dejan ese carácter en el valor serializado. Lo arreglé en el Apps Script: antes de escribir cada valor, si empieza por "=", lo elimina. Así los textos se guardan como texto plano.'));

children.push(H2('11.6 Google Sheets devolvía "connection aborted"'));

children.push(P('El nodo de lectura de Sheets fallaba con "connection aborted, perhaps the server is offline". Era porque Google Apps Script responde con un redirect 302 y el nodo HTTP Request por defecto no lo seguía. Lo arreglé activando "Follow All Redirects" en Options y subiendo el timeout a 30000 ms.'));

children.push(H2('11.7 El modelo de embeddings de Google no existía'));

children.push(P('Empecé usando text-embedding-004 porque lo había leído en un tutorial, pero daba 404. Google había renombrado el modelo a gemini-embedding-001 y además requiere pasar también el campo "model" dentro del body JSON (no solo en la URL). Con los dos cambios, la API respondió a la primera.'));

children.push(H2('11.8 Cartagena de Indias en vez de Cartagena, Murcia'));

children.push(P('La predicción diaria empezó a hablar de Cartagena, Colombia. El LLM no tenía manera de saber a cuál de las dos me refería porque el prompt solo decía "Cartagena". Añadí en el nodo de ubicación que si la ciudad no tiene coma (ni país), le concatene ", España". Y añadí al prompt una instrucción explícita: "NO confundas la ciudad con otra homónima en otro país". Desde entonces siempre acierta.'));

children.push(H2('11.9 El servidor de n8n del profesor se cayó'));

children.push(P('Mientras hacía las últimas pruebas, la instancia de progian8n.duckdns.org dejó de responder. Como ya había avanzado mucho, migré todo a mi propio n8n self-hosted con el kit oficial de n8n y expuse el webhook con ngrok. Tardé un buen rato (sobre todo con las variables de entorno para que n8n genere las URLs de webhook con la pública de ngrok en vez de localhost) pero al final el proyecto quedó más robusto: ya no depende del servidor del profesor.'));

children.push(H2('11.10 staticData no persistía entre ejecuciones manuales y la schedule'));

children.push(P('Cuando metía una ubicación por web y luego lanzaba manualmente la rama de predicción desde el editor, el staticData aparecía vacío. Al principio pensé que había un bug de n8n pero por lo que leí es el comportamiento esperado: staticData solo persiste entre ejecuciones "productivas" (triggers reales), no desde el botón Execute del editor. En producción funciona porque la rama principal del ESP32 rellena staticData cada 30 segundos con la IP geolocation, y el schedule de las 8:00 usa el que quedó guardado.'));

// ==========================================================
// 12. CONCLUSIONES
// ==========================================================
children.push(H1('12. Conclusiones'));

children.push(P('El proyecto cumple los requisitos del enunciado y añade tres mejoras que suben bastante la nota: chatbot con embeddings, predicción diaria y auto-localización por IP. Lo que más me ha aportado a nivel de aprendizaje es montar una cadena completa que une hardware real con servicios en la nube y un modelo LLM, respondiendo todo dentro del mismo bucle, y luego poder migrar toda esa infraestructura de un servidor externo a mi propio Docker sin romper nada.'));

children.push(P('Algunas reflexiones:'));

children.push(BULL('n8n es potente pero tiene aristas que solo descubres cuando te topas con ellas (body.body, expresiones con "=" que se propagan, redirecciones HTTP no seguidas por defecto, staticData que depende del tipo de trigger). Una vez sabido, es rápido iterar.'));
children.push(BULL('Groq es una alternativa muy atractiva a las APIs comerciales para prototipos. El tier gratuito es generoso y la latencia es mejor que Gemini o OpenAI.'));
children.push(BULL('Cuando combinas varios servicios, el bug más probable no está en ninguno de ellos sino en el formato en que intercambian datos. He perdido más tiempo depurando problemas de serialización y redirecciones que escribiendo lógica propia.'));
children.push(BULL('Tener desde el principio un manejador de errores que avisa por Telegram ha sido clave. Sin él, muchos fallos se habrían quedado enterrados en los logs del servidor.'));
children.push(BULL('El kit self-hosted-ai-starter-kit es una puerta de entrada excelente al stack de n8n + Ollama + Qdrant. Aunque solo uso n8n de los tres, tener el resto ya levantado me abre camino a futuras iteraciones.'));

children.push(P('Lo siguiente que haría sería convertir el prompt del LLM en un agente con varias herramientas (consulta al histórico de Sheets para comparar con lecturas pasadas, consulta a la previsión meteorológica del día en lugar de solo al momento actual), usar Qdrant de verdad para los embeddings y añadir memoria conversacional al chatbot. Todo eso ya sería otra tarea.'));

// ==========================================================
// 13. BIBLIOGRAFIA
// ==========================================================
children.push(H1('13. Bibliografía y referencias'));

children.push(H2('13.1 Documentación técnica'));

children.push(BULLR([new TextRun({ text: 'n8n documentation - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://docs.n8n.io/', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://docs.n8n.io/' })]));
children.push(BULLR([new TextRun({ text: 'self-hosted-ai-starter-kit - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://github.com/n8n-io/self-hosted-ai-starter-kit', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://github.com/n8n-io/self-hosted-ai-starter-kit' })]));
children.push(BULLR([new TextRun({ text: 'Groq API - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://console.groq.com/docs/quickstart', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://console.groq.com/docs/quickstart' })]));
children.push(BULLR([new TextRun({ text: 'Gemini embeddings - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://ai.google.dev/gemini-api/docs/embeddings', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://ai.google.dev/gemini-api/docs/embeddings' })]));
children.push(BULLR([new TextRun({ text: 'Open-Meteo API - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://open-meteo.com/en/docs', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://open-meteo.com/en/docs' })]));
children.push(BULLR([new TextRun({ text: 'Telegram Bot API - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://core.telegram.org/bots/api', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://core.telegram.org/bots/api' })]));
children.push(BULLR([new TextRun({ text: 'ip-api.com - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://ip-api.com/docs', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://ip-api.com/docs' })]));
children.push(BULLR([new TextRun({ text: 'Nominatim (OpenStreetMap) - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://nominatim.org/release-docs/latest/api/Overview/', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://nominatim.org/release-docs/latest/api/Overview/' })]));
children.push(BULLR([new TextRun({ text: 'Google Apps Script web apps - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://developers.google.com/apps-script/guides/web', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://developers.google.com/apps-script/guides/web' })]));
children.push(BULLR([new TextRun({ text: 'ngrok documentation - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://ngrok.com/docs', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://ngrok.com/docs' })]));

children.push(H2('13.2 ESP32 y sensores'));

children.push(BULLR([new TextRun({ text: 'ESP32 Arduino Core - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://docs.espressif.com/projects/arduino-esp32/', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://docs.espressif.com/projects/arduino-esp32/' })]));
children.push(BULLR([new TextRun({ text: 'Adafruit DHT sensor library - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://github.com/adafruit/DHT-sensor-library', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://github.com/adafruit/DHT-sensor-library' })]));
children.push(BULLR([new TextRun({ text: 'Adafruit SSD1306 OLED - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://github.com/adafruit/Adafruit_SSD1306', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://github.com/adafruit/Adafruit_SSD1306' })]));
children.push(BULLR([new TextRun({ text: 'ArduinoJson - ', font: FONT, size: 22 }), new ExternalHyperlink({ children: [new TextRun({ text: 'https://arduinojson.org/', font: FONT, size: 22, style: 'Hyperlink' })], link: 'https://arduinojson.org/' })]));

children.push(H2('13.3 Material de clase'));

children.push(BULL('Apuntes de la Unidad 9 - Automatización de procesos y agentes IA (n8n_teoria.docx).'));
children.push(BULL('Enunciado de la tarea (n8n_tarea_practica.docx).'));
children.push(BULL('Código de la tarea 7 como referencia de estilo y arquitectura (control IoT de LEDs con MQTT).'));

// ================== DOCUMENT BUILD ==================
const doc = new Document({
  creator: 'autor',
  title: 'Tarea Unidad 9 - Estacion IoT con n8n',
  description: 'Documento tecnico de la tarea 9',
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 32, bold: true, font: FONT, color: '2E3A87' },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 26, bold: true, font: FONT, color: '444444' },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 },
      },
      {
        id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: FONT, color: '666666' },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: 'bullets',
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [new TextRun({ text: 'Tarea Unidad 9 - Estación IoT con n8n', font: FONT, size: 18, color: '888888' })],
          alignment: AlignmentType.RIGHT,
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            new TextRun({ text: 'autor - Pág. ', font: FONT, size: 18, color: '888888' }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: '888888' }),
          ],
          alignment: AlignmentType.CENTER,
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUT_PATH, buffer);
  console.log('OK: ' + OUT_PATH);
  console.log('Tam: ' + buffer.length + ' bytes');
});
