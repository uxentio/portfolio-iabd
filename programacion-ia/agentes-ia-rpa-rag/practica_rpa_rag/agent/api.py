# API FastAPI que expone el agente con streaming SSE. La consume MAUI.
# El UI bus actúa de intermediario entre el agente (publica) y /chat (lee y emite SSE).
from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# load_dotenv() ya lo hace shared/load_model.py al importarse abajo

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from agent.agent import build_agent, stream_with_feedback as stream_lc  # noqa: E402
from agent.agent_langgraph import build_agent_lg, stream_with_feedback as stream_lg  # noqa: E402
from agent.tools import list_procedures, buscar_libro, listar_catalogo  # noqa: E402
from shared.events import AgentEventType  # noqa: E402
from shared.load_model import (  # noqa: E402
    get_openai_base_url,
    get_openai_model,
)
from shared.ui_bus import bus  # noqa: E402


# Backends disponibles. La API carga los dos al arrancar (`langgraph` y
# `langchain`) y elige uno u otro por petición según lo que pida el cliente
# en el body de POST /chat. El env var `AGENT_BACKEND` solo fija el default
# para clientes que no manden el campo.
_BACKENDS_VALIDOS = ("langgraph", "langchain")
_default_backend = os.getenv("AGENT_BACKEND", "langgraph").lower()
if _default_backend not in _BACKENDS_VALIDOS:
    print(f"(aviso) AGENT_BACKEND='{_default_backend}' no válido. Uso 'langgraph'.")
    _default_backend = "langgraph"


async def _build_checkpointer():
    """AsyncSqliteSaver si está disponible; si no, MemorySaver en RAM.
    La API es async (usa astream del agente), por eso necesita el saver
    asíncrono. La CLI usa SqliteSaver síncrono, no se puede compartir."""
    try:
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        (ROOT / "data").mkdir(exist_ok=True)
        cm = AsyncSqliteSaver.from_conn_string(str(ROOT / "data" / "checkpoints.sqlite"))
        saver = await cm.__aenter__()
        return saver, cm
    except Exception as e:
        print(f"(aviso) AsyncSqliteSaver no disponible, uso MemorySaver: {e}")
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver(), None


def _build_agents(checkpointer, model: str | None = None):
    """Monta los dos agentes (LC y LG) con feedback al UI bus.
    Si `model` es None, usa el del .env. Devuelve dict {nombre: (agent, stream_fn)}."""
    etiqueta_modelo = model or get_openai_model() or "(default)"
    print(f"[api] construyendo backend LangChain · create_agent · modelo={etiqueta_modelo}")
    agente_lc = build_agent(
        checkpointer=checkpointer, hitl=False, ui_feedback=True, model=model,
    )

    print(f"[api] construyendo backend LangGraph · StateGraph custom · modelo={etiqueta_modelo}")
    # hitl_before_run=False: un servidor HTTP no puede hacer input() bloqueante.
    from agent.agent_langgraph import UIFeedbackLGMiddleware
    agente_lg = build_agent_lg(
        checkpointer=checkpointer,
        hitl_before_run=False,
        middlewares=[UIFeedbackLGMiddleware()],
        model=model,
    )
    return {
        "langchain": (agente_lc, stream_lc),
        "langgraph": (agente_lg, stream_lg),
    }


# Se rellena en el lifespan al arrancar.
_agents: dict = {}
_cm = None
_checkpointer = None
# Modelo activo. Inicialmente el del .env; cambia al elegir otro desde
# la UI (lo que reconstruye los dos agentes).
_current_model: str = get_openai_model()
# Lock para evitar reconstrucciones concurrentes.
_rebuild_lock = asyncio.Lock()


