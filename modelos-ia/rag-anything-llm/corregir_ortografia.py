"""
Script para corregir tildes, eñes y ortografía en los archivos .txt de la entrega.
Aplica reemplazos cuidando de no modificar nombres de archivos, código, URLs
ni marcas tipo [Pagina XX] / [Minuto XX:XX].
"""

import re
import os

BASE_DIR = r"D:\Tarea 5 RAG"

FILES = [
    os.path.join(BASE_DIR, "Documento_Preprocesado.txt"),
    os.path.join(BASE_DIR, "Informe_de_Uso.txt"),
    os.path.join(BASE_DIR, "Casos_de_Uso.txt"),
]

# Reemplazos simples que se pueden hacer con str.replace
# Formato: (original, corregido)
# Ordenados de más largo a más corto para evitar colisiones
REPLACEMENTS = [
    # -ción / -sión (plurales primero, luego singular)
    ("configuraciones", "configuraciones"),  # ya ok
    ("actualizaciones", "actualizaciones"),  # ya ok
    ("configuracion", "configuración"),
    ("actualizacion", "actualización"),
    ("serializacion", "serialización"),
    ("deserializacion", "deserialización"),
    ("documentacion", "documentación"),
    ("transcripcion", "transcripción"),
    ("programacion", "programación"),
    ("comunicacion", "comunicación"),
    ("confirmacion", "confirmación"),
    ("construccion", "construcción"),
    ("segmentacion", "segmentación"),
    ("instalacion", "instalación"),
    ("interaccion", "interacción"),
    ("abstraccion", "abstracción"),
    ("modificacion", "modificación"),
    ("notificacion", "notificación"),
    ("informacion", "información"),
    ("descripcion", "descripción"),
    ("explicacion", "explicación"),
    ("orientacion", "orientación"),
    ("combinacion", "combinación"),
    ("extraccion", "extracción"),
    ("generacion", "generación"),
    ("aplicacion", "aplicación"),
    ("trazabilidad", "trazabilidad"),  # ya ok
    ("excepcion", "excepción"),
    ("dimension", "dimensión"),
    ("extension", "extensión"),
    ("expresion", "expresión"),
    ("ejecucion", "ejecución"),
    ("operacion", "operación"),
    ("precision", "precisión"),
    ("conexion", "conexión"),
    ("seccion", "sección"),
    ("relacion", "relación"),
    ("solucion", "solución"),
    ("funcion", "función"),
    ("version", "versión"),
    ("opcion", "opción"),
    ("mision", "misión"),
    ("vision", "visión"),

    # Variantes en mayúsculas de -CION
    ("CONFIGURACION", "CONFIGURACIÓN"),
    ("TRANSCRIPCION", "TRANSCRIPCIÓN"),
    ("PROGRAMACION", "PROGRAMACIÓN"),
    ("INTRODUCCION", "INTRODUCCIÓN"),
    ("SEGMENTACION", "SEGMENTACIÓN"),
    ("INSTALACION", "INSTALACIÓN"),
    ("INFORMACION", "INFORMACIÓN"),
    ("DESCRIPCION", "DESCRIPCIÓN"),
    ("EXPLICACION", "EXPLICACIÓN"),
    ("EXTRACCION", "EXTRACCIÓN"),
    ("GENERACION", "GENERACIÓN"),
    ("APLICACION", "APLICACIÓN"),
    ("COMPILACION", "COMPILACIÓN"),
    ("CONEXION", "CONEXIÓN"),
    ("SECCION", "SECCIÓN"),

    # Adverbios en -mente
    ("automaticamente", "automáticamente"),
    ("basicamente", "básicamente"),
    ("graficamente", "gráficamente"),
    ("unicamente", "únicamente"),
    ("especificamente", "específicamente"),
    ("semanticamente", "semánticamente"),
    ("analiticamente", "analíticamente"),
    ("razonablemente", "razonablemente"),  # ok

    # Palabras con tilde - técnicas y comunes
    ("caracteristicas", "características"),
    ("caracteristica", "característica"),
    ("multiplataforma", "multiplataforma"),  # ok
    ("multiplataformas", "multiplataformas"),  # ok
    ("especifico", "específico"),
    ("especifica", "específica"),
    ("especificos", "específicos"),
    ("especificas", "específicas"),
    ("tecnologico", "tecnológico"),
    ("tecnologicos", "tecnológicos"),
    ("tecnologica", "tecnológica"),
    ("tecnologicas", "tecnológicas"),
    ("semantica", "semántica"),
    ("semantico", "semántico"),
    ("imagenes", "imágenes"),
    ("vehiculo", "vehículo"),
    ("vehiculos", "vehículos"),
    ("capitulo", "capítulo"),
    ("capitulos", "capítulos"),
    ("metodos", "métodos"),
    ("metodo", "método"),
    ("codigo", "código"),
    ("codigos", "códigos"),
    ("numero", "número"),
    ("numeros", "números"),
    ("numerico", "numérico"),
    ("numericos", "numéricos"),
    ("parametros", "parámetros"),
    ("parametro", "parámetro"),
    ("tecnicas", "técnicas"),
    ("tecnica", "técnica"),
    ("tecnico", "técnico"),
    ("tecnicos", "técnicos"),
    ("practica", "práctica"),
    ("practicas", "prácticas"),
    ("practico", "práctico"),
    ("paginas", "páginas"),
    # "pagina" se trata con regex por las marcas [Pagina XX]
    ("patron", "patrón"),
    ("patrones", "patrones"),  # ok
    ("logica", "lógica"),
    ("logico", "lógico"),
    ("publicos", "públicos"),
    ("publico", "público"),
    ("publicas", "públicas"),
    ("publica", "pública"),
    ("privados", "privados"),  # ok
    ("titulo", "título"),
    ("titulos", "títulos"),
    ("indice", "índice"),
    ("indices", "índices"),
    ("camara", "cámara"),
    ("camaras", "cámaras"),
    ("unico", "único"),
    ("unicos", "únicos"),
    ("unica", "única"),
    ("unicidad", "unicidad"),  # ok
    ("termino", "término"),
    ("terminos", "términos"),
    ("academicos", "académicos"),
    ("academico", "académico"),
    ("clasico", "clásico"),
    ("clasicos", "clásicos"),

    # Palabras comunes con tilde
    ("tambien", "también"),
    ("ademas", "además"),
    ("aqui", "aquí"),
    ("despues", "después"),
    ("ultimo", "último"),
    ("ultimos", "últimos"),
    ("ultima", "última"),
    ("ultimas", "últimas"),
    ("demas", "demás"),
    ("detras", "detrás"),

    # eñes
    ("disenador", "diseñador"),
    ("disenadora", "diseñadora"),
    ("diseno", "diseño"),
    ("disenos", "diseños"),
    ("tamano", "tamaño"),
    ("tamanos", "tamaños"),
    ("pequeno", "pequeño"),
    ("pequenos", "pequeños"),
    ("pequena", "pequeña"),
    ("pequenas", "pequeñas"),
    ("anade", "añade"),
    ("anadiendo", "añadiendo"),
    ("anadir", "añadir"),
    ("anaden", "añaden"),
    ("anadido", "añadido"),
    ("espanol", "español"),
    ("espanola", "española"),
    ("espanoles", "españoles"),
    (" anos ", " años "),
    (" anos.", " años."),
    (" anos,", " años,"),
    (" ano ", " año "),

    # Nombres propios
    ("Ramirez", "Ramírez"),
    ("Gomez", "Gómez"),
    ("Perez", "Pérez"),
    ("Paez", "Páez"),
    ("Garcia", "García"),
    ("Jalon", "Jalón"),

    # Verbos y otras palabras con tilde
    ("podria", "podría"),
    ("tendria", "tendría"),
    ("habria", "habría"),
    ("seria", "sería"),
    ("estaria", "estaría"),
    ("deberia", "debería"),
    ("necesitaria", "necesitaría"),
    ("sabria", "sabría"),
    ("haria", "haría"),
    ("vendria", "vendría"),
    ("querria", "querría"),
    ("daria", "daría"),
    ("tomaria", "tomaría"),
    ("estarian", "estarían"),

    # Acentos en palabras esdrújulas
    ("basica", "básica"),
    ("basico", "básico"),
    ("basicos", "básicos"),
    ("valida", "válida"),  # cuidado: "valida" como verbo es sin tilde
    ("valido", "válido"),
    ("rapido", "rápido"),
    ("rapida", "rápida"),
    ("rapidos", "rápidos"),

    # Palabras agudas
    ("informara", "informará"),
    ("estara", "estará"),
    ("sabras", "sabrás"),
    ("podras", "podrás"),
    ("saldra", "saldrá"),
    ("veras", "verás"),

    # Otras correcciones
    ("que es", "qué es"),  # NO - esto es peligroso, solo en preguntas
    ("linea", "línea"),
    ("lineas", "líneas"),
]

