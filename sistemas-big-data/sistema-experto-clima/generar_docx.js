const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat,
        HeadingLevel, BorderStyle, WidthType, ShadingType,
        PageNumber, PageBreak, TabStopType, TabStopPosition } = require("docx");

const FONT = "Atkinson Hyperlegible Next";
const MONO = "Atkinson Hyperlegible Mono";
const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function p(text, opts = {}) {
  const runs = [];
  // Parse text for `code` backticks
  const parts = text.split(/(`[^`]+`)/);
  for (const part of parts) {
    if (part.startsWith("`") && part.endsWith("`")) {
      runs.push(new TextRun({ text: part.slice(1, -1), font: MONO, size: 20, bold: opts.bold }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 24, bold: opts.bold, italics: opts.italics }));
    }
  }
  return new Paragraph({
    spacing: { after: 200, line: 360 },
    ...opts.pOpts,
    children: runs
  });
}

function heading(text, level) {
  return new Paragraph({
    heading: level,
    keepNext: true, keepLines: true,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, font: FONT, bold: true,
      size: level === HeadingLevel.HEADING_1 ? 32 : level === HeadingLevel.HEADING_2 ? 28 : 24 })]
  });
}

function bullet(text) {
  const runs = [];
  const parts = text.split(/(`[^`]+`)/);
  for (const part of parts) {
    if (part.startsWith("`") && part.endsWith("`")) {
      runs.push(new TextRun({ text: part.slice(1, -1), font: MONO, size: 20 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 24 }));
    }
  }
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 80, line: 360 },
    children: runs
  });
}