def _activar_cache_llm() -> None:
    """Activa caché global de respuestas del LLM en SQLite.

    LangChain pasa por aquí cualquier llamada a un LLM y, si los mismos
    mensajes ya se preguntaron antes, devuelve la respuesta cacheada en
    lugar de re-invocar a LM Studio. En hardware modesto (CPU + GPU 2GB)
    eso ahorra los 60-90 s de prompt eval cuando el agente repite el
    mismo paso (p. ej. arrancar dos veces la misma demo).

    El caché es local y desechable: vive en `data/.llm_cache.sqlite`
    y se puede borrar sin consecuencias.
    """
    try:
        # Ruta canónica en LangChain 1.x. Si la versión instalada todavía
        # expone la legacy en `langchain.cache`, cae al except y reintenta.
        try:
            from langchain_community.cache import SQLiteCache
        except ImportError:
            from langchain.cache import SQLiteCache
        from langchain.globals import set_llm_cache
        cache_path = ROOT / "data" / ".llm_cache.sqlite"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        set_llm_cache(SQLiteCache(database_path=str(cache_path)))
        print(f"[api] cache LLM activo en {cache_path}")
    except Exception as e:
        print(f"(aviso) no pude activar el cache LLM: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Construye checkpointer y los dos agentes, fija el loop del bus, cierra al salir."""
    global _agents, _cm, _checkpointer

    _activar_cache_llm()

    checkpointer, cm = await _build_checkpointer()
    _cm = cm
    _checkpointer = checkpointer
    _agents = _build_agents(checkpointer, model=_current_model or None)
    print(f"[api] backend por defecto: {_default_backend}")
    print(f"[api] modelo activo: {_current_model or '(del .env al arrancar)'}")

    # Fija el loop del servidor para que las tools sync puedan publicar
    # vía loop.call_soon_threadsafe.
    bus.attach_loop(asyncio.get_running_loop())

    try:
        yield
    finally:
        if _cm is not None:
            try:
                await _cm.__aexit__(None, None, None)
            except Exception:
                pass


# --- app ---
app = FastAPI(title="Agente RPA+RAG - API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    thread_id: str = "default"
    message: str
    # Backend del agente para este turno. Si es None, se usa el default
    # del servidor. Valores: "langgraph" o "langchain".
    backend: str | None = None
    # Pausa sintética en milisegundos entre eventos SSE consecutivos.
    # Sirve para pasos por separado en la demo si la API responde demasiado
    # rápido para verlo a ojo (típico cuando el LLM va con GPU potente y el
    # RPA está en headless). 0 = sin pausa. Cap interno a 5000 ms.
    delay_ms: int = 0
    # Nombre del modelo a usar. Si difiere del actualmente cargado, los
    # dos agentes se reconstruyen antes de servir la petición. Si es
    # None, se mantiene el modelo activo del servidor.
    model: str | None = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "default_backend": _default_backend,
        "available_backends": list(_agents.keys()) if _agents else list(_BACKENDS_VALIDOS),
        "current_model": _current_model or None,
    }


@app.get("/backends")
def backends():
    """Lista los backends disponibles y el default. La UI lo consulta al
    arrancar para rellenar su selector."""
    return {
        "available": list(_agents.keys()) if _agents else list(_BACKENDS_VALIDOS),
        "default": _default_backend,
    }


@app.get("/models")
async def models():
    """Proxy a `/v1/models` de LM Studio. Devuelve la lista de modelos
    cargados o disponibles para que la UI rellene su Picker dinámicamente
    en lugar de pedir al usuario que escriba el id a mano."""
    base = get_openai_base_url().rstrip("/")
    url = f"{base}/models"
    try:
        # httpx solo se importa aquí para no obligar a tenerlo si la API
        # se usa offline (los tests no lo necesitan).
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=502,
            detail=f"No pude consultar {url}: {type(e).__name__}: {e}",
        )

    # LM Studio devuelve {"object":"list","data":[{"id":"...", ...}, ...]}
    # Devuelvo la lista de ids más el modelo activo del servidor para que
    # la UI pueda preseleccionarlo.
    items = data.get("data", []) if isinstance(data, dict) else []
    ids = [item.get("id") for item in items if isinstance(item, dict) and item.get("id")]
    return {
        "available": ids,
        "current": _current_model or None,
        "raw": data,
    }


