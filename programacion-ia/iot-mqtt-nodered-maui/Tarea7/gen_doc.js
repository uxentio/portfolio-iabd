import {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType, PageBreak,
  HeadingLevel, LevelFormat, ImageRun, TableLayoutType,
  VerticalAlign, convertInchesToTwip, TableOfContents,
} from "docx";
import * as fs from "fs";

/* ── helpers ─────────────────────────────────────────────────────── */

// Colores accesibles: evitar contraste extremo (BDA Style Guide)
// Negro puro sobre blanco puro causa fatiga visual
const BLUE1 = "1A5276";
const BLUE2 = "2471A3";
const GRAY  = "4D4D4D";  // oscurecido para cumplir WCAG AA (4.5:1 sobre crema)
const BLACK = "2D2D2D";        // gris muy oscuro en vez de negro puro (BDA)
const WHITE = "FFFFF0";        // crema/hueso en vez de blanco puro (BDA)
const HDR_FILL = "D5E8F0";
const BORDER_CLR = "BBBBBB";
const CODE_BG = "F5F5EB";      // crema claro para código
const CODE_BORDER = "D5D5C5";
const FONT = "Atkinson Hyperlegible";  // Braille Institute: disenada para máxima legibilidad, formas únicas b/d/p/q/I/l/1/O/0
const CODE_FONT = "Consolas";
const BODY_SIZE = 28;          // 14pt -- mínimo recomendado BDA para dislexia
const CODE_SIZE = 22;          // 11pt -- legible para bloques de código

const thinBorder = (color = BORDER_CLR) => ({
  style: BorderStyle.SINGLE, size: 1, color,
});
const noBorder = { style: BorderStyle.NONE, size: 0, color: WHITE };
const tableBorders = {
  top: thinBorder(), bottom: thinBorder(), left: thinBorder(), right: thinBorder(),
  insideHorizontal: thinBorder(), insideVertical: thinBorder(),
};
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function p(text, opts = {}) {
  const {
    bold, italic, size, color, font, alignment, spacing, heading,
    break: brk, underline, style,
  } = opts;
  const run = new TextRun({
    text,
    bold: bold || false,
    italics: italic || false,
    size: size || BODY_SIZE,
    color: color || BLACK,
    font: font || FONT,
    underline: underline ? {} : undefined,
    break: brk,
  });
  const pOpts = { children: [run] };
  if (alignment) pOpts.alignment = alignment;
  if (spacing) pOpts.spacing = spacing;
  if (heading) pOpts.heading = heading;
  if (style) pOpts.style = style;
  return new Paragraph(pOpts);
}

function multiRunParagraph(runs, opts = {}) {
  return new Paragraph({
    children: runs.map(r => {
      if (r instanceof TextRun || r instanceof ImageRun) return r;
      return new TextRun({
        text: r.text || "",
        bold: r.bold || false,
        italics: r.italic || false,
        size: r.size || BODY_SIZE,
        color: r.color || BLACK,
        font: r.font || FONT,
        break: r.break,
      });
    }),
    ...opts,
  });
}

function heading1(text) {
  return p(text, {
    style: "Heading1",
    bold: true, size: 56, color: BLUE1,
    spacing: { before: 400, after: 240 },
    alignment: AlignmentType.LEFT,
  });
}

function heading2(text) {
  return p(text, {
    style: "Heading2",
    bold: true, size: 44, color: BLUE2,
    spacing: { before: 280, after: 180 },
    alignment: AlignmentType.LEFT,
  });
}

// Interlineado 1.5 = 360 twips (240 twips = single spacing)
// Alineacion izquierda siempre (BDA: nunca justificado, crea "rios blancos")
const LINE_SPACING = { line: 360, lineRule: "atLeast" };

function bodyText(text, opts = {}) {
  return p(text, {
    size: BODY_SIZE, spacing: { after: 140, ...LINE_SPACING },
    alignment: AlignmentType.LEFT, ...opts,
  });
}

function codeBlock(code) {
  const lines = code.split("\n");
  const children = [];
  lines.forEach((line, i) => {
    if (i > 0) children.push(new TextRun({ text: "", break: 1, font: CODE_FONT, size: CODE_SIZE }));
    children.push(new TextRun({ text: line, font: CODE_FONT, size: CODE_SIZE, color: "333333" }));
  });
  const codeBorder = { style: BorderStyle.SINGLE, size: 1, color: CODE_BORDER };
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 9360, type: WidthType.DXA },
            shading: { type: ShadingType.CLEAR, fill: CODE_BG, color: CODE_BG },
            borders: {
              top: codeBorder, bottom: codeBorder, left: codeBorder, right: codeBorder,
            },
            margins: { top: 100, bottom: 100, left: 160, right: 160 },
            children: [new Paragraph({ children, spacing: { after: 0 } })],
          }),
        ],
      }),
    ],
  });
}

function dataTable(headers, rows, colWidths) {
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) =>
      new TableCell({
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: HDR_FILL, color: HDR_FILL },
        borders: {
          top: thinBorder(), bottom: thinBorder(), left: thinBorder(), right: thinBorder(),
        },
        margins: cellMargins,
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: h, bold: true, size: BODY_SIZE, font: FONT, color: BLUE1 })],
        })],
      })
    ),
  });

  const dataRows = rows.map(row =>
    new TableRow({
      children: row.map((cell, i) =>
        new TableCell({
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: WHITE, color: WHITE },
          borders: {
            top: thinBorder(), bottom: thinBorder(), left: thinBorder(), right: thinBorder(),
          },
          margins: cellMargins,
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            children: [new TextRun({ text: cell, size: BODY_SIZE, font: FONT })],
          })],
        })
      ),
    })
  );

  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    borders: tableBorders,
    rows: [headerRow, ...dataRows],
  });
}

function bulletList(items) {
  return items.map(text => new Paragraph({
    children: [new TextRun({ text, size: BODY_SIZE, font: FONT, color: BLACK })],
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 80, ...LINE_SPACING },
    alignment: AlignmentType.LEFT,
  }));
}

// Cada numberedList() necesita su propia referencia, porque si todas comparten
// la misma "numbers", docx sigue contando entre listas distintas y me queda
// "19, 20, 21..." en vez de "1, 2, 3...". Genero una referencia nueva por llamada.
let numberedListCounter = 0;
const extraNumberingRefs = [];

function numberedList(items) {
  numberedListCounter++;
  const ref = `numbers_${numberedListCounter}`;
  extraNumberingRefs.push({
    reference: ref,
    levels: [{
      level: 0,
      format: LevelFormat.DECIMAL,
      text: "%1.",
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } },
    }],
  });
  return items.map(text => new Paragraph({
    children: [new TextRun({ text, size: BODY_SIZE, font: FONT, color: BLACK })],
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80, ...LINE_SPACING },
    alignment: AlignmentType.LEFT,
  }));
}

function placeholder(text) {
  // BDA: evitar cursiva
  return p(text, { color: GRAY, spacing: { after: 140 } });
}

function spacer(after = 120) {
  return new Paragraph({ children: [], spacing: { after } });
}

/* ── read images ─────────────────────────────────────────────────── */

const BASE = "D:/2526-1BDAT-Programaci\u00f3n para IA/UNIDAD 8/Tarea7";

function loadImg(name) {
  try { return fs.readFileSync(`${BASE}/${name}`); }
  catch { return null; }
}

const diagramImageData   = loadImg("diagrama_arquitectura.png");
const imgLmStudio        = loadImg("captura_lmstudio.png");
const imgMauiApp         = loadImg("captura_maui_app.png");
const imgMauiChat        = loadImg("captura_maui_chat.png");
const imgNodeRed         = loadImg("captura_nodered.png");
const imgEsp32           = loadImg("captura_esp32.png");
const imgMontaje         = loadImg("captura_montaje.png");