function numbered(text, ref = "numbers") {
  const runs = [];
  const parts = text.split(/(`[^`]+`)/);
  for (const part of parts) {
    if (part.startsWith("`") && part.endsWith("`")) {
      runs.push(new TextRun({ text: part.slice(1, -1), font: MONO, size: 20 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 24 }));
    }
  }
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80, line: 360 },
    children: runs
  });
}

function codeBlock(lines) {
  return lines.map(line => new Paragraph({
    spacing: { after: 0, line: 240 },
    shading: { fill: "F0F0F0", type: ShadingType.CLEAR },
    indent: { left: 360 },
    children: [new TextRun({ text: line || " ", font: MONO, size: 18 })]
  }));
}

function tableRow(cells, isHeader = false) {
  return new TableRow({
    cantSplit: true,
    tableHeader: isHeader,
    children: cells.map((text, i) => new TableCell({
      borders,
      width: { size: Math.floor(9026 / cells.length), type: WidthType.DXA },
      shading: isHeader ? { fill: "E8E8E8", type: ShadingType.CLEAR } : undefined,
      margins: { top: 40, bottom: 40, left: 80, right: 80 },
      children: [new Paragraph({
        spacing: { after: 0 },
        children: [new TextRun({ text, font: FONT, size: 20, bold: isHeader })]
      })]
    }))
  });
}

function makeTable(headers, rows) {
  const colW = Math.floor(9026 / headers.length);
  return new Table({
    width: { size: 9026, type: WidthType.DXA },
    columnWidths: headers.map(() => colW),
    rows: [
      tableRow(headers, true),
      ...rows.map(r => tableRow(r))
    ]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT },
        paragraph: { spacing: { before: 360, after: 200, line: 360 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT },
        paragraph: { spacing: { before: 300, after: 160, line: 360 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONT },
        paragraph: { spacing: { before: 240, after: 120, line: 360 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers2",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers3",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [
    // PORTADA
    {
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1418, right: 1418, bottom: 1418, left: 1418 } }
      },
      children: [
        new Paragraph({ spacing: { before: 2400 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "CIFP Carlos III", font: FONT, size: 28 })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
          children: [new TextRun({ text: "Modelos Big Data", font: FONT, size: 24 })] }),
        new Paragraph({ alignment: AlignmentType.CENTER,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 1 } },
          children: [] }),
        new Paragraph({ spacing: { before: 600 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Sistema Experto de", font: FONT, size: 44, bold: true })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
          children: [new TextRun({ text: "Control Climático de Edificios", font: FONT, size: 44, bold: true })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
          children: [new TextRun({ text: "Documentación Técnica", font: FONT, size: 32 })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
          children: [new TextRun({ text: "UT3T1 - Diseño e implementación de un sistema experto con Experta", font: FONT, size: 24 })] }),
        new Paragraph({ alignment: AlignmentType.CENTER,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 1 } },
          children: [] }),
        new Paragraph({ spacing: { before: 800 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "autor", font: FONT, size: 28 })] }),
        new Paragraph({ spacing: { before: 1200 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Marzo 2026", font: FONT, size: 28 })] }),
      ]
    },
    // CONTENIDO
    {
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1418, right: 1418, bottom: 1418, left: 1418 } }
      },
      headers: {
        default: new Header({ children: [new Paragraph({
          children: [
            new TextRun({ text: "UT3T1 - Sistema Experto", font: FONT, size: 18, color: "666666" }),
            new TextRun({ text: "\tDocumentación Técnica", font: FONT, size: 18, color: "666666" }),
          ],
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
          border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC", space: 4 } }
        })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })]
        })] })
      },
      children: [
        // 1. DISEÑO DEL SISTEMA
        heading("1. Diseño del sistema", HeadingLevel.HEADING_1),
        heading("1.1 Dominio elegido", HeadingLevel.HEADING_2),
        p("Para este trabajo elegí hacer un sistema de control climático de un edificio. En la presentación de la UT3 (capítulo 4) se menciona el control industrial como una de las aplicaciones de los sistemas basados en reglas, y un sistema de climatización encaja bien con esa idea: hay datos de sensores, reglas claras de actuación y situaciones donde el orden de las decisiones importa."),
        p("El sistema recibe datos de sensores (temperatura, humedad, CO2, ocupación) y decide qué hacer: poner calefacción, refrigeración, ventilación, etc. También tiene una parte de predicción con series temporales para anticiparse a cambios de temperatura."),
        p("Encaja bien con Experta porque:"),
        bullet("Los sensores se representan como hechos tipados con `Field`, igual que `Persona` y `Pago` en la sesión 1bis."),
        bullet("Se puede separar el conocimiento (reglas) de los datos (hechos), que es la base de un sistema experto según la guía técnica (cap. 1)."),
        bullet("El `salience` permite dar prioridad a las emergencias sobre el resto de reglas."),

        heading("1.2 Cómo funciona", HeadingLevel.HEADING_2),
        p("El sistema sigue el ciclo de ejecución que describe la guía técnica en el capítulo 6 (encadenamiento hacia adelante):"),
        numbered("`reset()` inicializa la memoria de trabajo y ejecuta los `@DefFacts`, que en mi caso declaran `EstadoSistema(modo=\"normal\")`.", "numbers"),
        numbered("Con `declare()` se añaden los hechos de los sensores a la memoria de trabajo.", "numbers"),
        numbered("`run()` arranca el ciclo de inferencia: el motor busca qué reglas tienen su LHS (antecedente) satisfecho por los hechos actuales, elige la de mayor `salience`, ejecuta su RHS (consecuente), y repite. Los hechos nuevos que declare el RHS pueden activar más reglas.", "numbers"),

        heading("1.3 Hechos del sistema", HeadingLevel.HEADING_2),
        p("Tengo 11 tipos de hechos. Según la guía técnica (cap. 3), cada `Fact` es una subclase de `dict` que almacena datos etiquetados. Los divido en tres grupos:"),
        p("Sensores (entrada):", { bold: true }),
        bullet("`SensorTemperatura`: zona, valor, timestamp"),
        bullet("`SensorHumedad`: zona, valor"),
        bullet("`SensorOcupacion`: zona, personas"),
        bullet("`SensorCO2`: zona, ppm"),
        bullet("`PrediccionTemperatura`: zona, valor_futuro, horizonte_min (viene del modelo predictivo)"),
        p("Hechos derivados (los generan las reglas):", { bold: true }),
        bullet("`NivelConfort`: zona, nivel (frío/óptimo/caluroso)"),
        bullet("`NivelCalidadAire`: zona, nivel (bueno/regular/malo)"),
        bullet("`RiesgoEnergetico`: zona, nivel"),
        p("Salidas:", { bold: true }),
        bullet("`AccionControl`: zona, sistema, acción, intensidad"),
        bullet("`Alerta`: zona, tipo, mensaje, prioridad"),
        bullet("`EstadoSistema`: modo (normal/ahorro/emergencia)"),

        heading("1.4 Cadena de inferencia multinivel", HeadingLevel.HEADING_2),
        p("Las reglas van por niveles, cada nivel usa lo que ha generado el anterior:"),
        ...codeBlock([
          "Nivel 0: Datos de sensores + PrediccionTemperatura",
          "    |",
          "    | [salience=100] Emergencias",
          "    | temp >45 o <0, CO2 >5000 -> Alerta",
          "    v",
          "Nivel 1: NivelConfort, NivelCalidadAire",
          "    |",
          "    | [salience=50] Clasificación",
          "    | temp -> frío/óptimo/caluroso",
          "    | CO2 -> bueno/regular/malo",
          "    v",
          "Nivel 2: RiesgoEnergético",
          "    |",
          "    | [salience=50] Ocupación alta + temp mala -> riesgo",
          "    v",
          "Nivel 3: AccionControl, Alerta",
          "    |",
          "    | [salience=20] Control",
          "    | confort + ocupación -> calef/refrig/ventil",
          "    v",
          "Nivel 4: Ajustes",
          "    |",
          "    | [salience=10] Optimización",
          "    | conflicto energía -> bajar intensidad",
        ]),
        p("Cuando empecé a hacer las reglas no usaba salience y no me funcionaba porque las reglas de control se ejecutaban antes de que existieran los hechos de clasificación. Separarlo en niveles solucionó el problema."),

        // 2. REGLAS
        heading("2. Reglas y comportamiento", HeadingLevel.HEADING_1),
        heading("2.1 Reglas implementadas", HeadingLevel.HEADING_2),
        p("El sistema tiene 17 reglas repartidas en 4 niveles de prioridad."),
        p("Emergencias (salience=100) - 2 reglas:", { bold: true }),
        bullet("`emergencia_temp`: salta si la temperatura pasa de 45 o baja de 0. Usa `P(lambda t: t > 45 or t < 0)`."),
        bullet("`emergencia_co2`: salta si el CO2 pasa de 5000 ppm."),
        p("Clasificación (salience=50) - 7 reglas:", { bold: true }),
        bullet("3 para temperatura: frío (<19), óptimo (19-26), caluroso (>26). Llevan `NOT(Alerta(...))` para no clasificar si hay emergencia."),
        bullet("3 para calidad del aire: bueno (<=400), regular (401-1000), malo (1001-5000)."),
        bullet("1 de riesgo energético: más de 30 personas y confort no óptimo. Usa `OR()` para pillar frío o caluroso."),
        p("Control (salience=20) - 5 reglas:", { bold: true }),
        bullet("Calefacción si frío + hay gente."),
        bullet("Refrigeración si caluroso + hay gente."),
        bullet("Ventilación forzada si aire malo."),
        bullet("Modo ahorro si no hay nadie y temp óptima."),
        bullet("Pre-enfriamiento si la predicción dice que va a subir de 28°C (usa series temporales)."),
        p("Todas llevan `NOT()` para no duplicar acciones. Al principio no lo ponía y me generaba la misma acción varias veces."),
        p("Optimización (salience=10) - 3 reglas:", { bold: true }),
        bullet("Si hay refrigeración alta + riesgo energético, baja a moderada con `modify()`."),
        bullet("Si caluroso + humedad >70%, activa deshumidificador."),
        bullet("Ventilación preventiva si hay bastante gente y aire regular."),

        heading("2.2 Operadores que he usado", HeadingLevel.HEADING_2),
        bullet("`P(lambda)`: para condiciones numéricas, como `P(lambda t: t > 45 or t < 0)`."),
        bullet("`L(\"valor\")`: para comparar con un valor exacto."),
        bullet("`NOT()`: para comprobar que un hecho no existe. Lo uso bastante para evitar duplicados."),
        bullet("`OR()`: para agrupar condiciones. La uso en la regla de riesgo energético."),
        bullet("`AS.accion << AccionControl(...)`: captura el hecho para poder modificarlo después con `modify()`."),
        bullet("`MATCH.zona`: enlaza el campo zona a una variable para usarla luego."),

        // 3. ANÁLISIS
        heading("3. Análisis de variación", HeadingLevel.HEADING_1),
        heading("3.1 Variación de temperatura", HeadingLevel.HEADING_2),
        p("Hice un barrido de -5°C a 54°C con CO2 fijo a 500 y 10 personas para ver cómo reacciona el sistema:"),
        makeTable(
          ["Rango", "Confort", "Acción", "Emergencia"],
          [
            ["T < 0°C", "no clasifica", "parada", "SÍ"],
            ["0-18°C", "frío", "calefacción", "NO"],
            ["19-26°C", "óptimo", "ninguna", "NO"],
            ["27-44°C", "caluroso", "refrigeración", "NO"],
            ["T > 45°C", "no clasifica", "parada", "SÍ"],
          ]
        ),
        p("Las transiciones salen limpias, no se solapan los rangos. En emergencias no se clasifican porque las reglas de clasificación llevan `NOT(Alerta(...))`."),

        heading("3.2 Variación del CO2", HeadingLevel.HEADING_2),
        makeTable(
          ["Rango", "Calidad", "Ventilación", "Emergencia"],
          [
            ["<= 400 ppm", "bueno", "NO", "NO"],
            ["401-1000 ppm", "regular", "sí >15 personas", "NO"],
            ["1001-5000 ppm", "malo", "SÍ (forzada)", "NO"],
            ["> 5000 ppm", "N/A", "SÍ (emergencia)", "SÍ"],
          ]
        ),
        p("La ventilación preventiva con aire regular es un caso donde se combinan datos de CO2 y de ocupación para decidir."),

        heading("3.3 Efecto de la ocupación", HeadingLevel.HEADING_2),
        bullet("0 personas: modo ahorro (si temp óptima)"),
        bullet("> 0 personas: se activan calefacción/refrigeración"),
        bullet("> 15 personas: ventilación preventiva (con aire regular)"),
        bullet("> 30 personas: riesgo energético (si temp no óptima)"),

        heading("3.4 Efecto de la predicción", HeadingLevel.HEADING_2),
        makeTable(
          ["Predicción (30 min)", "Temp actual", "Acción"],
          [
            ["< 28°C", "óptima (22°C)", "ninguna"],
            [">= 28°C", "óptima (22°C)", "pre-enfriamiento"],
            [">= 28°C", "calurosa (30°C)", "refrigeración"],
          ]
        ),
        p("El pre-enfriamiento solo salta cuando ahora está bien pero se espera que suba. Si ya hace calor, la refrigeración normal tiene más prioridad."),

        // 4. ESTRATEGIAS
        heading("4. Estrategias de control", HeadingLevel.HEADING_1),
        heading("4.1 Niveles de prioridad", HeadingLevel.HEADING_2),
        p("Uso 4 valores de `salience`:"),
        p("salience=100 - Emergencias: Lo primero es la seguridad. Si la temperatura es peligrosa o el CO2 es tóxico, se genera una alerta y se bloquean las reglas de clasificación para que no intente climatizar una zona que habría que evacuar.", { bold: false }),
        p("salience=50 - Clasificación: Convierte los datos de sensores en categorías (frío, caluroso, aire malo...). Si esto no va antes que el control, las reglas de control no encuentran los hechos que necesitan y no hacen nada. Es lo que me pasaba al principio.", { bold: false }),
        p("salience=20 - Control: Genera acciones concretas a partir de las clasificaciones."),
        p("salience=10 - Optimización: Ajusta acciones cuando hay conflictos, por ejemplo bajar la intensidad si el gasto es alto."),

        heading("4.2 Conflicto confort vs energía", HeadingLevel.HEADING_2),
        p("Es el caso más interesante. Cuando hace calor y hay mucha gente pasan estas cosas en orden:"),
        numbered("Se clasifica como caluroso (salience=50)", "numbers2"),
        numbered("Se detecta riesgo energético porque hay >30 personas con temp no óptima (salience=50)", "numbers2"),
        numbered("Se activa refrigeración alta (salience=20)", "numbers2"),
        numbered("La regla de optimización ve que hay refrigeración alta + riesgo energético y baja la intensidad a moderada con `modify()` (salience=10)", "numbers2"),
        p("Para hacer el `modify()` uso `AS.accion << AccionControl(...)` para capturar el hecho y luego `self.modify(accion, intensidad=\"moderada\")`. Es parecido al ejemplo de préstamos de la sesión 1bis."),

        // 5. SERIES TEMPORALES
        heading("5. Series temporales", HeadingLevel.HEADING_1),
        heading("5.1 Datos y modelo", HeadingLevel.HEADING_2),
        p("Genero datos falsos de temperatura para 7 días (168 registros, uno por hora). Los datos simulan un ciclo día/noche, efecto fin de semana (2 grados menos), tendencia ascendente y ruido aleatorio."),
        p("El modelo es una regresión polinomial de grado 3 con scikit-learn. Como features uso:"),
        bullet("`hora_sin` y `hora_cos`: para codificar la hora de forma cíclica (que las 23h estén cerca de las 0h)."),
        bullet("`dia_semana`: número del día."),
        bullet("`es_finde`: 1 si es sábado o domingo."),

        heading("5.2 Cómo se integra con el experto", HeadingLevel.HEADING_2),
        p("La predicción se mete como un hecho más antes de ejecutar el motor:"),
        ...codeBlock([
          "temp_predicha = predecir_temp(modelo, hora + 0.5, dia)",
          "engine.declare(PrediccionTemperatura(",
          "    zona=\"oficina\",",
          "    valor_futuro=temp_predicha,",
          "    horizonte_min=30",
          "))",
        ]),
        p("La regla `control_predictivo` se activa si la predicción pasa de 28°C, la temperatura actual es óptima y hay gente en la zona. Así el sistema puede actuar 30 minutos antes de que suba la temperatura."),

        // 6. PLAN DE PRUEBAS
        heading("6. Plan de pruebas", HeadingLevel.HEADING_1),
        heading("6.1 Casos de prueba", HeadingLevel.HEADING_2),
        p("Hice 12 tests para cubrir distintas situaciones:"),
        makeTable(
          ["ID", "Tipo", "Prueba", "Entrada", "Esperado"],
          [
            ["T01", "Normal", "Calefacción", "Temp=15, Ocup=5", "calefacción"],
            ["T02", "Normal", "Refrigeración", "Temp=32, Ocup=3", "refrigeración"],
            ["T03", "Normal", "Ventilación", "CO2=1500", "ventilación"],
            ["T04", "Normal", "Sin acción", "T=22, CO2=400, Oc=5", "óptimo"],
            ["T05", "Multi", "Cadena", "Temp=15, Ocup=3", "frío+calef"],
            ["T06", "Multi", "Riesgo energ.", "T=30, Ocup=50", "refrig. mod."],
            ["T07", "Multi", "Predicción", "T=24, Pred=30", "pre-enfr."],
            ["T08", "Prior.", "Emergencia", "Temp=50", "alerta crít."],
            ["T09", "Prior.", "Ahorro", "Temp=22, Ocup=0", "modo ahorro"],
            ["T10", "Límite", "Umbral 19", "Temp=19.0", "óptimo"],
            ["T11", "Robust.", "Sin temp", "Solo Ocup=5", "sin acciones"],
            ["T12", "Robust.", "Dos zonas", "A:fría, B:caliente", "calef+refrig"],
          ]
        ),

        heading("6.2 Qué cubre cada grupo", HeadingLevel.HEADING_2),
        bullet("T01-T04: operación normal, que las reglas básicas funcionen."),
        bullet("T05-T07: inferencia multinivel. T05 comprueba la cadena sensor-confort-acción, T06 que el riesgo modifica la intensidad, T07 que la predicción activa el pre-enfriamiento."),
        bullet("T08-T09: que el salience funciona bien."),
        bullet("T10: caso límite, que 19.0 se clasifica como óptimo."),
        bullet("T11-T12: robustez. T11 que sin datos de temperatura no falla, T12 que dos zonas opuestas se manejan por separado."),
        p("Los 12 pasan correctamente."),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("D:\\UT3T1 - Dise\u00f1o e impl\\documentacion_tecnica.docx", buffer);
  console.log("OK - documentacion_tecnica.docx generado");
});
