# Tools del agente. Las docstrings se las lee el LLM (vía @tool), por
# eso describen "cuándo usar esto". HITL solo se aplica a run_workflow.
from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from typing import Annotated

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from shared.load_model import llm  # noqa: E402
from shared.models import build_model_from_schema, validate_params  # noqa: E402
from shared.templating import render_workflow  # noqa: E402
from shared.procedures import load_workflow, iter_workflows  # noqa: E402
from rag.search_procedures import search as _rag_search  # noqa: E402

from agent.runner import run_workflow as _run_workflow_pw  # noqa: E402


def _form_urls() -> dict[str, str]:
    """URLs de los formularios locales, inyectadas al renderizar."""
    base = os.getenv("FORM_URL", "http://localhost:8080/index.html")
    folder = base.rsplit("/", 1)[0]
    return {
        "FORM_URL": base,
        "FORM_URL_BAJA": f"{folder}/baja.html",
        "FORM_URL_AJUSTE_COPIAS": f"{folder}/ajustar_copias.html",
        "FORM_URL_PRESTAMO": f"{folder}/prestamo.html",
        "FORM_URL_DEVOLUCION": f"{folder}/devolucion.html",
    }


# Limpia fences ```json ... ``` que algunos modelos cuantizados añaden.
_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def _strip_fences(msg):
    txt = getattr(msg, "content", str(msg))
    cleaned = _FENCE_RE.sub("", txt.strip())
    return AIMessage(content=cleaned)


# --- tool 1: search_procedures ---
@tool
def search_procedures(
    query: Annotated[str, "Consulta del usuario en lenguaje natural"],
    k: Annotated[int, "Número de resultados a devolver (1-5)"] = 3,
) -> list[dict]:
    """Busca en el RAG los procedimientos más parecidos a la consulta y
    devuelve los top-k con su score y param_schema.

    Úsala como primer paso en cualquier petición que implique HACER algo.
    """
    hits = _rag_search(query, k=max(1, min(k, 5)))
    result = []
    for h in hits:
        wf = load_workflow(h["id"])
        if wf is None:
            continue
        result.append({
            "id": h["id"],
            "titulo": wf["titulo"],
            "descripcion": wf.get("descripcion", ""),
            "score": h["score"],
            "param_schema": wf["param_schema"],
        })
    return result


# --- tool 2: list_procedures ---
@tool
def list_procedures() -> list[dict]:
    """Devuelve el catálogo completo de procedimientos (id, título y
    descripción corta).

    Úsala cuando la petición sea vaga o el usuario pregunte "¿qué puedes hacer?".
    """
    out: list[dict] = []
    for wf in iter_workflows():
        desc = (wf.get("descripcion") or "")[:160]
        out.append({"id": wf["id"], "titulo": wf["titulo"], "descripcion": desc})
    return out


# --- tool 3: extract_parameters ---
def _describe_schema(schema: dict) -> str:
    lines = []
    for name, spec in schema.items():
        t = spec.get("type", "string")
        extra = f"  (valores permitidos: {spec.get('values')})" if t == "enum" else ""
        lines.append(f"- {name}: {t}{extra} — {spec.get('description','')}")
    return "\n".join(lines)