@app.get("/procedures")
def procedures():
    """Inventario de procedimientos. Lo usa la UI al arrancar."""
    return list_procedures.invoke({})


@app.get("/buscar-libro")
async def buscar_libro_endpoint(q: str, by: str = "titulo"):
    """Proxy a la tool buscar_libro: busca en Open Library + Google Books +
    BNE en paralelo y devuelve los candidatos deduplicados. Lo consume el
    formulario web (index.html) para autocompletar campos al dar de alta."""
    if by not in ("titulo", "autor", "isbn"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="by debe ser titulo, autor o isbn")
    # asyncio.to_thread para no bloquear el event loop con el ThreadPoolExecutor
    # interno de la tool (que es síncrono).
    return await asyncio.to_thread(buscar_libro.invoke, {"query": q, "by": by})


@app.get("/catalogo")
async def catalogo_endpoint(q: str | None = None):
    """Proxy a listar_catalogo. Útil para que MAUI o cualquier cliente
    pueda ver el catálogo sin tener que ir directo al :8080."""
    return await asyncio.to_thread(listar_catalogo.invoke, {"filtro": q})


# --- Endpoints de observabilidad: alimentan la pantalla de Logs en MAUI ---

_LOG_FILE = ROOT / "data" / "rpa_ejecucion.log"
_LISTING_DIRS: dict[str, tuple[Path, tuple[str, ...]]] = {
    "screenshots": (ROOT / "data" / "screenshots", (".png", ".jpg", ".jpeg")),
    "traces":      (ROOT / "data" / "traces",      (".zip",)),
    "videos":      (ROOT / "data" / "videos",      (".webm", ".mp4")),
}


def _read_log_tail(n: int) -> dict:
    """Lectura síncrona del log. Va envuelta en asyncio.to_thread desde el
    handler para no bloquear el event loop si el fichero es grande."""
    if not _LOG_FILE.exists():
        return {"path": str(_LOG_FILE), "lines": [], "size_bytes": 0}
    with _LOG_FILE.open("r", encoding="utf-8", errors="replace") as f:
        todas = f.readlines()
    return {
        "path": str(_LOG_FILE),
        "size_bytes": _LOG_FILE.stat().st_size,
        "lines": [linea.rstrip("\n") for linea in todas[-n:]],
    }


@app.get("/logs")
async def logs(tail: int = 200):
    """Devuelve las últimas N líneas del log del runner RPA.
    Lo usa la pantalla de Logs en MAUI para mostrar lo que está haciendo
    el sistema en tiempo real (la UI hace polling cada pocos segundos).
    El IO va a un thread para no bloquear el event loop async."""
    n = max(1, min(int(tail or 200), 2000))
    try:
        return await asyncio.to_thread(_read_log_tail, n)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error leyendo log: {e}")


def _listar_archivos(carpeta: Path, exts: tuple[str, ...]) -> list[dict]:
    """Lista archivos por extensión devolviendo nombre, tamaño y mtime.
    Usa os.scandir para obtener stat sin re-statear cada item al ordenar."""
    if not carpeta.exists():
        return []
    items: list[dict] = []
    with os.scandir(carpeta) as it:
        for entry in it:
            if not entry.is_file(follow_symlinks=False):
                continue
            if Path(entry.name).suffix.lower() not in exts:
                continue
            st = entry.stat(follow_symlinks=False)
            items.append({
                "name": entry.name,
                "size_bytes": st.st_size,
                "mtime": st.st_mtime,
            })
    items.sort(key=lambda d: d["mtime"], reverse=True)
    return items


async def _listing_endpoint(kind: str) -> dict:
    """Factoría compartida para los tres endpoints de listado."""
    carpeta, exts = _LISTING_DIRS[kind]
    items = await asyncio.to_thread(_listar_archivos, carpeta, exts)
    return {"directory": str(carpeta), "items": items}


@app.get("/screenshots")
async def screenshots():
    """Capturas de pantalla generadas por el runner cuando un paso falla.
    Cada item se descarga con GET /screenshots/{name}."""
    return await _listing_endpoint("screenshots")