# Reemplazos que necesitan regex (contexto)
REGEX_REPLACEMENTS = [
    # "pagina" solo cuando NO está dentro de [Pagina XX] o nombre de archivo
    # Reemplazar "pagina" cuando va precedida de espacio/inicio y NO dentro de corchetes
    (r'(?<!\[)(?<![_a-zA-Z])pagina(?![_a-zA-Z\]])(?!\s+\d+\])', 'página'),
    (r'(?<!\[)(?<![_a-zA-Z])Pagina(?![_a-zA-Z\]])(?!\s+\d+\])', 'Página'),

    # "asi" solo como palabra completa (no dentro de "basicamente", etc)
    (r'\basi\b(?! que)', 'así'),
    (r'\bAsi\b', 'Así'),

    # "mas" como adverbio (no dentro de "demas", "ademas", etc)
    # Solo cuando va precedido de espacio y es comparativo
    (r' mas ', ' más '),
    (r' mas,', ' más,'),
    (r' mas\.', ' más.'),
    (r' mas;', ' más;'),

    # Que con tilde en preguntas
    (r'"[Qq]ue es ', '"¿Qué es '),
    (r'"[Qq]ue puesto', '"¿Qué puesto'),
    (r'"[Qq]ue texto', '"¿Qué texto'),
    (r'"[Qq]ue marca', '"¿Qué marca'),
    (r'"[Qq]ue es un', '"¿Qué es un'),

    # Quien con tilde en preguntas
    (r'"[Qq]uien es', '"¿Quién es'),
    (r'"[Qq]uien tiene', '"¿Quién tiene'),

    # Cual con tilde en preguntas
    (r'"[Cc]ual es', '"¿Cuál es'),
    (r'"[Cc]uanto cobra', '"¿Cuánto cobra'),
    (r'"[Cc]uando se', '"¿Cuándo se'),

    # Donde con tilde en preguntas
    (r'"[Dd]onde ', '"¿Dónde '),

    # Interrogaciones de apertura faltantes (si hay ?)
    # Se manejan caso por caso arriba

    # "como" con tilde cuando es pregunta/exclamación
    (r'"[Cc]omo se', '"¿Cómo se'),
]