@tool
def extract_parameters(
    request: Annotated[str, "Petición original del usuario, TAL CUAL la escribió"],
    workflow_id: Annotated[str, "id del workflow elegido por search_procedures"],
) -> dict:
    """Extrae los parámetros del workflow desde la petición, los valida
    contra su param_schema (tipos y enums) y los devuelve como dict.

    Úsala después de search_procedures. Si falta algún dato, pregunta al
    usuario antes de ejecutar.
    """
    wf = load_workflow(workflow_id)
    if wf is None:
        return {"error": f"workflow_id '{workflow_id}' no encontrado"}

    schema = wf["param_schema"]
    # Pydantic dinámico construido en runtime desde el param_schema.
    PydanticModel = build_model_from_schema(schema)
    parser = JsonOutputParser(pydantic_object=PydanticModel)

    system_msg = (
        "Eres un extractor de parámetros. A partir de la petición del usuario, "
        "devuelves ÚNICAMENTE un objeto JSON con los campos indicados. "
        "Nada de explicaciones ni fences de markdown.\n\n"
        f"Procedimiento: {wf['titulo']}\n"
        f"Descripción: {wf.get('descripcion','')}\n\n"
        "Parámetros requeridos:\n"
        f"{_describe_schema(schema)}\n\n"
        "Formato del JSON:\n{format_instructions}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "{request}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    # prompt -> LLM -> limpiar fences -> parser JSON.
    chain = prompt | llm | RunnableLambda(_strip_fences) | parser

    try:
        raw = chain.invoke({"request": request})
    except Exception as e:
        return {"error": f"El LLM no devolvió JSON válido: {e}"}

    # Segunda pasada con Pydantic para forzar validación de tipos/enums.
    try:
        validated = validate_params(schema, raw)
    except Exception as e:
        return {"error": f"Validación Pydantic falló: {e}", "raw": raw}

    return validated


# --- tool 4: run_workflow ---
@tool
def run_workflow(
    workflow_id: Annotated[str, "id del workflow a ejecutar"],
    params: Annotated[dict, "Parámetros ya validados que devolvió extract_parameters"],
    headless: Annotated[bool, "True para ejecutar sin ventana visible"] = False,
) -> dict:
    """Ejecuta el workflow en el navegador, sustituyendo placeholders con
    los parámetros recibidos.

    Úsala como paso final, SIEMPRE después de extract_parameters. Si
    devuelve ok=False, cuéntale al usuario qué falló.
    """
    wf = load_workflow(workflow_id)
    if wf is None:
        return {"ok": False, "error": f"workflow_id '{workflow_id}' no encontrado"}

    # Filtra opcionales None: si el agente extrae solo `id_prestamo`, los
    # otros opcionales (id_libro, id_socio) entran como None y el render
    # acaba escribiendo "None" en los inputs del formulario.
    params_limpios = {k: v for k, v in (params or {}).items() if v is not None}

    # Inyecto también las URLs de los formularios locales.
    render_vars = {**params_limpios, **_form_urls()}
    try:
        rendered = render_workflow(wf, render_vars)
    except KeyError as e:
        return {"ok": False, "error": f"Falta un parámetro en el templating: {e}"}

    return _run_workflow_pw(rendered, headless=headless)


# --- tool 5: consultar_libreria_externa ---
# Scraping ligero contra books.toscrape.com (sandbox público).
_BOOKS_URL = "http://books.toscrape.com/"
_HTTP_HEADERS = {
    "User-Agent": "RpaRagAgent/1.0 (educational-project; contact=local)",
    "Accept-Language": "en;q=0.9",
}
_HTTP_TIMEOUT_S = 10
_CACHE_TTL_S = 300   # caché de 5 min para no saturar el servidor con peticiones repetidas
_html_cache: dict[str, tuple[float, str]] = {}


def _fetch_html(url: str) -> str:
    """GET con caché TTL 5 min."""
    import requests   # diferido: no obligar a tenerlo si la tool no se usa
    now = time.monotonic()
    cached = _html_cache.get(url)
    if cached is not None and (now - cached[0]) < _CACHE_TTL_S:
        return cached[1]
    resp = requests.get(url, headers=_HTTP_HEADERS, timeout=_HTTP_TIMEOUT_S)
    resp.raise_for_status()
    # Forzamos UTF-8: si no, requests cae a ISO-8859-1 y rompe el "£".
    resp.encoding = "utf-8"
    html = resp.text
    _html_cache[url] = (now, html)
    return html


@tool
def consultar_libreria_externa(
    consulta: Annotated[str, "Texto a buscar en los títulos de los libros. Vacío o genérico ('listame libros') -> devuelve los primeros."] = "",
    k: Annotated[int, "Número máximo de libros a devolver (1-10)."] = 3,
) -> dict:
    """Consulta el catálogo público de books.toscrape.com como referencia
    externa: devuelve título y disponibilidad de libros publicados.

    Úsala cuando el usuario pregunte por libros que NO están en el fondo
    local de la biblioteca (referencias bibliográficas externas, novedades
    del mercado). NUNCA cites importes monetarios en la respuesta al
    usuario: la sección de biblioteca no vende libros, solo presta los del
    fondo. La cantidad `precio_gbp` se devuelve para uso interno técnico.

    Devuelve dict con ok, total, libros (list de {titulo, precio_gbp,
    stock, url}) y error si ok=False.
    """
    try:
        html = _fetch_html(_BOOKS_URL)
    except Exception as e:
        return {"ok": False, "total": 0, "libros": [], "error": f"No pude consultar la web: {type(e).__name__}: {e}"}

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return {"ok": False, "total": 0, "libros": [], "error": "Falta beautifulsoup4. Instálalo con: pip install beautifulsoup4"}

    soup = BeautifulSoup(html, "html.parser")
    libros: list[dict] = []
    needle = (consulta or "").strip().lower()

    for art in soup.select("article.product_pod"):
        a = art.select_one("h3 a")
        if a is None:
            continue
        titulo = (a.get("title") or a.get_text() or "").strip()
        if needle and needle not in titulo.lower():
            continue
        precio_el = art.select_one("p.price_color")
        stock_el = art.select_one("p.instock.availability")
        precio_txt = (precio_el.get_text() if precio_el else "").strip()
        stock_txt = (stock_el.get_text() if stock_el else "").strip()
        href = a.get("href") or ""
        # Enlaces relativos del tipo "catalogue/<slug>/index.html".
        if href.startswith("http"):
            url = href
        else:
            url = _BOOKS_URL + href.lstrip("./")
        libros.append({
            "titulo": titulo,
            "precio_gbp": precio_txt,
            "stock": stock_txt or "Desconocido",
            "url": url,
        })

    k = max(1, min(int(k), 10))
    return {"ok": True, "total": len(libros), "libros": libros[:k]}


# ---------- Tools del catálogo interno (web_form/server.py) ----------

def _catalogo_base() -> str:
    """Base URL del web_form (donde vive /api/libros). Por defecto :8080."""
    base = os.getenv("FORM_URL", "http://localhost:8080/index.html")
    return base.rsplit("/", 1)[0]


@tool
def listar_catalogo(filtro: str | None = None, max_items: int = 50) -> dict:
    """Lista los libros del fondo de la sección. Usa `filtro` para buscar
    en título/autor/R-NNNN/ISBN/editorial. Esencial para resolver el
    R-NNNN a partir del título antes de baja, préstamo o ajuste."""
    import requests
    url = f"{_catalogo_base()}/api/libros"
    params = {"q": filtro} if filtro else None
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        libros = r.json()
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "libros": []}
    libros = libros[:max_items]
    return {"ok": True, "total": len(libros), "libros": libros}


