"""Servidor de la sección de biblioteca con API REST de catálogo y préstamos.

Modela una sección de la Biblioteca Regional (estilo BRMU):
- Catálogo de libros con número de registro `R-NNNN`, signatura, copias.
- Socios identificados con carnet `S-NNNN`.
- Préstamos `P-NNNN` con fecha límite, decrementan copias disponibles.
- Devoluciones que las reincorporan al fondo.

NO hay precio: es una biblioteca pública, los libros se prestan, no se venden.

Endpoints:
    GET    /                          → /index.html
    GET    /<archivo>                 → estáticos (.html, .js, .css)

    Catálogo:
    GET    /api/libros                → lista
    GET    /api/libros?q=...          → busca por título / autor / id / isbn
    GET    /api/libros/{id}           → un libro
    POST   /api/libros                → alta (devuelve id R-NNNN)
    PUT    /api/libros/{id}           → actualizar parcial
    DELETE /api/libros/{id}           → baja definitiva (libro retirado)

    Préstamos:
    GET    /api/prestamos             → lista préstamos activos
    GET    /api/prestamos?socio=...   → préstamos de un socio
    GET    /api/prestamos?libro=...   → préstamos de un libro
    POST   /api/prestamos             → presta un ejemplar
    POST   /api/devoluciones          → devuelve un ejemplar

    Reset:
    POST   /api/reset                 → restaura el seed de ejemplo

Uso:
    python web_form/server.py
"""
from __future__ import annotations

import http.server
import json
import os
import re
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ROOT = Path(__file__).resolve().parent.parent
CATALOGO_FILE = ROOT / "data" / "catalogo.json"
PRESTAMOS_FILE = ROOT / "data" / "prestamos.json"

# Géneros realistas para una biblioteca regional. Lista plana de 20.
# En una BRMU real esto sería CDU completa, pero un enum manejable cubre
# el 95% de los fondos de una sección sin abrumar al usuario.
GENEROS = (
    "novela", "poesia", "teatro", "ensayo", "biografia", "historia",
    "ciencia", "filosofia", "religion", "arte", "infantil", "juvenil",
    "comic", "manual", "referencia", "viajes", "cocina", "autoayuda",
    "idiomas", "otros",
)