function imgParagraph(data, w, h, caption) {
  const children = [];
  if (data) {
    children.push(new Paragraph({
      children: [new ImageRun({ data, transformation: { width: w, height: h }, type: "png" })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
    }));
    if (caption) {
      // BDA: evitar cursiva, usar texto normal o negrita para enfasis
      children.push(p(caption, { bold: false, size: 24, color: GRAY, alignment: AlignmentType.CENTER, spacing: { after: 180 } }));  // 12pt mínimo (BDA)
    }
  } else {
    children.push(placeholder(`[No se encontr\u00f3 la imagen -- ${caption || "insertar captura"}]`));
  }
  return children;
}

/* ── COVER PAGE ──────────────────────────────────────────────────── */

const coverChildren = [
  spacer(2400),
  p("Control IoT con Lenguaje Natural", {
    bold: true, size: 64, color: BLUE1, alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
  }),
  p("Integraci\u00f3n .NET MAUI, LM Studio, Node-RED y MQTT", {
    size: 32, color: BLUE2, alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
  }),
  new Paragraph({
    children: [],
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: BLUE2 } },
  }),
  spacer(200),
  p("Tarea 7 - Programaci\u00f3n de Inteligencia Artificial", {
    size: 26, alignment: AlignmentType.CENTER, spacing: { after: 80 },
  }),
  p("CE en Inteligencia Artificial y Big Data", {
    size: 26, alignment: AlignmentType.CENTER, spacing: { after: 80 },
  }),
  p("autor Mart\u00ednez", {
    bold: true, size: 28, alignment: AlignmentType.CENTER, spacing: { after: 80 },
  }),
  p("Abril 2026", {
    size: 26, alignment: AlignmentType.CENTER, spacing: { after: 80 },
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

/* ── AVISO DE ACCESIBILIDAD ──────────────────────────────────────── */

const accessNotice = [
  p("Nota sobre el formato de este documento", {
    bold: true, size: 32, color: BLUE1,
    spacing: { before: 200, after: 200 },
    alignment: AlignmentType.LEFT,
  }),
  bodyText("He formateado este documento pensando en que sea f\u00e1cil de leer (yo mismo tengo TEA y TDAH, y me pasa que los documentos densos me saturan). Me baso en estas fuentes:"),
  ...bulletList([
    "Gu\u00eda de estilo de la British Dyslexia Association (BDA): https://www.bdadyslexia.org.uk/advice/employers/creating-a-dyslexia-friendly-workplace/dyslexia-friendly-style-guide",
    "Pautas de accesibilidad web WCAG 2.1, criterios 1.4.8 y 1.4.12: https://www.w3.org/WAI/WCAG21/",
    "Recomendaciones de la National Autistic Society sobre comunicaci\u00f3n escrita: https://www.autism.org.uk/advice-and-guidance/topics/communication",
  ]),
  bodyText("En concreto he aplicado esto:", { bold: true }),
  ...bulletList([
    "Tipograf\u00eda Atkinson Hyperlegible a 14 puntos -- hecha por el Braille Institute para que se distingan bien letras parecidas (b/d, p/q, I/l/1, O/0)",
    "Interlineado de 1,5 l\u00edneas -- la BDA recomienda un m\u00ednimo de 1,5 para reducir la p\u00e9rdida de l\u00ednea durante la lectura",
    "Alineaci\u00f3n a la izquierda, nunca justificada -- el texto justificado crea espacios irregulares entre palabras (\u201cr\u00edos blancos\u201d) que dificultan el seguimiento visual",
    "Fondo color crema en vez de blanco puro -- el contraste extremo blanco/negro causa estr\u00e9s visual seg\u00fan la BDA",
    "Sin cursivas -- las letras inclinadas pierden su forma caracter\u00edstica y son m\u00e1s dif\u00edciles de distinguir para lectores con dislexia. Se usa negrita para el \u00e9nfasis",
    "P\u00e1rrafos cortos (3-5 frases m\u00e1ximo) y uso de listas con vi\u00f1etas siempre que es posible",
    "Estructura predecible con secciones numeradas e \u00edndice de contenidos -- la consistencia y previsibilidad benefician especialmente a personas con TEA",
  ]),
  new Paragraph({ children: [new PageBreak()] }),
];

/* ── INDICE DE CONTENIDOS ───────────────────────────────────────── */

const tocSection = [
  p("\u00cdndice de contenidos", {
    bold: true, size: 40, color: BLUE1,
    spacing: { before: 200, after: 300 },
    alignment: AlignmentType.LEFT,
  }),
  new TableOfContents("\u00cdndice", {
    hyperlink: true,
    headingStyleRange: "1-2",
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

/* ── SECTION 1: Introduccion ────────────────────────────────────── */

const secIntro = [
  heading1("1. Introducci\u00f3n"),
  bodyText("Esta tarea plantea construir una aplicaci\u00f3n en la que el usuario interact\u00faa con un modelo de lenguaje (LLM) ejecutado en local, y ese modelo, a trav\u00e9s del mecanismo de function calling, termina controlando un dispositivo f\u00edsico. En mi caso el dispositivo es una placa ESP32 con tres LEDs y una pantalla OLED, y el modelo puede pedirle que encienda, apague, regule o haga secuencias con esas luces."),
  bodyText("El flujo es en cadena: la app MAUI env\u00eda el mensaje del usuario al LLM; si la respuesta es una llamada a herramienta, el resultado se manda por HTTP a un flujo Node-RED; Node-RED publica el comando por MQTT al ESP32; y el ESP32 aplica los estados a los LEDs y devuelve una confirmaci\u00f3n por otro topic MQTT. Todo el procesado de lenguaje natural corre en local, sin servicios externos."),
  bodyText("Adem\u00e1s de la app, el mismo control se expone a trav\u00e9s de un servidor MCP (Model Context Protocol) en un proyecto .NET aparte, de forma que clientes como Claude Desktop pueden invocar la misma herramienta sin pasar por la interfaz gr\u00e1fica."),
];

/* ── SECTION 2: Objetivos ───────────────────────────────────────── */

const secObjetivos = [
  heading1("2. Objetivos"),
  bodyText("Los objetivos que me he marcado en el proyecto son:"),
  ...bulletList([
    "Ejecutar un modelo de lenguaje en local sin depender de servicios en la nube.",
    "Aprender a usar function calling con modelos peque\u00f1os (menos de 1B de par\u00e1metros) y ver sus limitaciones.",
    "Construir una aplicaci\u00f3n .NET MAUI multiplataforma con patr\u00f3n MVVM.",
    "Integrar una pasarela Node-RED y el protocolo MQTT como capa entre la app y el hardware.",
    "Dise\u00f1ar el firmware de la ESP32 para que acepte combinaciones de estados complejas (brillo, parpadeos a distintas velocidades, secuencias y c\u00f3digo morse) sin bloquear el bucle principal.",
    "Exponer el mismo control mediante un servidor MCP compatible con clientes externos.",
    "Dejar todo documentado y reproducible por otra persona con las instrucciones de este documento.",
  ]),
];

/* ── SECTION 3: Arquitectura general ───────────────────────────── */

const secArquitectura = [
  heading1("3. Arquitectura general"),
  bodyText("El sistema tiene cinco piezas que se comunican en cadena: la aplicaci\u00f3n MAUI (cliente), LM Studio (servidor local del modelo), Node-RED (pasarela HTTP a MQTT), un broker MQTT p\u00fablico y la ESP32 (dispositivo)."),
  bodyText("La app es el \u00fanico punto de contacto con el usuario. Cuando el usuario escribe o dicta algo, la app lo manda a LM Studio a trav\u00e9s de su API compatible con OpenAI, junto con la definici\u00f3n de la herramienta controlar_luces. Si el modelo responde con una llamada a esa herramienta, la app interpreta los par\u00e1metros y env\u00eda por POST un JSON a Node-RED. Node-RED empaqueta ese JSON y lo publica en un topic MQTT al que la ESP32 est\u00e1 suscrita. El firmware parsea el JSON y aplica los estados a los LEDs mediante PWM, y opcionalmente dispara secuencias autom\u00e1ticas (sem\u00e1foro, ola, morse). Por \u00faltimo, la ESP32 publica en un segundo topic (ACK) un resumen de lo que ha aplicado."),
  bodyText("En paralelo, el proyecto LucesIoT.MCP expone la misma herramienta a trav\u00e9s del protocolo MCP sobre STDIO, reutilizando el mismo flujo Node-RED \u2192 MQTT \u2192 ESP32. As\u00ed el ESP32 recibe \u00f3rdenes indistintamente desde la app o desde cualquier cliente MCP."),
  ...imgParagraph(diagramImageData, 600, 340, "Figura: arquitectura general del sistema (cliente, LLM, pasarela, dispositivo)"),
];

/* ── SECTION 4: Modelo LLM ───────────────────────────────────────── */

const secModelLLM = [
  heading1("4. Modelo LLM utilizado y configuraci\u00f3n"),

  heading2("4.1 LM Studio"),
  bodyText("Para correr el LLM en local he usado LM Studio (https://lmstudio.ai). La gracia es que levanta una API compatible con la de OpenAI en localhost:1234, as\u00ed que desde la app hago peticiones HTTP normales como si fuera OpenAI de verdad, pero todo se queda en mi ordenador sin mandar datos a ning\u00fan servidor externo."),
  bodyText("Mir\u00e9 tambi\u00e9n Ollama (https://ollama.com), que hace lo mismo y tiene buena documentaci\u00f3n, pero LM Studio tiene interfaz gr\u00e1fica para gestionar modelos, cambiar par\u00e1metros y ver logs en tiempo real. Eso para ir probando va mucho mejor. Adem\u00e1s lo hab\u00eda usado en tareas anteriores y ya me mov\u00eda bien por \u00e9l."),

  heading2("4.2 Elecci\u00f3n del modelo"),
  bodyText("En esta parte me tir\u00e9 un buen rato investigando. El ejemplo del enunciado usaba un modelo gen\u00e9rico con 2 herramientas (on/off) pero no dec\u00eda cu\u00e1l. Yo empec\u00e9 con Qwen 2.5 7B Instruct, que es bastante popular para llamadas a funciones. Funcionaba, pero en mi equipo iba lent\u00edsimo. Varios segundos para cada respuesta, con 7 mil millones de par\u00e1metros se nota mucho."),
  bodyText("Buscando otra cosa encontr\u00e9 una comparativa en jdhodges.com (https://www.jdhodges.com/blog/local-llms-on-tool-calling-2026-pt1-local-lm/) donde probaron 13 modelos locales en 40 casos de test. Qwen3.5 4B sac\u00f3 el mejor resultado: un 97,5% de acierto, por encima de modelos mucho m\u00e1s grandes. Intent\u00e9 cargar el 4B pero mi equipo no lo soporta (LM Studio me daba un error raro de c\u00f3digo de salida desbordado), as\u00ed que me baj\u00e9 al 0.8B de Unsloth."),
  bodyText("El 0.8B pesa 1,21 GB en formato GGUF (un formato optimizado para ejecutar modelos en local) con cuantizaci\u00f3n Q8_0 (t\u00e9cnica que reduce el tama\u00f1o del modelo sin perder mucha calidad). Para mi herramienta con 3 par\u00e1metros de tipo enum (on/off/blink) va de sobra: el modelo s\u00f3lo tiene que rellenar tres campos con valores de una lista cerrada."),
  bodyText("Referencia del modelo: https://lmstudio.ai/models/qwen3 y la gu\u00eda de Unsloth: https://unsloth.ai/docs/models/qwen3.5"),
  bodyText("Tambi\u00e9n vi otro art\u00edculo en mayhemcode.com (https://www.mayhemcode.com/2026/03/best-models-for-lm-studio-llama-4-qwen3.html) que compara los mejores modelos para LM Studio y confirma que Qwen3.5 destaca en llamada a herramientas frente a Llama 4 y Mistral."),

  bodyText("Configuraci\u00f3n:", { bold: true }),
  ...bulletList([
    "Temperatura: 0.7 -- lo t\u00edpico para que las respuestas no sean siempre id\u00e9nticas",
    "Transmisi\u00f3n continua (stream): desactivada -- la respuesta llega de una vez, lo cual facilita parsear el JSON completo",
    "tool_choice: \"required\" cuando detecto que el mensaje tiene pinta de comando de luces. Esto obliga al modelo a usar una herramienta s\u00ed o s\u00ed, en vez de responder con texto tipo \"claro, voy a encender la luz roja\". Al principio no pon\u00eda esto y el modelo a veces no llamaba a la herramienta",
  ]),

  ...imgParagraph(imgLmStudio, 560, 320, "Figura 1: LM Studio con Qwen3.5 0.8B cargado y servidor activo"),

  heading2("4.3 System prompt"),
  bodyText("El system prompt me cost\u00f3 varias vueltas. La primera versi\u00f3n era m\u00e1s suave y el modelo a veces responde con texto tipo \u201cvale, ahora enciendo\u201d en vez de llamar a la herramienta. Acab\u00e9 poni\u00e9ndole \u201cREGLA OBLIGATORIA\u201d en may\u00fasculas y \u201cNUNCA respondas s\u00f3lo con texto\u201d en negrita mental, porque seg\u00fan la documentaci\u00f3n de Qwen sobre function calling (https://qwen.readthedocs.io/en/latest/framework/function_call.html), los modelos peque\u00f1os necesitan que se lo dejes muy clarito para que lo hagan siempre."),
  codeBlock(`Eres un asistente IoT que controla 3 luces f\u00edsicas (verde, roja, azul).
Tienes UNA SOLA herramienta: controlar_luces, con estos par\u00e1metros:
 - verde, roja, azul: estado de cada luz, uno de: "off", "on", "dim"
   (tenue), "blink" (parpadeo 400ms), "fast" (150ms), "slow" (1s),
   "fade" (sube y baja suave).
 - modo_especial: opcional, uno de "ninguno" (por defecto),
   "semaforo", "ola", "morse". Si pones semaforo/ola/morse, los
   estados de verde/roja/azul se ignoran.
 - texto_morse: s\u00f3lo si modo_especial=morse, el texto a emitir.
 - color_morse: s\u00f3lo si modo_especial=morse, en qu\u00e9 LED emitir.
REGLA OBLIGATORIA: cuando el usuario pida tocar luces, SIEMPRE llama a
controlar_luces. Mapeo de intenciones: "tenue/suave/bajito" -> dim;
"r\u00e1pido" -> fast; "lento" -> slow; "respira/pulsa/fade" -> fade;
"parpadea" -> blink; "encendida/fija" -> on; "apagada" -> off.
Si dice "sem\u00e1foro" -> modo_especial=semaforo.
Si dice "la ola" -> modo_especial=ola.
Si dice "morse" o "emite XXX en morse" -> modo_especial=morse,
texto_morse=XXX.
Si pregunta algo no relacionado con luces, responde en texto normal.`),
  bodyText("Es m\u00e1s largo que el primero que ten\u00eda porque hay que explicarle las combinaciones y el mapeo de intenciones. Si digo \u201cenciende la verde y pon la roja intermitente\u201d tiene que deducir verde=on, roja=blink, azul=off. El bloque de mapeo de intenciones (tenue->dim, r\u00e1pido->fast...) es clave porque el usuario nunca dice \u201cdim\u201d o \u201cfade\u201d en castellano natural, dice \u201ctenue\u201d o \u201crespira\u201d, y el modelo peque\u00f1o necesita que se lo dejes clarito."),
];

/* ── SECTION 2: Tools ────────────────────────────────────────────── */

const secTool = [
  heading1("5. Configuraci\u00f3n de la herramienta (tool)"),
  bodyText("El ejemplo base del enunciado ten\u00eda 2 herramientas sin par\u00e1metros (turn_on_light y turn_off_light). Mi primera versi\u00f3n ten\u00eda 4 (una por color m\u00e1s apagar). Cuando me puse a combinar cosas (dos encendidas, una parpadeando y otra fija, apagar s\u00f3lo una...) me di cuenta de que con herramientas separadas no pod\u00eda hacerlo. As\u00ed que lo refactoric\u00e9 a una \u00fanica herramienta con par\u00e1metros, que es un patr\u00f3n mucho m\u00e1s potente de function calling."),
  bodyText("La herramienta se llama controlar_luces y tiene 3 par\u00e1metros principales (verde, roja, azul), cada uno con 7 estados distintos: off, on, dim (tenue), blink (parpadeo 400ms), fast (r\u00e1pido 150ms), slow (lento 1s) y fade (sube y baja suave). Adem\u00e1s he a\u00f1adido unos par\u00e1metros opcionales para activar modos autom\u00e1ticos como sem\u00e1foro, ola o emitir texto en c\u00f3digo morse, pero sigue siendo UNA \u00fanica herramienta. Seg\u00fan la documentaci\u00f3n de OpenAI sobre function calling (https://platform.openai.com/docs/guides/function-calling), que es la API que LM Studio replica, puedes definir par\u00e1metros con enum para limitar los valores posibles. Eso ayuda mucho al modelo peque\u00f1o porque no tiene que inventar nada, s\u00f3lo elegir de la lista."),

  bodyText("Par\u00e1metros de controlar_luces:", { bold: true }),
  dataTable(
    ["Par\u00e1metro", "Tipo", "Valores posibles", "Prop\u00f3sito"],
    [
      ["verde, roja, azul", "string", "off, on, dim, blink, fast, slow, fade", "Estado de cada LED (obligatorio)"],
      ["modo_especial",    "string", "ninguno, semaforo, ola, morse",          "Si no es 'ninguno' se ignoran los 3 anteriores"],
      ["texto_morse",      "string", "letras A-Z, n\u00fameros, espacios (max 30)", "S\u00f3lo si modo_especial=morse"],
      ["color_morse",      "string", "verde, roja, azul",                      "S\u00f3lo si modo_especial=morse: por qu\u00e9 LED emitir"],
    ],
    [2000, 1200, 3300, 2860],
  ),
  spacer(),

  bodyText("Ejemplos de lo que puede hacer:", { bold: true }),
  dataTable(
    ["El usuario dice", "Argumentos que elige el modelo"],
    [
      ["\"enciende la verde\"", "verde=on, roja=off, azul=off"],
      ["\"pon la azul tenue y la roja parpadeando r\u00e1pido\"", "verde=off, roja=fast, azul=dim"],
      ["\"haz que la verde respire\"", "verde=fade, roja=off, azul=off"],
      ["\"verde parpadeo lento, roja r\u00e1pido, azul fija\"", "verde=slow, roja=fast, azul=on"],
      ["\"activa el modo sem\u00e1foro\"", "modo_especial=semaforo"],
      ["\"haz la ola\"", "modo_especial=ola"],
      ["\"emite SOS en morse por la roja\"", "modo_especial=morse, texto_morse=SOS, color_morse=roja"],
      ["\"apaga todo\"", "verde=off, roja=off, azul=off"],
    ],
    [4000, 5360],
  ),
  spacer(),

  bodyText("El JSON de la herramienta (simplificado):", { bold: true }),
  codeBlock(`{
  "type": "function",
  "function": {
    "name": "controlar_luces",
    "description": "Controla las 3 luces. Si modo_especial no es 'ninguno' se activa el modo y se ignoran verde/roja/azul.",
    "parameters": {
      "type": "object",
      "properties": {
        "verde": { "type": "string", "enum": ["off","on","dim","blink","fast","slow","fade"] },
        "roja":  { "type": "string", "enum": ["off","on","dim","blink","fast","slow","fade"] },
        "azul":  { "type": "string", "enum": ["off","on","dim","blink","fast","slow","fade"] },
        "modo_especial": { "type": "string", "enum": ["ninguno","semaforo","ola","morse"] },
        "texto_morse":   { "type": "string" },
        "color_morse":   { "type": "string", "enum": ["verde","roja","azul"] }
      },
      "required": ["verde", "roja", "azul"]
    }
  }
}`),
  spacer(),

  bodyText("Para parsear la respuesta uso System.Text.Json, que ya viene con .NET y no necesita NuGet extra. El ejemplo del enunciado usaba Newtonsoft.Json, pero seg\u00fan Microsoft (https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/overview) el que viene de serie es m\u00e1s r\u00e1pido y es el recomendado. Ahora, adem\u00e1s del nombre de la funci\u00f3n, tengo que sacar los argumentos. Los argumentos vienen como un string JSON dentro del JSON de la respuesta (s\u00ed, JSON anidado), as\u00ed que hay que parsearlos aparte:"),
  codeBlock(`// Saco los argumentos del tool_call
string argsJson = firstCall.GetProperty("function")
    .GetProperty("arguments").GetString() ?? "{}";
using var args = JsonDocument.Parse(argsJson);

// miro primero si el LLM ha elegido un modo especial
string modo = LeerCampo(args.RootElement, "modo_especial", ModosEspeciales, "ninguno");
if (modo == "semaforo" || modo == "ola")   return new LmStudioResult { Preset = modo };
if (modo == "morse") { /* saco texto_morse y color_morse */ }

// si no hay modo especial, leo los 3 LEDs normales
var ledStates = new Dictionary<string, string>
{
    ["verde"] = LeerEstado(args.RootElement, "verde"),
    ["roja"]  = LeerEstado(args.RootElement, "roja"),
    ["azul"]  = LeerEstado(args.RootElement, "azul")
};
// LeerEstado/LeerCampo validan contra la lista de estados permitidos
// y normalizan tildes, as\u00ed si el modelo devuelve "encendido" o "\u00d3N" lo mando a off`),
  spacer(),

  bodyText("Uso TryGetProperty con valor por defecto \"off\" por si el modelo se deja alg\u00fan par\u00e1metro sin rellenar. Con el enum cerrado es raro que pase, pero por si acaso no quiero que pete."),
  bodyText("Sobre el tool_choice: cuando detecto que el usuario quiere tocar luces (busco palabras como \u201cenciende\u201d, \u201capaga\u201d, \u201cluz\u201d, \u201cintermitente\u201d, \u201cparpadea\u201d...) fuerzo tool_choice = \"required\". Si parece pregunta (\u201c\u00bfqu\u00e9 luces puedes controlar?\u201d) lo dejo en auto. Sin esto me pas\u00f3 que el modelo contestaba \u201cclaro, voy a encender la verde\u201d pero no llamaba a la herramienta y el LED no se encend\u00eda."),
];

/* ── SECTION 3: .NET MAUI ────────────────────────────────────────── */

const secMAUI = [
  heading1("6. Aplicaci\u00f3n .NET MAUI"),

  heading2("6.1 Por qu\u00e9 MVVM y por qu\u00e9 CommunityToolkit"),
  bodyText("El enunciado pide MVVM. Hay varias formas de hacer MVVM en .NET MAUI, pero el ejemplo base ten\u00eda todo en el archivo de detr\u00e1s de la vista (lo que se conoce como code-behind, el MainWindow.xaml.cs de turno), que es exactamente lo contrario de MVVM. As\u00ed que tocaba reorganizarlo."),
  bodyText("He elegido CommunityToolkit.Mvvm (https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/) porque es el que recomienda Microsoft, y sobre todo porque genera c\u00f3digo autom\u00e1ticamente con source generators (generadores de c\u00f3digo en tiempo de compilaci\u00f3n) y te ahorra escribir INotifyPropertyChanged a mano, que es un rollo. Con los atributos [ObservableProperty] y [RelayCommand] escribes la mitad de c\u00f3digo. Ya lo hab\u00eda usado en tareas anteriores y va bien."),
  bodyText("Mir\u00e9 tambi\u00e9n Prism (https://prismlibrary.com/), que es un framework m\u00e1s completo, pero tambi\u00e9n m\u00e1s pesado. Para una app con dos pantallas no merec\u00eda la pena."),

  heading2("6.2 Estructura del proyecto"),
  dataTable(
    ["Carpeta", "Archivos", "Para qu\u00e9 sirve"],
    [
      ["Models/", "ChatMessage.cs", "Datos de cada mensaje: texto, si es del usuario, timestamp"],
      ["Services/", "LmStudioService.cs", "Comunicaci\u00f3n con LM Studio: env\u00eda mensajes con la herramienta controlar_luces y parsea los argumentos JSON que devuelve"],
      ["Services/", "NodeRedService.cs", "Env\u00eda por HTTP POST a Node-RED los estados de las 3 luces o activa un preset (semaforo)"],
      ["ViewModels/", "MainViewModel.cs", "L\u00f3gica principal: chat, LEDs visuales, comandos por voz, botones manuales. Aqu\u00ed est\u00e1 toda la l\u00f3gica que en el ejemplo base estaba en el c\u00f3digo trasero de la vista"],
      ["ViewModels/", "SettingsViewModel.cs", "Ajustes de la app: URLs, modelo, broker (intermediario) MQTT. Consulta la API de LM Studio para listar los modelos disponibles"],
      ["Views/", "MainPage.xaml", "Pantalla principal con chat, LEDs y barra de entrada"],
      ["Views/", "SettingsPage.xaml", "Formulario de configuraci\u00f3n"],
      ["Converters/", "BoolToAlignmentConverter.cs", "Converters de XAML para alinear mensajes (derecha para usuario, izquierda para bot) y color del micro"],
      ["(ra\u00edz)", "MauiProgram.cs", "Inyecci\u00f3n de dependencias: registra HttpClient, servicios, ViewModels y p\u00e1ginas"],
    ],
    [1500, 2600, 5260],
  ),
  spacer(),

  bodyText("La inyecci\u00f3n de dependencias va en MauiProgram.cs. Los servicios como Singleton (una sola instancia) para que no se pierda el historial al navegar entre p\u00e1ginas, y los ViewModels como Transient (se crea una instancia nueva cada vez que se necesitan). Al principio los ten\u00eda todos Transient y cada vez que iba a Ajustes y volv\u00eda me quedaba sin historial de chat. Esto de los tipos de vida lo aclara la docu de MAUI (https://learn.microsoft.com/en-us/dotnet/maui/fundamentals/dependency-injection)."),

  heading2("6.3 LmStudioService: c\u00f3mo habla la app con el modelo"),
  bodyText("LmStudioService habla con LM Studio por HTTP. Al principio tenia guardado un historial de conversacion que se mandaba entero al modelo con cada petición, como se hace normalmente en un chat, para que recordase el contexto."),

  bodyText("Pero probandolo me encontre con un problema serio: con un modelo tan pequeño (0.8B parámetros) el historial le liaba. Cuando la conversacion llevaba 10-15 mensajes, el modelo empezaba a mezclar respuestas anteriores con la nueva. Por ejemplo, si antes le habia dicho \u201cactiva el modo semaforo\u201d y después le pedia \u201cemite SOS en morse\u201d, me respondia \u201cHe activado el modo semaforo\u201d otra vez, porque esa era la última acción del historial y se quedaba enganchado ahi. Probe con distintas frases, reinicie, forcze tool_choice, y aún así pasaba."),

  bodyText("El motivo técnico es que los modelos pequeños tienen menos \u201ccapacidad de atención\u201d: el mecanismo de attention del transformer funciona peor con contextos largos porque los pesos son limitados. Un modelo grande (como los de OpenAI o Qwen 4B) maneja fácilmente 20-30 mensajes sin perderse. Un modelo de 0.8B se atasca antes."),

  bodyText("La solución que acabe poniendo fue mandar al LLM solo el system prompt y el mensaje actual del usuario. Nada de historial. Cada comando se interpreta en aislado y el modelo responde limpio. El trade-off: el modelo no puede hacer referencias a lo anterior (no entiende \u201cpon la verde igual que estaba antes\u201d), pero a cambio es mucho mas fiable. Para este caso de uso (control de luces por comandos atomicos) es la decisión correcta."),

  bodyText("El historial sigue existiendo en la app, pero solo para pintarlo en el chat de la UI: así el usuario ve sus mensajes anteriores y las respuestas, que es lo que espera de una interfaz de chat. Lo que cambia es que ese historial no se manda al LLM."),
  bodyText("SendAsync monta la petici\u00f3n al endpoint /v1/chat/completions (documentaci\u00f3n de la API en https://lmstudio.ai/docs/api). Antes de mandarla hace una detecci\u00f3n: mira si el mensaje tiene pinta de comando (\u201cenciende\u201d, \u201capaga\u201d, \u201cintermitente\u201d, \u201cparpadea\u201d...) o de pregunta (signo de interrogaci\u00f3n, \u201cqu\u00e9\u201d, \u201cpuedes\u201d...). Si parece comando, fuerza tool_choice = \"required\" para que el modelo rellene los par\u00e1metros s\u00ed o s\u00ed. Si es pregunta, lo deja en auto:"),
  codeBlock(`// busco palabras clave: acciones, colores, modos y presets
bool tienePalabrasLuz =
    msgLower.Contains("encien") || msgLower.Contains("apaga") ||
    msgLower.Contains("prende") || msgLower.Contains("luz")   ||
    msgLower.Contains("led")    || msgLower.Contains("roj")   ||
    msgLower.Contains("verde")  || msgLower.Contains("azul")  ||
    msgLower.Contains("intermiten") || msgLower.Contains("blink")   ||
    msgLower.Contains("parpadea")   || msgLower.Contains("fij")     ||
    msgLower.Contains("tenue")      || msgLower.Contains("suave")   ||
    msgLower.Contains("rapido")     || msgLower.Contains("lento")   ||
    msgLower.Contains("respira")    || msgLower.Contains("pulsa")   ||
    msgLower.Contains("fade")       || msgLower.Contains("semaforo") ||
    msgLower.Contains("brillo")     || msgLower.Contains(" ola")    ||
    msgLower.Contains("morse");

bool esPregunta = msgLower.Contains("?") || msgLower.Contains("qu\u00e9")
    || msgLower.Contains("puedes") || msgLower.Contains("c\u00f3mo");

bool esComandoLuz = tienePalabrasLuz && !esPregunta;`),
  spacer(),

  bodyText("Esto me pas\u00f3: sin la detecci\u00f3n de preguntas, cuando preguntaba \u201c\u00bfqu\u00e9 luces puedes controlar?\u201d el modelo encend\u00eda una al azar en vez de contestarme. Porque yo le hab\u00eda puesto tool_choice = required para todo. La soluci\u00f3n fue mirar antes si era pregunta y no forzarle nada."),

  bodyText("Al parsear la respuesta tengo que sacar los argumentos. Como ya expliqu\u00e9 en la secci\u00f3n 2, vienen como JSON anidado. Monto un Dictionary<string, string> con las claves verde, roja, azul y si alguna falta pongo off por defecto."),

  heading2("6.4 MainViewModel: lo que pasa al darle a Enviar"),
  bodyText("MainViewModel conecta la interfaz con los servicios. Al pulsar Enviar se ejecuta SendAsync: a\u00f1ade tu mensaje al chat (la ObservableCollection que pinta los mensajes), llama a LM Studio, y seg\u00fan lo que venga hace una cosa u otra:"),
  codeBlock(`var result = await _lmStudioService.SendAsync(input);

if (result.IsToolCall)
    await ProcesarToolCall(result.LedStates!);
else
    Messages.Add(new ChatMessage { Text = result.TextResponse, IsUser = false });`),
  spacer(),

  bodyText("ProcesarToolCall recibe el diccionario con los 3 estados (por ejemplo verde=on, roja=blink, azul=off), actualiza los LEDs de la interfaz y manda el JSON a Node-RED:"),
  codeBlock(`private async Task ProcesarToolCall(Dictionary<string, string> ledStates)
{
    _currentStates = new Dictionary<string, string>(ledStates);
    SetLedsFromStates(ledStates);
    bool ok = await _nodeRedService.SendCommandAsync(ledStates);
    // ... mensaje al chat y haptic feedback
}`),
  spacer(),

  bodyText("SetLedsFromStates pone cada LED en su color con opacidad alta (encendido) o gris con opacidad baja (apagado). Si alg\u00fan LED est\u00e1 en blink, arranco un DispatcherTimer que lo alterna cada 400ms entre color vivo y gris, para que el efecto visual de parpadeo se vea en la app. El timer lo paro y lo vuelvo a crear cada vez que llega un estado nuevo, si no se acumulan y parpadea a lo loco."),

  bodyText("Ahora pueden estar varios LEDs encendidos a la vez, o uno fijo y otro parpadeando, o los tres intermitentes. Todo lo decide el modelo con los 3 par\u00e1metros."),

  heading2("6.5 Comandos por voz"),
  bodyText("Esto no lo pide el enunciado pero me apetec\u00eda meterlo. Uso CommunityToolkit.Maui (https://learn.microsoft.com/en-us/dotnet/communitytoolkit/maui/) porque ya ten\u00eda CommunityToolkit.Mvvm del mismo paquete y la integraci\u00f3n es inmediata. No hace falta claves de API ni depender de nada externo."),
  bodyText("Mir\u00e9 Azure Speech Services pero te obliga a tener cuenta y clave, Vosk va offline pero engancharlo a MAUI era un l\u00edo, y la API nativa de Windows s\u00f3lo vale en Windows. El del CommunityToolkit lo resuelve todo sin dramas."),
  bodyText("Lo fuerzo a espa\u00f1ol (es-ES) porque si no a veces me detectaba palabras en ingl\u00e9s y la l\u00edaba. Mientras hablas va mostrando lo que reconoce, y al terminar se manda al LLM s\u00f3lo:"),
  codeBlock(`var options = new SpeechToTextOptions
{
    Culture = CultureInfo.GetCultureInfo("es-ES"),
    ShouldReportPartialResults = true
};
await speechToText.StartListenAsync(options);`),
  spacer(),

  bodyText("Los permisos de micro me dieron guerra. En Windows la primera vez pide permiso y ya. En Android tienes que a\u00f1adir RECORD_AUDIO al AndroidManifest.xml o la app petar\u00e1 al pulsar el micro. Lo explica la docu de permisos de MAUI (https://learn.microsoft.com/en-us/dotnet/maui/platform-integration/appmodel/permissions)."),

  heading2("6.6 Interfaz de usuario"),
  bodyText("La interfaz es oscura, tipo panel de control IoT. Me gusta que la pinta acompa\u00f1e a lo que hace la app. A la izquierda el chat con estilo terminal (fondo casi negro, texto claro), a la derecha los tres c\u00edrculos que se iluminan con un halo (la Shadow de MAUI) cuando se enciende el LED. Arriba un panel con informaci\u00f3n del sistema: modelo cargado, broker y topic. Abajo un log con la \u00faltima acci\u00f3n."),
  bodyText("La barra de entrada tiene tres cosas: el campo de texto, un bot\u00f3n de micro para la voz, y Enviar. Los mensajes del usuario salen en azul a la derecha y los del bot en gris a la izquierda. Lo de la alineaci\u00f3n se hace con un Converter de XAML, el BoolToAlignmentConverter, que mira el IsUser del mensaje y devuelve Start o End."),
  bodyText("Debajo tengo cuatro botones manuales (verde, roja, azul y apagar todas) para poder probar el sistema sin depender del LLM. Los tres de colores funcionan como un ciclo de 3 estados: primer clic enciende, segundo clic pone en intermitente, tercer clic apaga. Cada bot\u00f3n s\u00f3lo afecta a su color, as\u00ed que puedo combinar estados a mano (por ejemplo verde encendida + roja parpadeando + azul apagada) dando clics independientes. El bot\u00f3n Apagar manda las tres a off de golpe. Esto me salv\u00f3 la vida al depurar: pod\u00eda comprobar el enlace app-Node-RED-ESP32 sin tener que lanzar LM Studio cada vez."),
  ...imgParagraph(imgMauiApp, 560, 320, "Figura 2: App MAUI con la luz roja encendida tras comando por chat"),
  ...imgParagraph(imgMauiChat, 560, 320, "Figura 3: Conversaci\u00f3n extendida con m\u00faltiples comandos de luces"),
];

/* ── SECTION 4: Node-RED ─────────────────────────────────────────── */

const secNodeRed = [
  heading1("7. Node-RED"),

  heading2("7.1 Por qu\u00e9 Node-RED"),
  bodyText("Node-RED lo pone el enunciado como intermediario entre la app y MQTT. Podr\u00eda publicar directamente desde la app con MQTTnet, pero as\u00ed tengo una capa intermedia que puedo tocar sin recompilar la app. Si ma\u00f1ana quiero a\u00f1adir un log, un filtro o mandar a dos brokers, lo hago en Node-RED arrastrando un nodo y ya. Y como expone un endpoint HTTP, lo puedo probar con curl sin levantar nada de .NET."),
  bodyText("Node-RED es de la fundaci\u00f3n OpenJS (https://nodered.org/). Se instala con npm y se configura en el navegador arrastrando nodos, que para un visual como yo va bien."),

  heading2("7.2 El flujo"),
  bodyText("El flujo tiene 5 nodos y es bastante directo:"),
  dataTable(
    ["Nodo", "Tipo", "Funci\u00f3n"],
    [
      ["POST /encender", "HTTP IN", "Recibe las peticiones POST de la app MAUI"],
      ["Preparar JSON", "Function", "Convierte el objeto JSON a string para publicarlo en MQTT tal cual"],
      ["Publicar MQTT", "MQTT OUT", "Publica en test.mosquitto.org:1883, topic iabd2425/esp32/led"],
      ["Respuesta HTTP", "HTTP Response", "Devuelve 200 a la app para que sepa que lleg\u00f3"],
      ["Debug (depuraci\u00f3n)", "Debug", "Muestra el comando en la consola de Node-RED"],
    ],
    [2200, 2200, 4960],
  ),
  spacer(),

  bodyText("El nodo Function:", { bold: true }),
  codeBlock(`// convierte el objeto a string JSON para que MQTT lo publique tal cual
// el ESP32 espera: {"verde":"on","roja":"off","azul":"blink"}
msg.payload = JSON.stringify(msg.payload);
return msg;`),
  spacer(),

  heading2("7.3 Broker MQTT"),
  bodyText("Uso el broker p\u00fablico test.mosquitto.org en el puerto 1883, sin usuario ni contrase\u00f1a. Es el que sale en el enunciado y el que todo el mundo usa para trastear (https://test.mosquitto.org/). Ojo que se cae de vez en cuando, sobre todo los fines de semana. Como respaldo tengo apuntado broker.hivemq.com por si acaso."),
  bodyText("El topic es iabd2425/esp32/led. Da igual el nombre, lo importante es que la app y la ESP32 est\u00e9n hablando en el mismo, que si no no se entera nadie."),
  ...imgParagraph(imgNodeRed, 560, 300, "Figura 4: Flujo Node-RED con los 5 nodos (HTTP IN, Function, MQTT OUT, HTTP Response, Debug)"),
];

/* ── Architecture diagram ────────────────────────────────────────── */

// (el diagrama de arquitectura ya se inserta en la sección 3, aqui no hace falta repetirlo)
const diagramSection = [];

/* ── SECTION 5: ESP32 ────────────────────────────────────────────── */

const secESP32 = [
  heading1("8. ESP32 y conexionado"),

  heading2("8.1 Hardware y por qu\u00e9 PlatformIO"),
  bodyText("Uso una ESP32 DevKit V1 real, no simulaci\u00f3n, enchufada por USB. El firmware lo escribo con PlatformIO (https://platformio.org/) dentro de VS Code, con el framework Arduino."),
  bodyText("Se pod\u00eda hacer con el Arduino IDE, pero PlatformIO me gusta m\u00e1s: las librer\u00edas las declaras en el platformio.ini y se descargan solas, tiene autocompletado de verdad, y ya trabajo en VS Code con todo lo dem\u00e1s, as\u00ed que no me cambio de ventana. La docu oficial para ESP32 est\u00e1 aqu\u00ed: https://docs.platformio.org/en/latest/boards/espressif32/esp32dev.html"),
  bodyText("Adem\u00e1s de los 3 LEDs que pide el enunciado he metido una pantalla OLED SSD1306 de 0,96 pulgadas por I2C, que es la mejora opcional que mencionan (\u201cincluir una pantalla LCD que muestre el mensaje recibido\u201d). Prefer\u00ed una OLED a una LCD porque por I2C (un protocolo de comunicaci\u00f3n serie que usa s\u00f3lo dos cables) s\u00f3lo necesitas dos pines (SDA y SCL) y las LCD paralelas te comen seis o m\u00e1s. Adem\u00e1s la librer\u00eda Adafruit_SSD1306 es muy sencilla y hay mil ejemplos."),

  heading2("8.2 Conexionado"),
  dataTable(
    ["Componente", "Pin GPIO", "Conexi\u00f3n"],
    [
      ["LED Rojo", "GPIO 15", "GPIO 15 -> R 220 Ohm -> \u00c1nodo -> C\u00e1todo -> GND"],
      ["LED Verde", "GPIO 2", "GPIO 2 -> R 220 Ohm -> \u00c1nodo -> C\u00e1todo -> GND"],
      ["LED Azul", "GPIO 4", "GPIO 4 -> R 220 Ohm -> \u00c1nodo -> C\u00e1todo -> GND"],
      ["OLED SDA", "GPIO 21", "I2C datos (pin por defecto de la ESP32)"],
      ["OLED SCL", "GPIO 22", "I2C reloj (pin por defecto de la ESP32)"],
      ["OLED VCC", "VIN (5V)", "Alimentaci\u00f3n"],
      ["OLED GND", "GND", "Tierra com\u00fan"],
    ],
    [2000, 2000, 5360],
  ),
  spacer(),

  bodyText("Los GPIO los eleg\u00ed esquivando los que dan problemas en el arranque de la ESP32 (hay algunos que si est\u00e1n en HIGH durante el boot la placa no arranca, es un cl\u00e1sico). El GPIO 2 ya trae un LED integrado en la placa, as\u00ed que cuando se enciende el verde tambi\u00e9n parpadea el de la placa, que queda hasta simp\u00e1tico. Los pines 21 y 22 son los I2C por defecto seg\u00fan el pinout oficial de la DevKit V1 (https://docs.espressif.com/projects/esp-idf/en/latest/esp32/hw-reference/esp32/get-started-devkitc.html)."),
  bodyText("Las resistencias son de 220 ohmios, el valor t\u00edpico para LEDs a 3,3V. Si echas n\u00fameros: R = (Vgpio - Vled) / Iled = (3,3 - 2,0) / 0,005 = 260 ohm. 220 se queda un pel\u00edn por debajo pero est\u00e1 dentro del rango seguro y es lo que ten\u00eda en el kit."),
  ...imgParagraph(imgEsp32, 520, 400, "Figura 5: Esquema de conexionado ESP32 con 3 LEDs, resistencias y pantalla OLED (KiCad)"),
  ...imgParagraph(imgMontaje, 340, 400, "Figura 6: Montaje real en protoboard — ESP32, OLED SSD1306 y 3 LEDs con resistencias"),

  heading2("8.3 Setup: WiFi, MQTT y OLED"),
  bodyText("El setup() hace las cosas en orden. Primero Wire.begin(SDA, SCL) arranca el bus I2C en los pines 21 y 22, y display.begin() enciende la OLED en la direcci\u00f3n 0x3C. Esa direcci\u00f3n es la que traen casi todos los m\u00f3dulos SSD1306 de 0.96 pulgadas. Si por lo que sea la pantalla no arranca, saco un aviso por Serial y sigo sin ella; lo importante es que los LEDs sigan funcionando aunque la OLED est\u00e9 rota o mal conectada."),
  bodyText("Despu\u00e9s configuro los pines de los LEDs como OUTPUT y los pongo a LOW. As\u00ed al arrancar siempre est\u00e1 todo apagado, aunque la placa haya quedado en un estado raro despu\u00e9s de un reset o un error."),
  bodyText("Luego viene el WiFi. WiFi.begin(ssid, password) y a esperar. Mientras no tiene IP, se queda en un while mostrando puntos en la OLED para que se vea que est\u00e1 intentando conectar. Cuando ya est\u00e1, configura el cliente MQTT con setServer y registra la funci\u00f3n callback, que es la que se ejecutar\u00e1 cada vez que llegue un mensaje al topic al que est\u00e1 suscrito."),

  heading2("8.4 Reconexi\u00f3n MQTT"),
  bodyText("El broker p\u00fablico de mosquitto se cae de vez en cuando, o a veces lo que se corta es el WiFi. En el loop principal miro si el cliente sigue conectado y si no, llamo a reconnect(). Lo clave es que la reconexi\u00f3n es NO BLOQUEANTE: en vez de un while con delay(), uso millis() para reintentar una sola vez cada 3 segundos y vuelvo al loop. As\u00ed los LEDs en blink y el OLED siguen respondiendo mientras busca broker. El client ID lo genero aleatorio con formato ESP32_XXXX (snprintf sobre buffer en pila, no String, para no fragmentar el heap del ESP32)."),
  codeBlock(`unsigned long ultimoReintento = 0;

void reconnect() {
    if (client.connected()) return;
    if (millis() - ultimoReintento < 3000) return;  // reintento cada 3s
    ultimoReintento = millis();

    char cid[20];
    snprintf(cid, sizeof(cid), "ESP32_%04X", (unsigned int)random(0xffff));

    if (client.connect(cid)) {
        client.subscribe(mqttTopic);
    }
    // si falla, vuelvo al loop y reintentara en 3s
}`),
  spacer(),

  heading2("8.5 Callback MQTT: cuando llega un comando"),
  bodyText("La funci\u00f3n callback salta cada vez que llega un mensaje al topic. Antes comparaba strings sueltos (\u201cencender_roja\u201d, \u201capagar\u201d...), ahora llega un JSON con los 3 estados. Lo parseo con ArduinoJson (https://arduinojson.org/v7/tutorial/deserialization/), que es la librer\u00eda de JSON m\u00e1s usada en Arduino y ESP32."),
  bodyText("El payload de MQTT llega como un array de bytes sin terminador \\0, as\u00ed que primero lo copio a un buffer con terminador. Despu\u00e9s deserializeJson lo parsea y saco cada estado. Si falta alg\u00fan campo pongo off por defecto:"),
  codeBlock(`void callback(char* topic, byte* payload, unsigned int length) {
    char buf[256];
    memcpy(buf, payload, length < 255 ? length : 255);
    buf[length < 255 ? length : 255] = '\\0';

    JsonDocument doc;  // ArduinoJson v7, sin tamanio fijo
    DeserializationError err = deserializeJson(doc, buf);
    if (err) return;  // JSON roto, ignorar

    // tres ramas posibles segun lo que traiga el JSON
    if (!doc["morse"].isNull()) {
        // {"morse":"SOS","color":"roja"} -> emitir texto en morse
        preset = "morse";
        prepararMorse(doc["morse"]);
    } else if (!doc["preset"].isNull()) {
        // {"preset":"semaforo"} o "ola" -> secuencia automatica
        preset = (const char*)doc["preset"];
    } else {
        // {"verde":"on","roja":"off","azul":"dim"} -> control por LED
        preset = "ninguno";
        estadoVerde = parseEstado(doc["verde"] | "off");
        estadoRojo  = parseEstado(doc["roja"]  | "off");
        estadoAzul  = parseEstado(doc["azul"]  | "off");
    }

    aplicarLeds();
    oledEstado();

    // ACK de vuelta: publico un JSON en iabd2425/esp32/ack para que
    // la app sepa que el ESP32 llego a procesar el comando
    client.publish(ackTopic, "{\\"ok\\":true}");
}`),
  spacer(),

  bodyText("Cada LED tiene 7 estados posibles, guardados en un enum. As\u00ed me ahorro magic numbers y el c\u00f3digo se lee mejor."),

  dataTable(
    ["Valor JSON", "Enum interno", "Acci\u00f3n en el LED"],
    [
      ["\"off\"",   "OFF",   "Apagado (PWM = 0)"],
      ["\"on\"",    "ON",    "Brillo m\u00e1ximo (PWM = 255)"],
      ["\"dim\"",   "DIM",   "Brillo tenue (PWM = 20, casi vela)"],
      ["\"blink\"", "BLINK", "Parpadea a 400 ms entre encendido y apagado"],
      ["\"fast\"",  "FAST",  "Parpadea r\u00e1pido, a 150 ms"],
      ["\"slow\"",  "SLOW",  "Parpadea lento, a 1 segundo"],
      ["\"fade\"",  "FADE",  "Sube y baja suave tipo respiraci\u00f3n (PWM sinusoide)"],
    ],
    [1800, 1800, 5360],
  ),
  spacer(),

  heading2("8.6 PWM, parpadeo sin delay, preset sem\u00e1foro y OLED"),
  bodyText("Los estados \"on\", \"off\" y los de parpadeo podr\u00edan hacerse con digitalWrite, pero \"dim\" y \"fade\" necesitan brillo intermedio. Para eso uso el m\u00f3dulo LEDC del ESP32 (PWM por hardware), configurado a 5 kHz y 8 bits de resoluci\u00f3n. PWM significa Pulse Width Modulation: la placa enciende y apaga el LED muy r\u00e1pido, y cambiando el porcentaje de tiempo encendido (el \"ancho de pulso\") se percibe como m\u00e1s o menos brillo. A 5 kHz el parpadeo es invisible para el ojo. Ref: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html"),

  bodyText("Configuro un canal PWM por LED:"),
  codeBlock(`ledcSetup(CANAL_ROJO,  5000, 8);     // 5 kHz, 0..255
ledcSetup(CANAL_VERDE, 5000, 8);
ledcSetup(CANAL_AZUL,  5000, 8);
ledcAttachPin(LED_ROJO,  CANAL_ROJO);
ledcAttachPin(LED_VERDE, CANAL_VERDE);
ledcAttachPin(LED_AZUL,  CANAL_AZUL);`),
  spacer(),

  bodyText("El parpadeo (blink/fast/slow) lo hago con millis() en el loop(), sin delay(). Cada LED tiene su propio timer, as\u00ed pueden ir a ritmos distintos (uno r\u00e1pido, otro lento, otro fijo). La t\u00e9cnica \"blink without delay\" est\u00e1 explicada en los ejemplos oficiales de Arduino (https://docs.arduino.cc/built-in-examples/digital/BlinkWithoutDelay/)."),

  bodyText("Para el modo fade cálculo una curva suave tipo respiraci\u00f3n con una funci\u00f3n seno, que va de 0 a 255 y vuelve con periodo de 2 segundos:"),
  codeBlock(`float fase = 2 * PI * (millis() % 2000) / 2000.0;
int fadeLvl = (int)((sin(fase) * 0.5 + 0.5) * 255);
ledcWrite(CANAL_VERDE, fadeLvl);  // brillo continuo cambiando`),
  spacer(),

  bodyText("El preset \"semaforo\" es una secuencia que se autogestiona en el loop: verde 3 segundos, \u00e1mbar (verde+rojo a la vez) 1 segundo, rojo 3 segundos, y vuelta a empezar. Se activa desde la \u00fanica herramienta poniendo modo_especial=semaforo, y se desactiva poniendo modo_especial=ninguno. Cualquier comando normal de LEDs tambi\u00e9n lo interrumpe autom\u00e1ticamente."),

  bodyText("El preset \"ola\" es parecido pero m\u00e1s simple: enciende los 3 LEDs por turnos (verde -> roja -> azul -> verde...) cada 500 ms, como cuando la grada de un estadio hace la ola. El usuario s\u00f3lo tiene que decir \"haz la ola\" y el modelo rellena modo_especial=ola."),

  bodyText("Modo \"morse\": emite un texto en c\u00f3digo morse internacional por el LED que diga el usuario. El usuario dice por ejemplo \"emite SOS en morse por la roja\" y el modelo rellena modo_especial=morse, texto_morse=SOS, color_morse=roja. El ESP32 tiene una tabla con los s\u00edmbolos morse de cada letra A-Z y d\u00edgitos 0-9, y los va emitiendo respetando los tiempos est\u00e1ndar: un punto dura 350 ms y la raya el triple, 1050 ms, para que en el LED se note claramente la diferencia (https://es.wikipedia.org/wiki/C%C3%B3digo_morse). Entre los s\u00edmbolos de una misma letra meto un gap de 1 unidad OFF (si no, las tres puntos de la S se ver\u00edan como un solo parpadeo continuo). Entre letras uso 3 unidades OFF y entre palabras 7. Cuando la cadena termina, el firmware la vuelve a emitir desde el principio en bucle, as\u00ed el morse se queda sonando hasta que el usuario mande apagar. Mientras emite, la OLED muestra en letras grandes los puntos y rayas que est\u00e1n saliendo (la implementaci\u00f3n interna usa un car\u00e1cter 'g' para marcar los gaps de una misma letra, pero la OLED los filtra para que solo se vean puntos, rayas y espacios)."),

  bodyText("La OLED est\u00e1 redise\u00f1ada para leerse de un vistazo. En la franja amarilla (filas superiores de la SSD1306 dual-color) va la cabecera, y en la franja azul van los 3 LEDs con su estado en castellano: \"VERDE encendida\", \"ROJA parpadea\", \"AZUL tenue\". Un c\u00edrculo s\u00f3lido indica que el LED est\u00e1 activo en cualquier modo; vac\u00edo que est\u00e1 apagado. Al recibir cada comando se muestra un pantallazo breve \"OK - Comando recibido\" como feedback visual."),

  bodyText("ACK de vuelta a la app (acuse de recibo): adem\u00e1s de aplicar el comando, el ESP32 publica en el topic iabd2425/esp32/ack un JSON con los estados aplicados. As\u00ed cualquier cliente puede verificar que la placa lleg\u00f3 a procesar el mensaje. Ejemplo de payload ACK:"),
  codeBlock(`{"ok":true,"verde":2,"roja":3,"azul":0,"preset":"ninguno"}`),
  spacer(),

  bodyText("Para MQTT uso PubSubClient (https://pubsubclient.knolleary.net/api). Hay otra librer\u00eda AsyncMqttClient que no bloquea el loop, pero para comandos espor\u00e1dicos como los de la demo PubSubClient va de sobra."),
];

/* ── SECTION 6: MCP ──────────────────────────────────────────────── */

const secMCP = [
  heading1("9. Servidor MCP"),
  bodyText("Adem\u00e1s de la app MAUI he montado un servidor MCP en un proyecto aparte (LucesIoT.MCP). La idea es que cualquier cliente que hable Model Context Protocol, como Claude Desktop, pueda usar la misma herramienta controlar_luces sin tener que abrir la aplicaci\u00f3n de escritorio. El servidor reusa la misma l\u00f3gica de Node-RED mediante HTTP, as\u00ed que todo el flujo hacia el ESP32 no cambia."),
  bodyText("MCP es un est\u00e1ndar abierto de Anthropic (https://modelcontextprotocol.io/). La idea es que cualquier cliente que hable MCP pueda usar el mismo servidor, sin acoplarse a una app concreta. Est\u00e1 bastante de moda ahora mismo."),
  bodyText("El servidor va en un proyecto .NET aparte (LucesIoT.MCP) con el paquete ModelContextProtocol de NuGet y transporte STDIO (entrada/salida est\u00e1ndar por consola), que es el m\u00e1s simple para un servidor local."),

  dataTable(
    ["Herramienta MCP", "Par\u00e1metros", "Descripci\u00f3n"],
    [
      ["ControlarLuces", "verde, roja, azul + modo_especial, texto_morse, color_morse", "Todo en una: control de los 3 LEDs con 7 estados, o activa sem\u00e1foro/ola/morse seg\u00fan modo_especial"],
      ["EstadoSistema",  "ninguno",  "Devuelve info del estado actual, topic MQTT y modos disponibles"],
    ],
    [2500, 3500, 3360],
  ),
  spacer(),

  codeBlock(`[McpServerTool, Description(
    "Controla las 3 luces. Estados por luz: off, on, dim, blink, fast, slow, fade. " +
    "Si modo_especial no es 'ninguno' se ignoran verde/roja/azul y se activa el modo.")]
public async Task<string> ControlarLuces(
    [Description("Estado de la luz verde")] string verde = "off",
    [Description("Estado de la luz roja")]  string roja  = "off",
    [Description("Estado de la luz azul")]  string azul  = "off",
    [Description("Modo: ninguno, semaforo, ola, morse")] string modo_especial = "ninguno",
    [Description("Texto a emitir si modo=morse")]        string texto_morse   = "",
    [Description("LED del morse: verde, roja, azul")]    string color_morse   = "verde")
{
    // segun el modo elegido llama a una u otra ruta del servicio interno
    if (modo_especial == "semaforo" || modo_especial == "ola")
        return await _nodeRedService.SendPresetAsync(modo_especial) ? ... : "error";
    if (modo_especial == "morse" && !string.IsNullOrWhiteSpace(texto_morse))
        return await _nodeRedService.SendMorseAsync(texto_morse, color_morse) ? ... : "error";
    return await _nodeRedService.SendLedStatesAsync(verde, roja, azul) ? ... : "error";
}`),
  spacer(),

  bodyText("Por dentro hace lo mismo que la app MAUI: decide si es modo normal, preset o morse, y manda el POST JSON correspondiente a Node-RED. La \u00fanica diferencia es de d\u00f3nde viene la orden: del chat de la app o de un cliente MCP como Claude Desktop. He mantenido la misma herramienta \u00fanica con los mismos par\u00e1metros para que sea consistente entre los dos sitios."),
];

/* ── SECTION 7: Instalación ──────────────────────────────────────── */

const secInstall = [
  heading1("10. Instalaci\u00f3n y puesta en marcha"),
  bodyText("Son varias piezas que tienen que arrancar en el orden correcto: LM Studio, Node-RED, la ESP32 y la app. Si saltas un paso o los enciendes desordenados te puedes volver loco buscando por qu\u00e9 no responde. Lo explico en orden para que sea f\u00e1cil de seguir."),
  bodyText("Para ahorrarme los pasos cada vez he incluido en la ra\u00edz del proyecto un script ARRANCAR_TODO.bat que levanta el servidor de LM Studio con el modelo cargado, arranca Node-RED y lanza la app MAUI en cadena. S\u00f3lo hay que darle doble clic. El script detecta si tengo instalado el CLI de LM Studio (lms) y lo usa; si no, avisa para abrir LM Studio a mano. Igual con Node-RED: si no lo encuentra, lo intenta con npx. As\u00ed la demo arranca sin tener que abrir tres programas por separado."),

  heading2("10.1 Requisitos previos"),
  bodyText("Software necesario:", { bold: true }),
  ...bulletList([
    "Windows 10/11 (tambi\u00e9n compila para Android/iOS pero yo lo he probado en Windows)",
    ".NET 9.0 SDK -- descarga: https://dotnet.microsoft.com/download",
    "Node.js y npm -- descarga: https://nodejs.org (la versi\u00f3n LTS)",
    "LM Studio -- descarga: https://lmstudio.ai",
    "Un IDE para la app MAUI: Visual Studio 2022 (17.8+) con carga de trabajo \".NET Multi-platform App UI development\", VS Code con C# Dev Kit, o terminal con dotnet CLI",
    "PlatformIO -- se instala como extensi\u00f3n de VS Code (buscar \"PlatformIO IDE\" en la tienda de extensiones)",
  ]),
  bodyText("Hardware para la parte IoT:", { bold: true }),
  ...bulletList([
    "ESP32 DevKit V1",
    "3 LEDs (rojo, verde, azul) con 3 resistencias de 220 ohmios",
    "Pantalla OLED SSD1306 0.96\" I2C (opcional)",
    "Cables dupont y protoboard",
    "Cable USB para la ESP32",
  ]),

  heading2("10.2 Instalar y arrancar LM Studio"),
  ...numberedList([
    "Descargar LM Studio desde https://lmstudio.ai e instalarlo.",
    "Abrir LM Studio. En la barra de b\u00fasqueda de modelos, buscar \"unsloth/qwen3.5\" y descargar Qwen3.5-0.8B-GGUF (el de unsloth, 1.21 GB). Si tu equipo tiene m\u00e1s RAM/GPU, puedes probar el 4B que es mejor.",
    "Ir a la pesta\u00f1a Developer > Local Server.",
    "Pulsar \"+ Load Model\" y seleccionar el Qwen3.5 0.8B que acabas de descargar.",
    "El servidor arranca autom\u00e1ticamente. Verificar que funciona abriendo en el navegador:",
  ]),
  codeBlock("http://127.0.0.1:1234/v1/models"),
  bodyText("Deber\u00eda devolver un JSON con el modelo. Si sale error, comprobar que no haya otro proceso en el puerto 1234."),

  heading2("10.3 Instalar y arrancar Node-RED"),
  bodyText("Node-RED necesita Node.js. Si no lo tienes, desc\u00e1rgalo de https://nodejs.org (LTS)."),
  bodyText("Instalar Node-RED de forma global:", { bold: true }),
  codeBlock("npm install -g node-red"),
  bodyText("Arrancarlo:", { bold: true }),
  codeBlock("node-red"),
  bodyText("Esto levanta Node-RED en http://localhost:1880. Abrirlo en el navegador."),
  bodyText("Importar el flujo del proyecto:", { bold: true }),
  ...numberedList([
    "En Node-RED, ir al men\u00fa (tres rayas arriba a la derecha) > Import",
    "Seleccionar el archivo NodeRED/flows.json de la carpeta del proyecto",
    "Pulsar Import",
    "Pulsar Deploy (desplegar, bot\u00f3n rojo arriba a la derecha)",
  ]),
  bodyText("Para comprobar que funciona, abrir una terminal y hacer:"),
  codeBlock(`curl -X POST http://localhost:1880/encender -H "Content-Type: application/json" -d "{\\"verde\\":\\"off\\",\\"roja\\":\\"on\\",\\"azul\\":\\"off\\"}"`),
  bodyText("O en PowerShell:"),
  codeBlock(`Invoke-RestMethod -Uri http://localhost:1880/encender -Method Post -ContentType "application/json" -Body '{"verde":"off","roja":"on","azul":"off"}'`),
  bodyText("Si en la pesta\u00f1a Debug (depuraci\u00f3n) de Node-RED aparece el JSON con los 3 estados y despu\u00e9s el LED rojo del ESP32 se enciende, est\u00e1 funcionando bien."),

  heading2("10.4 Cargar firmware en la ESP32"),
  ...numberedList([
    "Abrir VS Code e instalar la extensi\u00f3n PlatformIO IDE (si no la tienes, buscarla en la tienda de extensiones).",
    "Abrir la carpeta ESP32/ del proyecto: File > Open Folder > seleccionar la carpeta ESP32.",
    "Editar src/main.cpp y poner tu WiFi:",
  ]),
  codeBlock(`const char* ssid = "TU_WIFI";
const char* password = "TU_PASSWORD";`),
  ...numberedList([
    "Conectar la ESP32 por USB al ordenador.",
    "En la barra azul inferior de VS Code (la de PlatformIO), pulsar el icono de flecha para subir el firmware. La primera vez tarda m\u00e1s porque PlatformIO descarga las librer\u00edas (PubSubClient, Adafruit SSD1306, Adafruit GFX).",
    "Abrir el Serial Monitor (monitor serie, icono del enchufe en la barra de PlatformIO, velocidad 115200). Deber\u00eda mostrar:",
  ]),
  codeBlock(`Conectando a WiFi...
WiFi conectado! IP: 192.168.1.xxx
Conectando a MQTT...
Conectado a MQTT. Suscrito a: iabd2425/esp32/led`),
  bodyText("Si no conecta al WiFi, verificar SSID y contrase\u00f1a. Si no conecta a MQTT, puede ser que test.mosquitto.org est\u00e9 ca\u00eddo (pasa a veces) -- en ese caso cambiar al broker de respaldo broker.hivemq.com."),

  heading2("10.5 Compilar y ejecutar la app MAUI"),
  bodyText("Opci\u00f3n A -- Visual Studio 2022 (lo m\u00e1s sencillo):", { bold: true }),
  ...numberedList([
    "Abrir LucesIoT.slnx con Visual Studio 2022.",
    "En el desplegable de target, seleccionar \"Windows Machine\".",
    "Pulsar F5 o el bot\u00f3n de play verde.",
  ]),
  bodyText("Opci\u00f3n B -- Terminal con dotnet CLI (sin Visual Studio):", { bold: true }),
  codeBlock(`cd LucesIoT.MAUI
dotnet restore
dotnet build -f net9.0-windows10.0.19041.0
dotnet run -f net9.0-windows10.0.19041.0`),
  bodyText("Opci\u00f3n C -- VS Code:", { bold: true }),
  bodyText("Abrir la carpeta del proyecto, instalar la extensi\u00f3n C# Dev Kit, y usar Ctrl+F5."),
  bodyText("Paquetes NuGet que usa la app (se restauran autom\u00e1ticamente):", { bold: true }),
  ...bulletList([
    "CommunityToolkit.Mvvm 8.4.2 -- patr\u00f3n MVVM",
    "CommunityToolkit.Maui 11.2.0 -- reconocimiento de voz (SpeechToText)",
    "Microsoft.Maui.Controls -- el framework de MAUI (viene con el SDK)",
  ]),

  heading2("10.6 Orden de arranque"),
  bodyText("Para que todo funcione de extremo a extremo:"),
  ...numberedList([
    "LM Studio -- cargar el modelo y verificar que el servidor est\u00e1 en \"Running\"",
    "Node-RED -- arrancar y desplegar el flujo",
    "ESP32 -- conectar por USB y verificar en el monitor serie que conecta al WiFi y MQTT",
    "App MAUI -- ejecutar con F5 o dotnet run",
  ]),
  bodyText("Si todo est\u00e1 correcto, al escribir 'enciende la luz roja' en la app: el chat muestra el mensaje, el LED visual de la app se pone rojo, en Node-RED aparece el mensaje de depuraci\u00f3n, y en la ESP32 se enciende el LED f\u00edsico rojo."),
];

/* ── SECTION 11: Conclusiones ────────────────────────────────────── */

const secConclusiones = [
  heading1("11. Conclusiones"),
  bodyText("Mirando atr\u00e1s, lo importante me ha salido: que un modelo corriendo en mi propio PC entienda castellano normal (\u201cenciende la verde y pon la roja parpadeando r\u00e1pido\u201d) y acabe moviendo unos LEDs f\u00edsicos en la ESP32 al otro lado de la red. La primera vez que la placa respondi\u00f3 en dos segundos me re\u00ed solo. La cadena entera (app MAUI \u2192 LM Studio \u2192 Node-RED \u2192 MQTT \u2192 ESP32) va estable, y al montarla he entendido por fin c\u00f3mo encajan las piezas que antes ve\u00eda sueltas."),
  bodyText("No todo fue f\u00e1cil. Donde m\u00e1s me atasqu\u00e9 fue eligiendo modelo: prob\u00e9 tama\u00f1os y cuantizaciones a ciegas hasta dar con uno que me cupiera en la GPU y adem\u00e1s llamase a la tool de verdad. El system prompt tambi\u00e9n me hizo sudar, porque el modelo contestaba \u201cvale, ahora enciendo\u201d en vez de invocar la herramienta; no se quit\u00f3 hasta que met\u00ed la regla en may\u00fasculas y forc\u00e9 tool_choice=\u201crequired\u201d. Y en la ESP32 me comi\u00f3 un par de horas los delay() bloqueantes al meter varios parpadeos a la vez; lo reescrib\u00ed con millis() y cada LED con su propio ritmo."),
  bodyText("Me llevo varias cosas. La principal, que dise\u00f1ar bien la tool (par\u00e1metros, enum, descripci\u00f3n) importa casi m\u00e1s que elegir modelo: con una tool bien pensada hasta un modelo peque\u00f1o acierta. Tambi\u00e9n que partir el sistema en capas (MVVM en la app, Node-RED como pasarela, ESP32 solo ejecutando) te salva cuando algo peta, porque vas probando trozo a trozo. Y, ya al final, que MQTT para esto es un regalo: con cuatro l\u00edneas tienes comunicaci\u00f3n bidireccional y desacoplada."),
  bodyText("Cosas que dejo pendientes: meter TLS y autenticaci\u00f3n al broker MQTT (ahora mismo est\u00e1 todo abierto) y sacar SSID/password a un fichero de config en vez de tenerlos dentro del c\u00f3digo. Si lo retomara, a\u00f1adir\u00eda m\u00e1s dispositivos (otra ESP32, un sensor de temperatura, un rel\u00e9) y un inventario din\u00e1mico para que el LLM supiera qu\u00e9 hay conectado en cada momento. Si acabo cambiando de equipo probar\u00e9 con un modelo m\u00e1s grande para ver cu\u00e1nto mejora con frases ambiguas. Y ya puestos, estar\u00eda guapo guardar logs persistentes de lo que se va ejecutando para revisar despu\u00e9s qu\u00e9 hizo el sistema."),
];

/* ── SECTION 9: Bibliografia ────────────────────────────────────── */

const secBiblio = [
  heading1("12. Bibliograf\u00eda y referencias"),
  bodyText("Todas las fuentes consultadas durante el desarrollo de este proyecto, organizadas por tema:"),

  heading2("12.1 Modelo LLM y function calling"),
  ...bulletList([
    "LM Studio -- aplicaci\u00f3n para ejecutar LLMs en local: https://lmstudio.ai",
    "Qwen3.5 en LM Studio: https://lmstudio.ai/models/qwen3",
    "Unsloth Qwen3.5-0.8B-GGUF (modelo utilizado): https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF",
    "Comparativa de modelos locales en tool calling (jdhodges.com, 13 modelos, 40 tests): https://www.jdhodges.com/blog/local-llms-on-tool-calling-2026-pt1-local-lm/",
    "Mejores modelos para LM Studio (mayhemcode.com): https://www.mayhemcode.com/2026/03/best-models-for-lm-studio-llama-4-qwen3.html",
    "Documentaci\u00f3n de Qwen sobre function calling: https://qwen.readthedocs.io/en/latest/framework/function_call.html",
    "Gu\u00eda de function calling de OpenAI (API que LM Studio replica): https://platform.openai.com/docs/guides/function-calling",
  ]),

  heading2("12.2 .NET MAUI y MVVM"),
  ...bulletList([
    "CommunityToolkit.Mvvm (Microsoft): https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/",
    "CommunityToolkit.Maui (SpeechToText): https://learn.microsoft.com/en-us/dotnet/communitytoolkit/maui/",
    "Inyecci\u00f3n de dependencias en MAUI: https://learn.microsoft.com/en-us/dotnet/maui/fundamentals/dependency-injection",
    "Permisos en MAUI: https://learn.microsoft.com/en-us/dotnet/maui/platform-integration/appmodel/permissions",
    "System.Text.Json (Microsoft): https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/overview",
  ]),

  heading2("12.3 Node-RED y MQTT"),
  ...bulletList([
    "Node-RED (OpenJS Foundation): https://nodered.org/",
    "Broker p\u00fablico test.mosquitto.org: https://test.mosquitto.org/",
    "Broker alternativo HiveMQ: https://www.hivemq.com/mqtt/public-mqtt-broker/",
  ]),

  heading2("12.4 ESP32 y hardware"),
  ...bulletList([
    "PlatformIO para ESP32: https://docs.platformio.org/en/latest/boards/espressif32/esp32dev.html",
    "Pinout ESP32 DevKit V1 (Espressif): https://docs.espressif.com/projects/esp-idf/en/latest/esp32/hw-reference/esp32/get-started-devkitc.html",
    "Librer\u00eda PubSubClient (MQTT para Arduino): https://pubsubclient.knolleary.net/api",
    "Librer\u00eda Adafruit SSD1306 (pantalla OLED): https://github.com/adafruit/Adafruit_SSD1306",
    "ArduinoJson v7 (parseo de JSON en ESP32): https://arduinojson.org/v7/tutorial/deserialization/",
    "Blink Without Delay (patr\u00f3n millis() de Arduino): https://docs.arduino.cc/built-in-examples/digital/BlinkWithoutDelay/",
  ]),

  heading2("12.5 MCP (Model Context Protocol)"),
  ...bulletList([
    "Especificaci\u00f3n MCP (Anthropic): https://modelcontextprotocol.io/",
    "Paquete NuGet ModelContextProtocol: https://www.nuget.org/packages/ModelContextProtocol",
  ]),

  heading2("12.6 Accesibilidad y formato del documento"),
  ...bulletList([
    "British Dyslexia Association -- Gu\u00eda de estilo: https://www.bdadyslexia.org.uk/advice/employers/creating-a-dyslexia-friendly-workplace/dyslexia-friendly-style-guide",
    "WCAG 2.1 -- Pautas de accesibilidad web (W3C): https://www.w3.org/WAI/WCAG21/",
    "WCAG 2.1 SC 1.4.8 -- Presentaci\u00f3n visual: https://www.w3.org/WAI/WCAG21/Understanding/visual-presentation.html",
    "WCAG 2.1 SC 1.4.12 -- Espaciado de texto: https://www.w3.org/WAI/WCAG21/Understanding/text-spacing.html",
    "National Autistic Society -- Comunicaci\u00f3n: https://www.autism.org.uk/advice-and-guidance/topics/communication",
    "Atkinson Hyperlegible (Braille Institute): https://brailleinstitute.org/freefont",
    "Rello, L. y Baeza-Yates, R. (2013). Good Fonts for Dyslexia. Proceedings of ASSETS '13: https://dl.acm.org/doi/10.1145/2513383.2513447",
    "CAST -- Dise\u00f1o Universal para el Aprendizaje (UDL): https://udlguidelines.cast.org/",
  ]),
];

/* ── BUILD DOCUMENT ──────────────────────────────────────────────── */

const doc = new Document({
  // metadatos del documento (los que salen al darle a Archivo > Información)
  creator: "autor Mart\u00ednez",
  lastModifiedBy: "autor Mart\u00ednez",
  title: "Tarea 7",
  styles: {
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { bold: true, size: 56, color: BLUE1, font: FONT },
        paragraph: {
          spacing: { before: 360, after: 200 },
          outlineLevel: 0,
        },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { bold: true, size: 44, color: BLUE2, font: FONT },
        paragraph: {
          spacing: { before: 240, after: 160 },
          outlineLevel: 1,
        },
      },
    ],
    default: {
      document: {
        run: { font: FONT, size: BODY_SIZE, color: BLACK },
        paragraph: {
          spacing: { after: 140, line: 360, lineRule: "atLeast" },
          alignment: AlignmentType.LEFT,
        },
      },
    },
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "\u2022",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: "numbers",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      // referencias dinamicas generadas por cada numberedList() -- hacen que
      // cada lista empiece desde 1 en vez de continuar la anterior
      ...extraNumberingRefs,
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      children: [
        ...coverChildren,
        ...tocSection,
        ...secIntro,
        ...secObjetivos,
        ...secArquitectura,
        ...secModelLLM,
        ...secTool,
        ...secMAUI,
        ...secNodeRed,
        ...secESP32,
        ...secMCP,
        ...secInstall,
        ...secConclusiones,
        ...secBiblio,
      ],
    },
  ],
});

/* ── WRITE FILE ──────────────────────────────────────────────────── */

const outPath = "D:/2526-1BDAT-Programaci\u00f3n para IA/UNIDAD 8/Tarea7/DocumentoTecnico.docx";
const buffer = await Packer.toBuffer(doc);
fs.writeFileSync(outPath, buffer);
console.log(`DocumentoTecnico.docx written (${(buffer.length / 1024).toFixed(1)} KB)`);
