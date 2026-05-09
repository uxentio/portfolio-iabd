"""
Script para descargar los subtitulos de un video de YouTube y generar
un archivo .txt con marcas de tiempo [Minuto XX:XX - YY:YY].

El texto se agrupa en bloques de 30 segundos para que cada chunk que
genere AnythingLLM tenga suficiente contexto.

Requisitos: pip install youtube-transcript-api

Uso:
    python transcribir_video_youtube.py <URL_o_ID> [idioma]

Ejemplos:
    python transcribir_video_youtube.py https://www.youtube.com/watch?v=SI7O81GMG2A
    python transcribir_video_youtube.py SI7O81GMG2A es
    python transcribir_video_youtube.py dQw4w9WgXcQ en

Si no se pasan argumentos, el script los pide por consola.
"""

from youtube_transcript_api import YouTubeTranscriptApi
import sys
import os
import re


DURACION_BLOQUE = 30  # segundos por bloque


def extraer_video_id(entrada):
    """Extrae el ID del video a partir de una URL de YouTube o un ID directo."""
    # si ya es un ID (11 caracteres alfanumericos)
    if re.match(r'^[\w-]{11}$', entrada):
        return entrada

    # intentar extraer de distintos formatos de URL
    patrones = [
        r'[?&]v=([\w-]{11})',           # youtube.com/watch?v=ID
        r'youtu\.be/([\w-]{11})',        # youtu.be/ID
        r'youtube\.com/embed/([\w-]{11})',  # youtube.com/embed/ID
        r'youtube\.com/shorts/([\w-]{11})', # youtube.com/shorts/ID
    ]
    for patron in patrones:
        match = re.search(patron, entrada)
        if match:
            return match.group(1)

    return None


def descargar_y_formatear(video_id, idioma='es'):
    """Descarga los subtitulos y genera el archivo .txt formateado."""
    url_video = f"https://www.youtube.com/watch?v={video_id}"

    print(f"Descargando subtitulos del video: {url_video}")
    print(f"Idioma: {idioma}")

    api = YouTubeTranscriptApi()

    # intentar con el idioma pedido, si no existe probar con los disponibles
    try:
        transcript = api.fetch(video_id, languages=[idioma])
    except Exception:
        print(f"  No se encontraron subtitulos en '{idioma}', buscando cualquier idioma...")
        transcript = api.fetch(video_id)

    snippets = list(transcript)
    print(f"  Segmentos descargados: {len(snippets)}")

    if not snippets:
        print("ERROR: El video no tiene subtitulos disponibles.")
        return

    # agrupar en bloques de ~30 segundos para que los chunks tengan contexto
    bloques = []
    bloque_actual = {"inicio": 0, "fin": 0, "texto": ""}

    for s in snippets:
        if s.start - bloques[-1]["inicio"] > DURACION_BLOQUE if bloques else s.start > DURACION_BLOQUE:
            if bloque_actual["texto"].strip():
                bloques.append(bloque_actual)
            bloque_actual = {"inicio": s.start, "fin": s.start + s.duration, "texto": ""}

        texto_limpio = s.text.replace('\n', ' ').replace('\u200b', '').strip()
        bloque_actual["texto"] += " " + texto_limpio
        bloque_actual["fin"] = s.start + s.duration

    if bloque_actual["texto"].strip():
        bloques.append(bloque_actual)

    # calcular duracion total
    duracion_total = int(snippets[-1].start + snippets[-1].duration)
    dur_min = duracion_total // 60
    dur_sec = duracion_total % 60

    # generar el documento
    lineas = []
    lineas.append("=" * 60)
    lineas.append(f"TRANSCRIPCION DE VIDEO DE YOUTUBE")
    lineas.append(f"URL: {url_video}")
    lineas.append(f"Duracion aproximada: {dur_min}:{dur_sec:02d}")
    lineas.append(f"Idioma de los subtitulos: {idioma}")
    lineas.append("=" * 60)
    lineas.append("")

    for b in bloques:
        min_inicio = int(b["inicio"] // 60)
        sec_inicio = int(b["inicio"] % 60)
        min_fin = int(b["fin"] // 60)
        sec_fin = int(b["fin"] % 60)

        lineas.append(f"[Minuto {min_inicio:02d}:{sec_inicio:02d} - {min_fin:02d}:{sec_fin:02d}]")
        lineas.append(b["texto"].strip())
        lineas.append("")

    # generar nombre de salida a partir del ID del video
    archivo_salida = f"transcripcion_{video_id}.txt"
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), archivo_salida)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas))

    print(f"\n  Generado: {ruta}")
    print(f"  Bloques de {DURACION_BLOQUE}s: {len(bloques)}")
    print(f"\nAhora sube '{archivo_salida}' a AnythingLLM desde la pestana Documentos.")


if __name__ == "__main__":
    # leer argumentos de la linea de comandos o pedir por consola
    if len(sys.argv) >= 2:
        entrada = sys.argv[1]
        idioma = sys.argv[2] if len(sys.argv) >= 3 else 'es'
    else:
        print("=== Transcriptor de videos de YouTube ===")
        print("Descarga los subtitulos y genera un .txt con marcas de tiempo.\n")
        entrada = input("URL o ID del video de YouTube: ").strip()
        idioma = input("Idioma de los subtitulos (por defecto 'es'): ").strip() or 'es'

    video_id = extraer_video_id(entrada)
    if not video_id:
        print(f"ERROR: No se pudo extraer el ID del video de '{entrada}'")
        print("Introduce una URL de YouTube o un ID de 11 caracteres.")
        sys.exit(1)

    descargar_y_formatear(video_id, idioma)
