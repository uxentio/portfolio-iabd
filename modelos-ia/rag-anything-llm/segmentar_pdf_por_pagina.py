"""
Script para extraer texto de un PDF pagina a pagina y generar
un archivo .txt con marcas [Pagina XX] al inicio de cada linea.

Esto es necesario porque AnythingLLM, al procesar un PDF directamente,
pierde la referencia a la pagina de origen en los chunks. Con este
formato cada chunk siempre contiene la pagina de donde viene el texto.

Requisitos: pip install PyPDF2

Uso:
    python segmentar_pdf_por_pagina.py <archivo.pdf> [pagina_inicio-pagina_fin]

Ejemplos:
    python segmentar_pdf_por_pagina.py manual.pdf
    python segmentar_pdf_por_pagina.py manual.pdf 10-50
    python segmentar_pdf_por_pagina.py aprenda_java_primero.pdf 37-64

Si no se pasan argumentos, el script los pide por consola.
La numeracion de paginas es la del documento (empezando en 1), no la interna del PDF.
"""

from PyPDF2 import PdfReader
import sys
import os
import re


def limpiar_texto(texto):
    """Limpia cabeceras y pies de pagina comunes en PDFs academicos."""
    # quitar cabeceras de copyright tipicas
    texto = re.sub(r'Copyright.*?personales\.\s*', '', texto, flags=re.DOTALL)
    # quitar cabeceras de capitulo repetidas (varios formatos)
    texto = re.sub(r'(ESIISS:.*?p[aá]gina \d+|Cap[ií]tulo \d+:.*?p[aá]gina \d+)\s*', '', texto)
    # quitar numeros de pagina sueltos al principio o final
    texto = re.sub(r'^\s*\d{1,3}\s*$', '', texto, flags=re.MULTILINE)
    return texto.strip()


def segmentar(pdf_path, pagina_inicio=None, pagina_fin=None):
    """Extrae el texto del PDF y genera un .txt con [Pagina XX] en cada linea."""
    if not os.path.exists(pdf_path):
        print(f"ERROR: No se encuentra el PDF '{pdf_path}'")
        return

    print(f"Procesando PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    total_paginas = len(reader.pages)
    print(f"  Paginas totales del PDF: {total_paginas}")

    # determinar rango de paginas a procesar
    if pagina_inicio is None:
        pagina_inicio = 1
    if pagina_fin is None:
        pagina_fin = total_paginas

    # validar rango
    if pagina_inicio < 1 or pagina_fin > total_paginas:
        print(f"ERROR: Rango de paginas invalido ({pagina_inicio}-{pagina_fin}). "
              f"El PDF tiene {total_paginas} paginas.")
        return
    if pagina_inicio > pagina_fin:
        print(f"ERROR: La pagina de inicio ({pagina_inicio}) es mayor que la de fin ({pagina_fin}).")
        return

    print(f"  Procesando paginas {pagina_inicio} a {pagina_fin}")

    # generar cabecera del documento
    nombre_pdf = os.path.basename(pdf_path)
    lineas = []
    lineas.append("=" * 60)
    lineas.append(f"TEXTO EXTRAIDO DE: {nombre_pdf}")
    lineas.append(f"Paginas: {pagina_inicio} a {pagina_fin} (de {total_paginas} totales)")
    lineas.append("=" * 60)
    lineas.append("")

    paginas_procesadas = 0
    paginas_vacias = 0

    for num_pagina in range(pagina_inicio, pagina_fin + 1):
        # PyPDF2 usa indices 0-based
        idx = num_pagina - 1
        texto = reader.pages[idx].extract_text()

        if not texto or len(texto.strip()) < 30:
            paginas_vacias += 1
            continue

        texto = limpiar_texto(texto)
        if len(texto) < 20:
            paginas_vacias += 1
            continue

        # poner [Pagina XX] al inicio de cada linea para que cualquier
        # chunk que genere AnythingLLM siempre contenga la pagina de origen
        parrafos = [p.strip() for p in texto.split('\n') if p.strip()]
        for parrafo in parrafos:
            lineas.append(f"[Pagina {num_pagina}] {parrafo}")
        lineas.append("")
        paginas_procesadas += 1

    # generar nombre de salida a partir del nombre del PDF
    nombre_base = os.path.splitext(nombre_pdf)[0]
    archivo_salida = f"{nombre_base}_segmentado.txt"
    ruta_salida = os.path.join(os.path.dirname(os.path.abspath(pdf_path)), archivo_salida)

    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas))

    print(f"\n  Generado: {ruta_salida}")
    print(f"  Paginas con texto: {paginas_procesadas}")
    if paginas_vacias > 0:
        print(f"  Paginas vacias/sin texto: {paginas_vacias}")
    print(f"\nAhora sube '{archivo_salida}' a AnythingLLM desde la pestana Documentos.")


if __name__ == "__main__":
    # leer argumentos de la linea de comandos o pedir por consola
    if len(sys.argv) >= 2:
        pdf_path = sys.argv[1]
        rango = sys.argv[2] if len(sys.argv) >= 3 else None
    else:
        print("=== Segmentador de PDF por pagina ===")
        print("Extrae el texto de un PDF y genera un .txt con [Pagina XX] en cada linea.\n")
        pdf_path = input("Ruta del archivo PDF: ").strip().strip('"')
        rango = input("Rango de paginas (ej: 10-50, o Enter para todas): ").strip() or None

    # resolver ruta relativa
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pdf_path)

    # parsear rango de paginas
    pagina_inicio = None
    pagina_fin = None
    if rango:
        match = re.match(r'(\d+)\s*-\s*(\d+)', rango)
        if match:
            pagina_inicio = int(match.group(1))
            pagina_fin = int(match.group(2))
        else:
            # si solo ponen un numero, procesar solo esa pagina
            try:
                pagina_inicio = int(rango)
                pagina_fin = int(rango)
            except ValueError:
                print(f"ERROR: Formato de rango invalido '{rango}'. Usa: 10-50")
                sys.exit(1)

    segmentar(pdf_path, pagina_inicio, pagina_fin)