@tool
def listar_prestamos(socio: str | None = None, libro: str | None = None,
                     incluir_devueltos: bool = False) -> dict:
    """Lista préstamos activos. Filtra por `socio` (S-NNNN) o `libro`
    (R-NNNN). Útil para "qué tiene S-0042", "cuándo vuelve R-0003"."""
    import requests
    params: dict[str, str] = {}
    if socio:
        params["socio"] = socio
    if libro:
        params["libro"] = libro
    if incluir_devueltos:
        params["todos"] = "1"
    try:
        r = requests.get(f"{_catalogo_base()}/api/prestamos", params=params, timeout=5)
        r.raise_for_status()
        prestamos = r.json()
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "prestamos": []}
    return {"ok": True, "total": len(prestamos), "prestamos": prestamos}


# ---------- Tool de búsqueda externa: Open Library + Google Books + BNE ----------

# Caché en memoria para evitar machacar las APIs si el agente repite la
# misma búsqueda en el mismo turno. TTL 5 min como en consultar_libreria_externa.
_busqueda_cache: dict[tuple[str, str], tuple[float, dict]] = {}
_BUSQUEDA_TTL = 300


def _ol_buscar(query: str, by: str, timeout: float) -> list[dict]:
    """Busca en Open Library con preferencia por ediciones en español.
    Si la query con `language=spa` no devuelve resultados, hace fallback
    a la query genérica para no perder libros que solo están catalogados
    en otros idiomas."""
    import requests
    field = {"titulo": "title", "autor": "author", "isbn": "isbn"}.get(by, "title")
    base = f"https://openlibrary.org/search.json?{field}={requests.utils.quote(query)}&limit=5"

    def _fetch(url: str) -> list[dict]:
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "practica-rpa-rag/1.0"})
            r.raise_for_status()
            data = r.json()
        except Exception:
            return []
        out = []
        for doc in (data.get("docs") or [])[:5]:
            autores = doc.get("author_name") or []
            isbns = doc.get("isbn") or []
            out.append({
                "fuente": "OL",
                "titulo": doc.get("title", ""),
                "autor": autores[0] if autores else "",
                "anio": doc.get("first_publish_year"),
                "isbn": isbns[0] if isbns else "",
                "categoria": (doc.get("subject") or [""])[0],
            })
        return out

    # Intento 1: ediciones en español. Devuelve autor en transliteración española
    # y suele incluir ISBN de la edición Cátedra/Alianza/Debate, no del original.
    items = _fetch(base + "&language=spa")
    if items:
        return items
    # Intento 2: sin filtro de idioma para libros que solo están en su idioma original.
    return _fetch(base)