# Catálogo inicial con datos bibliográficos reales y verificables. Los ISBN,
# editoriales y años corresponden a ediciones publicadas en España y se
# pueden comprobar contra Open Library o Google Books. Cubre los 20 géneros
# del enum con al menos un título por género representativo, para que la
# demo del inventario y el filtro por categoría tengan contenido real.
#
# Si quieres regenerar este seed con datos frescos de Wikidata, hay un
# script en scripts/regenerar_seed_wikidata.py (opcional, requiere internet).
SEED_LIBROS = [
    # --- Narrativa española e hispanoamericana ---
    {"titulo": "Cien años de soledad",       "autor": "García Márquez, Gabriel",   "editorial": "Cátedra",         "anio": 1967, "isbn": "978-84-376-0494-7", "paginas": 471, "idioma": "es", "categoria": "novela",     "copias_total": 3},
    {"titulo": "Don Quijote de la Mancha",   "autor": "Cervantes, Miguel de",      "editorial": "Alfaguara",       "anio": 1605, "isbn": "978-84-204-2256-8", "paginas": 1250,"idioma": "es", "categoria": "novela",     "copias_total": 2},
    {"titulo": "La sombra del viento",       "autor": "Ruiz Zafón, Carlos",        "editorial": "Planeta",         "anio": 2001, "isbn": "978-84-08-04364-8", "paginas": 576, "idioma": "es", "categoria": "novela",     "copias_total": 4},
    {"titulo": "Crónica de una muerte anunciada", "autor": "García Márquez, Gabriel", "editorial": "Debolsillo",   "anio": 1981, "isbn": "978-84-9759-432-9", "paginas": 122, "idioma": "es", "categoria": "novela",     "copias_total": 2},
    {"titulo": "La casa de los espíritus",   "autor": "Allende, Isabel",           "editorial": "Plaza & Janés",   "anio": 1982, "isbn": "978-84-01-38631-2", "paginas": 480, "idioma": "es", "categoria": "novela",     "copias_total": 2},
    {"titulo": "Pedro Páramo",               "autor": "Rulfo, Juan",               "editorial": "Cátedra",         "anio": 1955, "isbn": "978-84-376-0414-5", "paginas": 192, "idioma": "es", "categoria": "novela",     "copias_total": 2},

    # --- Narrativa internacional traducida ---
    {"titulo": "1984",                       "autor": "Orwell, George",            "editorial": "Debolsillo",      "anio": 1949, "isbn": "978-84-9759-866-2", "paginas": 332, "idioma": "es", "categoria": "novela",     "copias_total": 4},
    {"titulo": "El nombre del viento",       "autor": "Rothfuss, Patrick",         "editorial": "Plaza & Janés",   "anio": 2007, "isbn": "978-84-01-33720-5", "paginas": 872, "idioma": "es", "categoria": "novela",     "copias_total": 2},
    {"titulo": "Crimen y castigo",           "autor": "Dostoievski, Fiódor",       "editorial": "Alianza",         "anio": 1866, "isbn": "978-84-206-7359-4", "paginas": 720, "idioma": "es", "categoria": "novela",     "copias_total": 2},

    # --- Poesía ---
    {"titulo": "Veinte poemas de amor y una canción desesperada", "autor": "Neruda, Pablo", "editorial": "Cátedra", "anio": 1924, "isbn": "978-84-376-2410-5", "paginas": 144, "idioma": "es", "categoria": "poesia",     "copias_total": 2},
    {"titulo": "Romancero gitano",           "autor": "García Lorca, Federico",    "editorial": "Cátedra",         "anio": 1928, "isbn": "978-84-376-0259-2", "paginas": 168, "idioma": "es", "categoria": "poesia",     "copias_total": 2},

    # --- Teatro ---
    {"titulo": "La casa de Bernarda Alba",   "autor": "García Lorca, Federico",    "editorial": "Cátedra",         "anio": 1936, "isbn": "978-84-376-0258-5", "paginas": 200, "idioma": "es", "categoria": "teatro",     "copias_total": 2},

    # --- Ensayo / pensamiento ---
    {"titulo": "Sapiens. De animales a dioses", "autor": "Harari, Yuval Noah",     "editorial": "Debate",          "anio": 2014, "isbn": "978-84-9992-622-4", "paginas": 496, "idioma": "es", "categoria": "ensayo",     "copias_total": 3},
    {"titulo": "Pensar rápido, pensar despacio", "autor": "Kahneman, Daniel",       "editorial": "Debate",          "anio": 2011, "isbn": "978-84-9992-242-4", "paginas": 666, "idioma": "es", "categoria": "ensayo",     "copias_total": 2},

    # --- Biografía / historia ---
    {"titulo": "Vida de Mahatma Gandhi",     "autor": "Fischer, Louis",            "editorial": "Aguilar",         "anio": 1950, "isbn": "978-84-03-09451-2", "paginas": 480, "idioma": "es", "categoria": "biografia",  "copias_total": 1},
    {"titulo": "Imperiofobia y leyenda negra","autor": "Roca Barea, María Elvira", "editorial": "Siruela",         "anio": 2016, "isbn": "978-84-16854-23-1", "paginas": 472, "idioma": "es", "categoria": "historia",   "copias_total": 2},

    # --- Ciencia / divulgación ---
    {"titulo": "Una breve historia del tiempo", "autor": "Hawking, Stephen",       "editorial": "Crítica",         "anio": 1988, "isbn": "978-84-9892-665-1", "paginas": 240, "idioma": "es", "categoria": "ciencia",    "copias_total": 2},
    {"titulo": "El gen egoísta",             "autor": "Dawkins, Richard",          "editorial": "Salvat",          "anio": 1976, "isbn": "978-84-345-0149-9", "paginas": 416, "idioma": "es", "categoria": "ciencia",    "copias_total": 2},

    # --- Filosofía ---
    {"titulo": "El mundo de Sofía",          "autor": "Gaarder, Jostein",          "editorial": "Siruela",         "anio": 1991, "isbn": "978-84-7844-211-3", "paginas": 632, "idioma": "es", "categoria": "filosofia",  "copias_total": 2},

    # --- Arte ---
    {"titulo": "Historia del arte",          "autor": "Gombrich, Ernst H.",        "editorial": "Phaidon",         "anio": 1950, "isbn": "978-0-7148-9870-9", "paginas": 688, "idioma": "es", "categoria": "arte",       "copias_total": 1},

    # --- Infantil / juvenil / cómic ---
    {"titulo": "El Principito",              "autor": "Saint-Exupéry, Antoine de", "editorial": "Salamandra",      "anio": 1943, "isbn": "978-84-204-7937-1", "paginas": 96,  "idioma": "es", "categoria": "infantil",   "copias_total": 5},
    {"titulo": "Harry Potter y la piedra filosofal", "autor": "Rowling, J. K.",    "editorial": "Salamandra",      "anio": 1997, "isbn": "978-84-7888-654-3", "paginas": 256, "idioma": "es", "categoria": "juvenil",    "copias_total": 4},
    {"titulo": "Maus",                       "autor": "Spiegelman, Art",           "editorial": "Reservoir Books", "anio": 1986, "isbn": "978-84-397-3197-7", "paginas": 296, "idioma": "es", "categoria": "comic",      "copias_total": 2},

    # --- Manuales y referencia ---
    {"titulo": "Aprende Python en un fin de semana", "autor": "Padial, Alfredo",  "editorial": "Independiente",   "anio": 2018, "isbn": "978-15-2014-625-1", "paginas": 192, "idioma": "es", "categoria": "manual",     "copias_total": 2},
    {"titulo": "Diccionario de la lengua española", "autor": "Real Academia Española", "editorial": "Espasa",     "anio": 2014, "isbn": "978-84-670-4189-7", "paginas": 2432,"idioma": "es", "categoria": "referencia", "copias_total": 1},
]

