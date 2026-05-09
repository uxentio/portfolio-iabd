const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun,
  AlignmentType, HeadingLevel, PageBreak,
  Header, Footer, PageNumber, BorderStyle,
  Table, TableRow, TableCell, WidthType, ShadingType,
  VerticalAlign, TabStopType, TabStopPosition, TableLayoutType
} = require("docx");

const img1 = fs.readFileSync("D:/Users/anton/Pictures/Screenshots/Captura de pantalla 2026-03-17 114038.png");
const img2 = fs.readFileSync("D:/Users/anton/Pictures/Screenshots/Captura de pantalla 2026-03-17 115321.png");
const img3 = fs.readFileSync("D:/Users/anton/Pictures/Screenshots/Captura de pantalla 2026-03-17 115516.png");

const FONT = "Atkinson Hyperlegible";
const ACCENT = "2563EB";    // azul intenso
const DARK = "1E293B";      // gris oscuro
const SUBTLE = "64748B";    // gris medio
const LIGHT_BG = "EFF6FF";  // azul muy claro fondo

const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: FONT, size: 22 } }
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT, color: DARK },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 8 } }
        }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT, color: ACCENT },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
      },
    ]
  },
  sections: [
    // ==================== PORTADA ====================
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 0, right: 0, bottom: 0, left: 0 }
        }
      },
      children: [
        // Barra superior azul
        new Table({
          width: { size: 11906, type: WidthType.DXA },
          columnWidths: [11906],
          rows: [new TableRow({
            height: { value: 2800, rule: "exact" },
            children: [new TableCell({
              borders: noBorders,
              width: { size: 11906, type: WidthType.DXA },
              shading: { fill: ACCENT, type: ShadingType.CLEAR },
              verticalAlign: VerticalAlign.CENTER,
              children: [
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "BIG DATA APLICADO", font: FONT, size: 28, bold: true, color: "FFFFFF" })]
                }),
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Curso 2025 / 2026", font: FONT, size: 20, color: "BFDBFE" })]
                }),
              ]
            })]
          })]
        }),

        // Espacio
        new Paragraph({ spacing: { before: 3000 }, children: [] }),

        // Titulo del reto
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          indent: { left: 1440, right: 1440 },
          children: [new TextRun({ text: "RETO 02", font: FONT, size: 72, bold: true, color: DARK })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 120 },
          indent: { left: 1440, right: 1440 },
          children: [new TextRun({ text: "Un Regalo", font: FONT, size: 44, color: ACCENT })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          indent: { left: 1440, right: 1440 },
          children: [new TextRun({ text: "Grafana - RA4", font: FONT, size: 28, color: SUBTLE })]
        }),

        // Linea decorativa
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 400, after: 400 },
          indent: { left: 3600, right: 3600 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 1 } },
          children: []
        }),

        // Info
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          indent: { left: 1440, right: 1440 },
          children: [new TextRun({ text: "Asignatura: Big Data Aplicado", font: FONT, size: 22, color: SUBTLE })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          indent: { left: 1440, right: 1440 },
          children: [new TextRun({ text: "Unidad: UT4 - Monitorizaci\u00f3n y Observabilidad", font: FONT, size: 22, color: SUBTLE })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          indent: { left: 1440, right: 1440 },
          children: [new TextRun({ text: "Fecha: 17 de marzo de 2026", font: FONT, size: 22, color: SUBTLE })]
        }),

        // Barra inferior
        new Paragraph({ spacing: { before: 3200 }, children: [] }),
        new Table({
          width: { size: 11906, type: WidthType.DXA },
          columnWidths: [11906],
          rows: [new TableRow({
            height: { value: 800, rule: "exact" },
            children: [new TableCell({
              borders: noBorders,
              width: { size: 11906, type: WidthType.DXA },
              shading: { fill: DARK, type: ShadingType.CLEAR },
              verticalAlign: VerticalAlign.CENTER,
              children: [
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Herramientas: Docker \u00B7 Prometheus \u00B7 Grafana \u00B7 Hadoop", font: FONT, size: 18, color: "94A3B8" })]
                })
              ]
            })]
          })]
        }),
      ]
    },

    // ==================== CONTENIDO ====================
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: ACCENT, space: 6 } },
              spacing: { after: 120 },
              children: [
                new TextRun({ text: "RETO 02 - Un Regalo - Grafana - RA4", font: FONT, size: 16, color: SUBTLE }),
              ],
              tabStops: [{ type: TabStopType.RIGHT, position: 9026 }]
            })
          ]
        })
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              border: { top: { style: BorderStyle.SINGLE, size: 2, color: "E2E8F0", space: 6 } },
              children: [
                new TextRun({ text: "Big Data Aplicado 25-26", font: FONT, size: 16, color: SUBTLE }),
                new TextRun({ text: "\t" }),
                new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: SUBTLE })
              ],
              tabStops: [{ type: TabStopType.RIGHT, position: 9026 }]
            })
          ]
        })
      },
      children: [
        // Ejercicio 1
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Ejercicio 1")] }),
        new Paragraph({
          spacing: { after: 200 },
          children: [new TextRun({ text: "Lo primero que he hecho ha sido levantar el entorno v6 con ", font: FONT }),
            new TextRun({ text: "docker compose up -d", font: FONT, bold: true, color: ACCENT }),
            new TextRun({ text: " y esperar a que arrancaran todos los contenedores. En la siguiente captura se ve que est\u00e1n todos en verde:", font: FONT })]
        }),

        // Captura 1
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Contenedores levantados")] }),
        new Paragraph({
          spacing: { after: 200 },
          children: [new TextRun({ text: "Aqu\u00ed se ven todos los contenedores del entorno funcionando en Docker Desktop:", font: FONT, color: SUBTLE, italics: true })]
        }),
        // Caja con fondo para la imagen
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [9026],
          rows: [new TableRow({
            children: [new TableCell({
              borders: {
                top: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                bottom: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                left: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                right: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" }
              },
              width: { size: 9026, type: WidthType.DXA },
              shading: { fill: "F8FAFC", type: ShadingType.CLEAR },
              margins: { top: 120, bottom: 120, left: 120, right: 120 },
              children: [new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new ImageRun({
                  type: "png", data: img1,
                  transformation: { width: 620, height: 349 },
                  altText: { title: "Contenedores", description: "Docker Desktop con contenedores levantados", name: "docker" }
                })]
              })]
            })]
          })]
        }),
        new Paragraph({
          spacing: { before: 80, after: 200 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Figura 1: Vista de Docker Desktop con todos los servicios activos", font: FONT, size: 18, italics: true, color: SUBTLE })]
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Captura 2: Caida
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Desactivaci\u00f3n del datanode2")] }),
        new Paragraph({
          spacing: { after: 120 },
          children: [new TextRun({ text: "Despu\u00e9s he abierto Grafana y lo he dejado unos minutos para que se vieran bien las gr\u00e1ficas. Luego he apagado el datanode2 con:", font: FONT })]
        }),
        // Comando en caja
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [9026],
          rows: [new TableRow({
            children: [new TableCell({
              borders: {
                top: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                bottom: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                left: { style: BorderStyle.SINGLE, size: 6, color: ACCENT },
                right: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" }
              },
              width: { size: 9026, type: WidthType.DXA },
              shading: { fill: LIGHT_BG, type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 200, right: 120 },
              children: [new Paragraph({
                children: [new TextRun({ text: "$ docker stop datanode2", font: "Atkinson Hyperlegible Mono", size: 20, color: DARK })]
              })]
            })]
          })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Al cabo de un minuto m\u00e1s o menos, en Grafana se ve c\u00f3mo la l\u00ednea del datanode2 deja de aparecer, porque ya no env\u00eda datos:", font: FONT })]
        }),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [9026],
          rows: [new TableRow({
            children: [new TableCell({
              borders: {
                top: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                bottom: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                left: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                right: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" }
              },
              width: { size: 9026, type: WidthType.DXA },
              shading: { fill: "F8FAFC", type: ShadingType.CLEAR },
              margins: { top: 120, bottom: 120, left: 120, right: 120 },
              children: [new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new ImageRun({
                  type: "png", data: img2,
                  transformation: { width: 620, height: 337 },
                  altText: { title: "Caida", description: "Grafana mostrando caida del datanode2", name: "caida" }
                })]
              })]
            })]
          })]
        }),
        new Paragraph({
          spacing: { before: 80, after: 300 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Figura 2: Dashboard Grafana - ca\u00edda del datanode2 (l\u00ednea roja se interrumpe)", font: FONT, size: 18, italics: true, color: SUBTLE })]
        }),

        // Captura 3: Recuperacion
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Reactivaci\u00f3n del datanode2")] }),
        new Paragraph({
          spacing: { after: 120 },
          children: [new TextRun({ text: "Para volver a levantarlo he ejecutado:", font: FONT })]
        }),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [9026],
          rows: [new TableRow({
            children: [new TableCell({
              borders: {
                top: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                bottom: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                left: { style: BorderStyle.SINGLE, size: 6, color: "16A34A" },
                right: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" }
              },
              width: { size: 9026, type: WidthType.DXA },
              shading: { fill: "F0FDF4", type: ShadingType.CLEAR },
              margins: { top: 80, bottom: 80, left: 200, right: 120 },
              children: [new Paragraph({
                children: [new TextRun({ text: "$ docker start datanode2", font: "Atkinson Hyperlegible Mono", size: 20, color: DARK })]
              })]
            })]
          })]
        }),
        new Paragraph({
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "He esperado otro minuto y en Grafana se ve c\u00f3mo vuelve a aparecer la l\u00ednea del datanode2, con un pico de CPU del arranque:", font: FONT })]
        }),
        new Table({
          width: { size: 9026, type: WidthType.DXA },
          columnWidths: [9026],
          rows: [new TableRow({
            children: [new TableCell({
              borders: {
                top: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                bottom: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                left: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" },
                right: { style: BorderStyle.SINGLE, size: 2, color: "CBD5E1" }
              },
              width: { size: 9026, type: WidthType.DXA },
              shading: { fill: "F8FAFC", type: ShadingType.CLEAR },
              margins: { top: 120, bottom: 120, left: 120, right: 120 },
              children: [new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new ImageRun({
                  type: "png", data: img3,
                  transformation: { width: 620, height: 337 },
                  altText: { title: "Recuperacion", description: "Grafana mostrando recuperacion del datanode2", name: "recuperacion" }
                })]
              })]
            })]
          })]
        }),
        new Paragraph({
          spacing: { before: 80, after: 200 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Figura 3: Dashboard Grafana - recuperaci\u00f3n del datanode2 (pico de CPU al arrancar)", font: FONT, size: 18, italics: true, color: SUBTLE })]
        }),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("D:/IA_y_BD - BIG DATA APLICADO - 25-26/RETO 02 - Un Regalo - Grafana - RA4/RETO02_Un_Regalo_Grafana_RA4.docx", buffer);
  console.log("Documento creado correctamente.");
});