def _gb_buscar(query: str, by: str, timeout: float) -> list[dict]:
    """Busca en Google Books. Devuelve lista normalizada o []."""
    import requests
    prefix = {"titulo": "intitle:", "autor": "inauthor:", "isbn": "isbn:"}.get(by, "intitle:")
    q = f"{prefix}{query}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={requests.utils.quote(q)}&maxResults=5"
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    items = []
    for vol in (data.get("items") or [])[:5]:
        info = vol.get("volumeInfo", {}) or {}
        isbns = [i.get("identifier") for i in (info.get("industryIdentifiers") or [])
                 if i.get("type", "").startswith("ISBN")]
        anio = None
        if info.get("publishedDate"):
            try:
                anio = int(info["publishedDate"][:4])
            except (ValueError, TypeError):
                anio = None
        items.append({
            "fuente": "GBooks",
            "titulo": info.get("title", ""),
            "autor": ", ".join(info.get("authors") or []),
            "anio": anio,
            "isbn": isbns[0] if isbns else "",
            "categoria": (info.get("categories") or [""])[0],
        })
    return items


def _bne_buscar(query: str, by: str, timeout: float) -> list[dict]:
    """Busca en datos.bne.es vía SPARQL. Devuelve lista normalizada o [].
    El servidor de la BNE puede tardar varios segundos; con timeout corto
    se descarta y los resultados de OL/GBooks llegan igual."""
    import requests
    # Filtro SPARQL distinto según el campo de búsqueda. Uso CONTAINS y
    # LCASE para hacer coincidencia parcial insensible a mayúsculas.
    if by == "isbn":
        filtro = f'CONTAINS(STR(?isbn), "{query}")'
    elif by == "autor":
        filtro = f'CONTAINS(LCASE(STR(?autor)), LCASE("{query}"))'
    else:
        filtro = f'CONTAINS(LCASE(STR(?titulo)), LCASE("{query}"))'

    sparql = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX bne:  <http://datos.bne.es/def/>
        SELECT ?titulo ?autor ?isbn ?anio WHERE {{
            ?obra a bne:C1005 ;
                  rdfs:label ?titulo .
            OPTIONAL {{ ?obra bne:OP5001 ?personaObj . ?personaObj rdfs:label ?autor . }}
            OPTIONAL {{ ?obra bne:P3013 ?isbn . }}
            OPTIONAL {{ ?obra bne:P3001 ?anio . }}
            FILTER ({filtro})
        }} LIMIT 5
    """.strip()

    try:
        r = requests.get(
            "https://datos.bne.es/sparql",
            params={"query": sparql, "format": "application/sparql-results+json"},
            timeout=timeout,
            headers={"Accept": "application/sparql-results+json"},
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    items = []
    for binding in (data.get("results", {}).get("bindings", []) or [])[:5]:
        anio_raw = binding.get("anio", {}).get("value", "")
        anio = None
        if anio_raw:
            m = re.search(r"\d{4}", anio_raw)
            if m:
                try:
                    anio = int(m.group(0))
                except ValueError:
                    anio = None
        items.append({
            "fuente": "BNE",
            "titulo": binding.get("titulo", {}).get("value", ""),
            "autor": binding.get("autor", {}).get("value", ""),
            "anio": anio,
            "isbn": binding.get("isbn", {}).get("value", ""),
            "categoria": "",
        })
    return items


def _normalizar_titulo(t: str) -> str:
    """Quita acentos, signos y palabras vacías para comparar títulos.
    'Crimen y Castigo' y 'crimen y castigo' colapsan a la misma clave."""
    import unicodedata
    s = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()
    return re.sub(r"\s+", " ", s)


def _mezclar_y_deduplicar(grupos: list[list[dict]]) -> list[dict]:
    """Une los resultados de las 3 fuentes y deduplica por ISBN (preferido)
    o por titulo+primer_apellido_autor normalizados. Si dos fuentes
    describen el mismo libro, conserva el más completo (más campos no
    vacíos)."""
    candidatos: list[dict] = []
    for grupo in grupos:
        candidatos.extend(grupo or [])

    def clave(c: dict) -> str:
        # ISBN si existe es el mejor identificador.
        if c.get("isbn"):
            return "isbn:" + re.sub(r"[^0-9Xx]", "", c["isbn"]).lower()
        # Si no, titulo normalizado + primer apellido del autor.
        autor = c.get("autor", "")
        primer_apellido = autor.split(",")[0].strip() if "," in autor else autor.split()[0] if autor else ""
        return f"t:{_normalizar_titulo(c.get('titulo',''))}|a:{_normalizar_titulo(primer_apellido)}"

    def completitud(c: dict) -> int:
        return sum(1 for v in c.values() if v)

    bucket: dict[str, dict] = {}
    for c in candidatos:
        k = clave(c)
        if not k or k.endswith("|a:"):
            continue
        if k not in bucket or completitud(c) > completitud(bucket[k]):
            bucket[k] = c

    # Orden: primero los que tienen ISBN, después por completitud.
    return sorted(bucket.values(),
                  key=lambda c: (1 if c.get("isbn") else 0, completitud(c)),
                  reverse=True)[:10]


@tool
def buscar_libro(query: str, by: str = "titulo", timeout_s: float = 8.0) -> dict:
    """Busca metadatos de un libro en Open Library + Google Books + BNE en
    paralelo. `by`: "titulo" (default), "autor" o "isbn". Devuelve hasta
    10 candidatos con autor, año, ISBN y categoría. Úsala cuando se da de
    alta un libro y faltan datos."""
    import concurrent.futures
    cache_key = (by, query.lower().strip())
    if cache_key in _busqueda_cache:
        ts, payload = _busqueda_cache[cache_key]
        if time.time() - ts < _BUSQUEDA_TTL:
            return payload

    funciones = {
        "OL":     lambda: _ol_buscar(query, by, timeout_s),
        "GBooks": lambda: _gb_buscar(query, by, timeout_s),
        "BNE":    lambda: _bne_buscar(query, by, timeout_s),
    }
    resultados: dict[str, list[dict]] = {}
    fallos: list[str] = []
    # Threads en paralelo para ganar latencia: total ≈ max(timeouts) en lugar de suma.
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futuros = {ex.submit(fn): nombre for nombre, fn in funciones.items()}
        for fut in concurrent.futures.as_completed(futuros, timeout=timeout_s + 2):
            nombre = futuros[fut]
            try:
                resultados[nombre] = fut.result(timeout=0.1) or []
            except Exception:
                resultados[nombre] = []
                fallos.append(nombre)

    candidatos = _mezclar_y_deduplicar(list(resultados.values()))
    payload = {
        "ok": True,
        "candidatos": candidatos,
        "fuentes_ok": [n for n, lst in resultados.items() if lst and n not in fallos],
        "fuentes_fallo": fallos + [n for n, lst in resultados.items() if not lst and n not in fallos],
    }
    _busqueda_cache[cache_key] = (time.time(), payload)
    return payload


# Lista que registran agent.py y agent_langgraph.py.
ALL_TOOLS = [
    search_procedures,
    list_procedures,
    extract_parameters,
    run_workflow,
    consultar_libreria_externa,
    listar_catalogo,
    listar_prestamos,
    buscar_libro,
]