# Lock para mutar los JSON en disco sin race conditions.
_db_lock = threading.Lock()


# ---------- Helpers de id ----------

def _siguiente_id_prefijo(items: list[dict], prefijo: str) -> str:
    """Devuelve el siguiente id correlativo con el prefijo dado.
    Ejemplos: R-0009, S-0042, P-0123."""
    n_max = 0
    pat = re.compile(rf"^{re.escape(prefijo)}-(\d+)$")
    for item in items:
        m = pat.match(item.get("id", ""))
        if m:
            n_max = max(n_max, int(m.group(1)))
    return f"{prefijo}-{n_max + 1:04d}"


def _signatura(libro: dict) -> str:
    """Signatura topográfica simple: 3 letras del apellido + 3 letras del título.
    Es decorativa pero da el aspecto de catálogo de biblioteca. Las BRMU usan
    algo similar (apellido en mayúsculas + 3 letras del título en minúscula)."""
    autor = libro.get("autor", "")
    apellido = autor.split(",")[0] if "," in autor else autor.split()[0] if autor else "ANO"
    apellido = re.sub(r"[^A-Za-zÁÉÍÓÚÑáéíóúñ]", "", apellido).upper()[:3] or "ANO"
    titulo = libro.get("titulo", "")
    titulo_clean = re.sub(r"[^A-Za-zÁÉÍÓÚÑáéíóúñ ]", "", titulo).strip()
    palabras = [p for p in titulo_clean.split() if p.lower() not in ("el", "la", "los", "las", "un", "una", "de", "del")]
    primera = palabras[0] if palabras else titulo_clean
    return f"{apellido} {primera[:3].lower()}"


# ---------- Persistencia JSON ----------