# Lista de líneas que NO deben modificarse (contienen código, URLs, nombres de archivo)
PROTECTED_PATTERNS = [
    r'^\s{4,}',          # Líneas indentadas (código)
    r'^\t',              # Líneas con tab (código)
    r'https?://',        # URLs
    r'\.py\b',           # Nombres de archivo .py (en la misma línea)
    r'\.cs\b',           # Nombres de archivo .cs
    r'pip install',      # Comandos
    r'python\s+\w',      # Comandos python
    r'dotnet\s+\w',      # Comandos dotnet
    r'from\s+\w',        # Import Python
    r'import\s+\w',      # Import Python
]


def is_code_line(line):
    """Detecta si una línea es código y no debe modificarse."""
    stripped = line.strip()
    # Líneas vacías
    if not stripped:
        return False
    # Líneas indentadas (código)
    if line.startswith("    ") or line.startswith("\t"):
        return True
    # Líneas que son claramente código
    for pattern in PROTECTED_PATTERNS[2:]:  # Skip indentation patterns
        if re.search(pattern, stripped):
            return True
    return False


def apply_replacements(text):
    """Aplica todos los reemplazos al texto, línea por línea."""
    lines = text.split('\n')
    result = []

    for line in lines:
        # Proteger marcas [Pagina XX] y [Minuto XX:XX]
        # Primero extraemos y protegemos las marcas
        protected = {}
        counter = [0]

        def protect(match):
            key = f"__PROTECTED_{counter[0]}__"
            protected[key] = match.group(0)
            counter[0] += 1
            return key

        # Proteger [Pagina XX], nombres de archivo, URLs y código inline
        processed = re.sub(r'\[Pagina \d+\]', protect, line)
        processed = re.sub(r'\[Minuto \d+:\d+ - \d+:\d+\]', protect, line if not protected else processed)
        processed = re.sub(r'\b\w+\.(py|cs|txt|csv|pdf|docx|json|xaml|csproj|md)\b', protect, processed)
        processed = re.sub(r'https?://\S+', protect, processed)

        # Si es línea de código, no tocar
        if line.startswith("    ") or line.startswith("\t"):
            result.append(line)
            continue

        # Aplicar reemplazos simples
        for old, new in REPLACEMENTS:
            if old == new:
                continue
            processed = processed.replace(old, new)

        # Aplicar reemplazos regex
        for pattern, replacement in REGEX_REPLACEMENTS:
            processed = re.sub(pattern, replacement, processed)

        # Restaurar marcas protegidas
        for key, value in protected.items():
            processed = processed.replace(key, value)

        result.append(processed)

    return '\n'.join(result)


def main():
    total_changes = 0

    for filepath in FILES:
        filename = os.path.basename(filepath)
        print(f"\nProcesando: {filename}")

        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

        corrected = apply_replacements(original)

        # Contar cambios
        changes = 0
        orig_lines = original.split('\n')
        corr_lines = corrected.split('\n')
        for o, c in zip(orig_lines, corr_lines):
            if o != c:
                changes += 1

        print(f"  Líneas modificadas: {changes}")
        total_changes += changes

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(corrected)

        print(f"  Guardado: {filepath}")

    print(f"\nTotal líneas modificadas: {total_changes}")


if __name__ == "__main__":
    main()
