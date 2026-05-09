"""
Script para preparar los documentos de los casos de uso reales:
- CASO 4: Transcripcion de video de YouTube con marcas de tiempo
- CASO 5: Apuntes de Java (PDF de TECNUN) segmentados por pagina
"""

from youtube_transcript_api import YouTubeTranscriptApi
from PyPDF2 import PdfReader
import os
import re

BASE = r"D:\Tarea 5 RAG"


def preparar_transcripcion_video():
    """Descarga la transcripcion del video de Fazt sobre POO y la formatea
    con marcas de tiempo agrupadas por bloques de 30 segundos."""

    VIDEO_ID = "SI7O81GMG2A"
    TITULO_VIDEO = "Programacion Orientada a Objetos (POO) Explicada - Fazt"
    URL_VIDEO = f"https://www.youtube.com/watch?v={VIDEO_ID}"

    print(f"Descargando transcripcion de: {TITULO_VIDEO}")
    api = YouTubeTranscriptApi()
    transcript = api.fetch(VIDEO_ID, languages=['es'])
    snippets = list(transcript)

    # agrupar en bloques de ~30 segundos para que los chunks tengan contexto
    bloques = []
    bloque_actual = {"inicio": 0, "fin": 0, "texto": ""}
    DURACION_BLOQUE = 30  # segundos

    for s in snippets:
        if s.start - bloques[-1]["inicio"] > DURACION_BLOQUE if bloques else s.start > DURACION_BLOQUE:
            if bloque_actual["texto"].strip():
                bloques.append(bloque_actual)
            bloque_actual = {"inicio": s.start, "fin": s.start + s.duration, "texto": ""}

        # limpiar texto (quitar saltos de linea internos del subtitulo)
        texto_limpio = s.text.replace('\n', ' ').replace('\u200b', '').strip()
        bloque_actual["texto"] += " " + texto_limpio
        bloque_actual["fin"] = s.start + s.duration

    # ultimo bloque
    if bloque_actual["texto"].strip():
        bloques.append(bloque_actual)

    # generar el documento
    lineas = []
    lineas.append("=" * 60)
    lineas.append(f"TRANSCRIPCION DE VIDEO: {TITULO_VIDEO}")
    lineas.append(f"URL: {URL_VIDEO}")
    lineas.append(f"Duracion: {int(snippets[-1].start // 60)}:{int(snippets[-1].start % 60):02d}")
    lineas.append("=" * 60)
    lineas.append("")
    lineas.append("INDICE DE CONTENIDOS:")
    lineas.append("- Minuto 00:00 - Introduccion a la POO")
    lineas.append("- Minuto 01:00 - Clases, objetos e instancias")
    lineas.append("- Minuto 02:00 - Herencia")
    lineas.append("- Minuto 03:30 - Encapsulamiento")
    lineas.append("- Minuto 05:30 - Abstraccion")
    lineas.append("- Minuto 07:00 - Polimorfismo")
    lineas.append("- Minuto 08:30 - Resumen y cierre")
    lineas.append("")
    lineas.append("-" * 60)
    lineas.append("")

    for b in bloques:
        min_inicio = int(b["inicio"] // 60)
        sec_inicio = int(b["inicio"] % 60)
        min_fin = int(b["fin"] // 60)
        sec_fin = int(b["fin"] % 60)

        lineas.append(f"[Minuto {min_inicio:02d}:{sec_inicio:02d} - {min_fin:02d}:{sec_fin:02d}]")
        lineas.append(b["texto"].strip())
        lineas.append("")

    ruta = os.path.join(BASE, "transcripcion_poo_video.txt")
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas))

    print(f"  Generado: {ruta}")
    print(f"  Bloques: {len(bloques)}")
    return ruta


def preparar_apuntes_pdf():
    """Extrae el capitulo 3 (Clases en Java) del PDF de TECNUN y lo segmenta
    por pagina con marcas [Pagina X]."""

    pdf_path = os.path.join(BASE, "aprenda_java_primero.pdf")
    if not os.path.exists(pdf_path):
        print(f"ERROR: No se encuentra {pdf_path}")
        return None

    print(f"Procesando PDF: {pdf_path}")
    reader = PdfReader(pdf_path)

    # capitulo 3 "Clases en Java" va de PDF pag 45 a 72 (doc pag 37 a 64)
    # selecciono las mas relevantes para POO (no todas 28)
    paginas_relevantes = list(range(44, 72))  # PDF pages 45-72 (0-indexed: 44-71)

    lineas = []
    lineas.append("=" * 60)
    lineas.append("APUNTES DE JAVA: CLASES Y PROGRAMACION ORIENTADA A OBJETOS")
    lineas.append("Fuente: 'Aprenda Java como si estuviera en Primero'")
    lineas.append("Autores: J. Garcia de Jalon et al. - TECNUN, Universidad de Navarra")
    lineas.append("Capitulo 3: Clases en Java (paginas 37-64)")
    lineas.append("=" * 60)
    lineas.append("")
    lineas.append("INDICE DEL CAPITULO:")
    lineas.append("- Pagina 37: Generalidades sobre clases en Java")
    lineas.append("- Pagina 39: Variables miembro y metodos")
    lineas.append("- Pagina 41: Constructores y creacion de objetos")
    lineas.append("- Pagina 45: Herencia")
    lineas.append("- Pagina 49: Clases y metodos abstractos")
    lineas.append("- Pagina 51: Interfaces")
    lineas.append("- Pagina 55: Polimorfismo")
    lineas.append("- Pagina 57: Casting y conversiones de tipo")
    lineas.append("")
    lineas.append("-" * 60)
    lineas.append("")

    for pdf_page in paginas_relevantes:
        doc_page = pdf_page - 7  # offset entre numeracion PDF y documento
        text = reader.pages[pdf_page].extract_text()
        if not text or len(text.strip()) < 50:
            continue

        # limpiar el texto
        # quitar la cabecera repetida de copyright
        text = re.sub(r'Copyright.*?personales\.\s*', '', text, flags=re.DOTALL)
        # quitar cabecera de capitulo repetida
        text = re.sub(r'(ESIISS:.*?página \d+|Capítulo \d+:.*?página \d+)\s*', '', text)
        text = re.sub(r'(Cap.tulo \d+:.*?p.gina \d+)\s*', '', text)

        text = text.strip()
        if len(text) < 30:
            continue

        # pegar [Pagina XX] al inicio de cada parrafo para que cualquier
        # chunk que genere AnythingLLM siempre lleve la pagina
        parrafos = [p.strip() for p in text.split('\n') if p.strip()]
        for parrafo in parrafos:
            lineas.append(f"[Pagina {doc_page}] {parrafo}")
        lineas.append("")

    ruta = os.path.join(BASE, "apuntes_java_clases.txt")
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas))

    print(f"  Generado: {ruta}")
    print(f"  Paginas extraidas: {len([p for p in paginas_relevantes])}")
    return ruta


# === EJECUTAR ===
print("=== Preparando documentos para casos de uso reales ===\n")

print("--- CASO 4: Video de YouTube ---")
ruta_video = preparar_transcripcion_video()

print("\n--- CASO 5: Apuntes PDF ---")
ruta_pdf = preparar_apuntes_pdf()

print("\n=== Listo! ===")
print("Ahora sube estos dos archivos a AnythingLLM:")
print(f"  1. {ruta_video}")
print(f"  2. {ruta_pdf}")
print("Y prueba a hacer preguntas sobre POO para tomar las capturas.")