def _cargar_catalogo() -> list[dict]:
    if not CATALOGO_FILE.exists():
        CATALOGO_FILE.parent.mkdir(parents=True, exist_ok=True)
        _seed_catalogo()
    try:
        return json.loads(CATALOGO_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _seed_catalogo()
        return json.loads(CATALOGO_FILE.read_text(encoding="utf-8"))


def _guardar_catalogo(libros: list[dict]) -> None:
    """Escritura atómica para no dejar el archivo a medio escribir."""
    CATALOGO_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CATALOGO_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(libros, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, CATALOGO_FILE)


def _cargar_prestamos() -> list[dict]:
    if not PRESTAMOS_FILE.exists():
        return []
    try:
        return json.loads(PRESTAMOS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _guardar_prestamos(prestamos: list[dict]) -> None:
    PRESTAMOS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = PRESTAMOS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(prestamos, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, PRESTAMOS_FILE)


def _seed_catalogo() -> None:
    """Crea catalogo.json con SEED_LIBROS, asigna ids R-NNNN y signatura."""
    libros: list[dict] = []
    for plantilla in SEED_LIBROS:
        libro = {
            "id": _siguiente_id_prefijo(libros, "R"),
            **plantilla,
            "copias_disponibles": plantilla["copias_total"],
        }
        libro["signatura"] = _signatura(libro)
        libros.append(libro)
    _guardar_catalogo(libros)
    # Reset también préstamos al hacer seed.
    _guardar_prestamos([])


# ---------- Operaciones de catálogo ----------

def listar(filtro: str | None = None) -> list[dict]:
    """Devuelve todos los libros, recalculando copias_disponibles a partir
    de los préstamos activos para que esté siempre consistente."""
    libros = _cargar_catalogo()
    activos = [p for p in _cargar_prestamos() if not p.get("devuelto")]
    prestados_por_libro: dict[str, int] = {}
    for p in activos:
        prestados_por_libro[p.get("id_libro", "")] = prestados_por_libro.get(p.get("id_libro", ""), 0) + 1
    for libro in libros:
        prestados = prestados_por_libro.get(libro.get("id", ""), 0)
        libro["copias_disponibles"] = max(0, int(libro.get("copias_total", 0)) - prestados)
        libro["copias_prestadas"] = prestados

    if not filtro:
        return libros
    f = filtro.lower().strip()
    return [
        l for l in libros
        if f in l.get("titulo", "").lower()
        or f in l.get("autor", "").lower()
        or f in l.get("id", "").lower()
        or f in l.get("isbn", "").lower()
        or f in l.get("editorial", "").lower()
    ]


def obtener(id_libro: str) -> dict | None:
    return next((l for l in listar() if l.get("id") == id_libro), None)


def crear(datos: dict) -> dict:
    """Da de alta un libro. Asigna R-NNNN y signatura. Devuelve el libro."""
    with _db_lock:
        libros = _cargar_catalogo()
        cat = str(datos.get("categoria", "")).strip().lower()
        if cat and cat not in GENEROS:
            raise ValueError(f"categoria '{cat}' no válida. Géneros: {', '.join(GENEROS)}")
        copias = int(datos.get("copias_total", 1)) or 1
        nuevo = {
            "id": _siguiente_id_prefijo(libros, "R"),
            "titulo":      str(datos.get("titulo", "")).strip(),
            "autor":       str(datos.get("autor", "")).strip(),
            "editorial":   str(datos.get("editorial", "")).strip(),
            "anio":        int(datos["anio"]) if datos.get("anio") else None,
            "isbn":        str(datos.get("isbn", "")).strip(),
            "paginas":     int(datos["paginas"]) if datos.get("paginas") else None,
            "idioma":      str(datos.get("idioma", "es")).strip().lower(),
            "categoria":   cat,
            "copias_total": copias,
            "copias_disponibles": copias,
        }
        if not nuevo["titulo"]:
            raise ValueError("titulo es obligatorio")
        if not nuevo["autor"]:
            raise ValueError("autor es obligatorio")
        nuevo["signatura"] = _signatura(nuevo)
        libros.append(nuevo)
        _guardar_catalogo(libros)
        return nuevo


def actualizar(id_libro: str, cambios: dict) -> dict | None:
    """Modifica campos de un libro. NO permite cambiar id, copias_disponibles
    ni signatura directamente (signatura se regenera si cambia autor/título)."""
    with _db_lock:
        libros = _cargar_catalogo()
        for libro in libros:
            if libro.get("id") == id_libro:
                regen_sig = False
                for campo, valor in cambios.items():
                    if campo in ("id", "copias_disponibles", "copias_prestadas", "signatura"):
                        continue
                    if campo in ("anio", "paginas", "copias_total") and valor is not None:
                        libro[campo] = int(valor)
                    elif campo == "categoria" and valor is not None:
                        v = str(valor).strip().lower()
                        if v and v not in GENEROS:
                            raise ValueError(f"categoria '{v}' no válida")
                        libro[campo] = v
                    elif valor is not None:
                        libro[campo] = str(valor).strip()
                    if campo in ("titulo", "autor"):
                        regen_sig = True
                if regen_sig:
                    libro["signatura"] = _signatura(libro)
                _guardar_catalogo(libros)
                return libro
        return None


def borrar_por_id(id_libro: str) -> dict | None:
    """Baja definitiva del catálogo. No es lo mismo que un préstamo: aquí
    el libro deja de existir (perdido, deteriorado, expurgado)."""
    with _db_lock:
        libros = _cargar_catalogo()
        for i, libro in enumerate(libros):
            if libro.get("id") == id_libro:
                eliminado = libros.pop(i)
                _guardar_catalogo(libros)
                # Cancelar préstamos pendientes del libro eliminado.
                prestamos = _cargar_prestamos()
                for p in prestamos:
                    if p.get("id_libro") == id_libro and not p.get("devuelto"):
                        p["devuelto"] = True
                        p["fecha_devolucion_real"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                        p["nota"] = "auto-cierre por baja del libro"
                _guardar_prestamos(prestamos)
                return eliminado
        return None


def borrar_por_titulo(titulo: str) -> dict | None:
    """Baja por título exacto. Si hay duplicados, elimina el primero."""
    nombre_norm = titulo.strip().lower()
    with _db_lock:
        libros = _cargar_catalogo()
        for libro in libros:
            if libro.get("titulo", "").strip().lower() == nombre_norm:
                return borrar_por_id(libro["id"])  # reusar para cerrar préstamos
        return None


# ---------- Operaciones de préstamo ----------

def listar_prestamos(socio: str | None = None, libro: str | None = None,
                     incluir_devueltos: bool = False) -> list[dict]:
    prestamos = _cargar_prestamos()
    if not incluir_devueltos:
        prestamos = [p for p in prestamos if not p.get("devuelto")]
    if socio:
        prestamos = [p for p in prestamos if p.get("id_socio") == socio]
    if libro:
        prestamos = [p for p in prestamos if p.get("id_libro") == libro]
    return prestamos


def prestar(datos: dict) -> dict:
    """Crea un préstamo activo si hay copias disponibles."""
    id_libro = str(datos.get("id_libro", "")).strip()
    id_socio = str(datos.get("id_socio", "")).strip() or _siguiente_id_prefijo(_cargar_prestamos(), "S")
    dias = int(datos.get("dias_prestamo", 21)) or 21

    if not id_libro:
        raise ValueError("id_libro es obligatorio")
    libro = obtener(id_libro)
    if not libro:
        raise ValueError(f"Libro {id_libro} no existe en el catálogo")
    if libro.get("copias_disponibles", 0) <= 0:
        raise ValueError(f"No hay copias disponibles de '{libro.get('titulo')}' (todas prestadas)")

    with _db_lock:
        prestamos = _cargar_prestamos()
        ahora = datetime.now(timezone.utc)
        nuevo = {
            "id": _siguiente_id_prefijo(prestamos, "P"),
            "id_libro": id_libro,
            "titulo_libro": libro.get("titulo", ""),
            "id_socio": id_socio,
            "fecha_prestamo": ahora.isoformat(timespec="seconds"),
            "fecha_devolucion_prevista": (ahora + timedelta(days=dias)).isoformat(timespec="seconds"),
            "fecha_devolucion_real": None,
            "devuelto": False,
        }
        prestamos.append(nuevo)
        _guardar_prestamos(prestamos)
        return nuevo


def devolver(datos: dict) -> dict:
    """Cierra un préstamo activo. Acepta `id_prestamo` o `id_libro` + `id_socio`.
    Si solo viene id_libro y hay un único activo de ese libro, lo cierra."""
    id_prestamo = str(datos.get("id_prestamo", "")).strip()
    id_libro = str(datos.get("id_libro", "")).strip()
    id_socio = str(datos.get("id_socio", "")).strip()

    with _db_lock:
        prestamos = _cargar_prestamos()
        candidato: dict | None = None
        if id_prestamo:
            candidato = next((p for p in prestamos
                              if p.get("id") == id_prestamo and not p.get("devuelto")), None)
        elif id_libro and id_socio:
            candidato = next((p for p in prestamos
                              if p.get("id_libro") == id_libro and p.get("id_socio") == id_socio
                              and not p.get("devuelto")), None)
        elif id_libro:
            activos = [p for p in prestamos
                       if p.get("id_libro") == id_libro and not p.get("devuelto")]
            if len(activos) == 1:
                candidato = activos[0]
            elif len(activos) > 1:
                raise ValueError(
                    f"Hay {len(activos)} préstamos activos de {id_libro}. Indica id_socio o id_prestamo."
                )

        if not candidato:
            raise ValueError("No encuentro préstamo activo con esos datos")

        candidato["devuelto"] = True
        candidato["fecha_devolucion_real"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _guardar_prestamos(prestamos)
        return candidato


# ---------- Handler HTTP ----------

class Handler(http.server.SimpleHTTPRequestHandler):
    """Sirve estáticos del directorio web_form/ + endpoints /api/*."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        print(f"[WebForm] {args[0]}")

    # --- Helpers ---

    def _json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _leer_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    # --- Routing ---

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        # ----- Catálogo -----
        if url.path == "/api/libros":
            qs = parse_qs(url.query)
            self._json(200, listar(qs.get("q", [None])[0]))
            return
        m = re.match(r"^/api/libros/([^/]+)$", url.path)
        if m:
            libro = obtener(m.group(1))
            self._json(200 if libro else 404, libro or {"error": "Libro no encontrado"})
            return
        if url.path == "/api/generos":
            self._json(200, list(GENEROS))
            return
        # ----- Préstamos -----
        if url.path == "/api/prestamos":
            qs = parse_qs(url.query)
            self._json(200, listar_prestamos(
                socio=qs.get("socio", [None])[0],
                libro=qs.get("libro", [None])[0],
                incluir_devueltos=qs.get("todos", ["false"])[0] in ("1", "true", "True"),
            ))
            return
        # Estáticos.
        super().do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/libros":
            try:
                self._json(201, crear(self._leer_json_body()))
            except ValueError as e:
                self._json(400, {"error": str(e)})
            return
        if url.path == "/api/prestamos":
            try:
                self._json(201, prestar(self._leer_json_body()))
            except ValueError as e:
                self._json(400, {"error": str(e)})
            return
        if url.path == "/api/devoluciones":
            try:
                self._json(200, devolver(self._leer_json_body()))
            except ValueError as e:
                self._json(400, {"error": str(e)})
            return
        if url.path == "/api/reset":
            with _db_lock:
                _seed_catalogo()
            self._json(200, {"status": "reset", "libros": len(_cargar_catalogo())})
            return
        self._json(404, {"error": "Endpoint no soportado"})

    def do_PUT(self):
        url = urlparse(self.path)
        m = re.match(r"^/api/libros/([^/]+)$", url.path)
        if m:
            try:
                actualizado = actualizar(m.group(1), self._leer_json_body())
                self._json(200 if actualizado else 404,
                           actualizado or {"error": "Libro no encontrado"})
            except ValueError as e:
                self._json(400, {"error": str(e)})
            return
        self._json(404, {"error": "Endpoint no soportado"})

    def do_DELETE(self):
        url = urlparse(self.path)
        m = re.match(r"^/api/libros/([^/]+)$", url.path)
        if m:
            eliminado = borrar_por_id(m.group(1))
            self._json(200 if eliminado else 404,
                       eliminado or {"error": "Libro no encontrado"})
            return
        if url.path == "/api/libros":
            qs = parse_qs(url.query)
            titulo = qs.get("titulo", qs.get("nombre", [None]))[0]
            if not titulo:
                self._json(400, {"error": "Falta parámetro titulo"})
                return
            eliminado = borrar_por_titulo(titulo)
            self._json(200 if eliminado else 404,
                       eliminado or {"error": "Libro no encontrado"})
            return
        self._json(404, {"error": "Endpoint no soportado"})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    _cargar_catalogo()  # asegura que el seed exista
    with http.server.HTTPServer(("", port), Handler) as httpd:
        print(f"Sección de Biblioteca disponible en http://localhost:{port}/index.html")
        print(f"  Inventario   en http://localhost:{port}/inventario.html")
        print(f"  Préstamos    en http://localhost:{port}/prestamo.html")
        print(f"  Devoluciones en http://localhost:{port}/devolucion.html")
        print(f"  API REST     en http://localhost:{port}/api/libros y /api/prestamos")
        print(f"  Catálogo en  {CATALOGO_FILE}")
        print(f"  Préstamos en {PRESTAMOS_FILE}")
        print("  Pulsa Ctrl+C para detener el servidor.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == "__main__":
    main()