@app.get("/screenshots/{name}")
def screenshot_file(name: str):
    """Sirve la imagen PNG a la UI con guard de path traversal: resuelvo
    la ruta absoluta y verifico que sigue dentro de _SCREENSHOTS_DIR."""
    from fastapi import HTTPException
    from fastapi.responses import FileResponse
    base, _ = _LISTING_DIRS["screenshots"]
    base_abs = base.resolve()
    ruta = (base / name).resolve()
    try:
        ruta.relative_to(base_abs)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nombre inválido")
    if not ruta.exists() or not ruta.is_file():
        raise HTTPException(status_code=404, detail="Captura no encontrada")
    return FileResponse(str(ruta), media_type="image/png")


@app.get("/traces")
async def traces():
    """Traces de Playwright (RPA_TRACE_ON_ERROR=1).
    Se inspeccionan con `playwright show-trace <archivo>.zip`."""
    return await _listing_endpoint("traces")


@app.get("/videos")
async def videos():
    """Vídeos .webm grabados cuando RPA_RECORD_VIDEO=1."""
    return await _listing_endpoint("videos")


async def _ensure_model(deseado: str | None) -> str:
    """Si llega un modelo distinto al activo, reconstruye los dos agentes
    con el nuevo. Devuelve el modelo que finalmente se está usando."""
    global _agents, _current_model
    if not deseado or deseado == _current_model:
        return _current_model
    async with _rebuild_lock:
        # Re-comprueba dentro del lock por si otro request lo cambió antes.
        if deseado == _current_model:
            return _current_model
        print(f"[api] cambio de modelo: '{_current_model}' -> '{deseado}'. Reconstruyo agentes.")
        nuevos = _build_agents(_checkpointer, model=deseado)
        _agents = nuevos
        _current_model = deseado
    return _current_model


def _sse(event: str, data: dict) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


@app.post("/chat")
async def chat(req: ChatRequest):
    """Recibe un mensaje y devuelve un stream SSE con los eventos del agente.
    El backend se elige por petición: el cliente envía `backend` en el body."""

    # Si la petición pide un modelo distinto al actual, reconstruyo los
    # agentes con el nuevo (con lock para no hacerlo dos veces si dos
    # peticiones llegan a la vez).
    modelo_usado = await _ensure_model(req.model)

    backend = (req.backend or _default_backend).lower()
    if backend not in _agents:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"Backend '{backend}' no soportado. Disponibles: {list(_agents.keys())}",
        )
    agent_actual, stream_fn = _agents[backend]

    # Cap del delay sintético: 0 a 5000 ms. Evita que un cliente pida un
    # delay absurdo y deje colgada la conexión.
    delay_s = max(0, min(int(req.delay_ms or 0), 5000)) / 1000.0

    async def gen():
        # 1) anuncio el backend y el modelo usados en el primer evento.
        yield _sse(AgentEventType.META, {
            "backend": backend,
            "model": modelo_usado,
            "delay_ms": int(delay_s * 1000),
        })

        # 2) abro suscripción al bus para este thread_id
        with bus.subscribe(req.thread_id) as q:
            # 3) lanzo el agente en background (publica eventos en el bus)
            task = asyncio.create_task(stream_fn(agent_actual, req.message, req.thread_id))

            # 4) drenado del bus y emisión de SSE hasta el sentinel.
            # Si delay_s > 0, espero entre eventos para que la demo se vea
            # paso a paso (no afecta a la velocidad del agente, solo a la
            # cadencia con la que llegan al cliente).
            while True:
                event = await q.get()
                if event is None:
                    break
                yield _sse(event["type"], {k: v for k, v in event.items() if k != "type"})
                if delay_s > 0:
                    await asyncio.sleep(delay_s)

            # espero a la task y propago excepciones si las hay
            try:
                await task
            except Exception as e:
                yield _sse(AgentEventType.ERROR, {"message": str(e)})

            yield _sse(AgentEventType.DONE, {})

    return StreamingResponse(gen(), media_type="text/event-stream")
