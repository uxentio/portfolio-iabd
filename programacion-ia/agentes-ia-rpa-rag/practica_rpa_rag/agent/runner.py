# Runner RPA con Playwright. RPAChain ejecuta una cadena de pasos
# desde un workflow JSON, con reintentos por PWTimeout, log a archivo
# y captura de pantalla en cada error.
from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from playwright.sync_api import (
    Page,
    TimeoutError as PWTimeout,
    sync_playwright,
)


# --- logging a archivo y consola ---
ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "data" / "rpa_ejecucion.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("RPARunner")


DEFAULT_TIMEOUT_MS = 10_000
MAX_INTENTOS_POR_STEP = 3   # 1 intento + 2 reintentos
ESPERA_REINTENTO_S = 1.5

# RPA_VIEW_DELAY_MS controla el cierre del navegador en visible:
# "keep"/sin definir -> espera Enter; nº ms -> espera ese tiempo; "0" -> cierra ya.

# Pausa entre acciones de Playwright en visible (slow_mo). Headless = 0.
DEFAULT_SLOW_MO_MS = 400


def _flag_env(nombre: str) -> bool:
    """Lee un flag estilo bool desde env var. Acepta 1/true/yes/on (case-insensitive)."""
    val = os.getenv(nombre, "").strip().lower()
    return val in ("1", "true", "yes", "on")


# --- función de reintentos ---
def con_reintentos(
    func: Callable[[], Any],
    max_intentos: int = MAX_INTENTOS_POR_STEP,
    espera: float = ESPERA_REINTENTO_S,
    nombre: str = "acción",
):
    """Reintenta ante PWTimeout (transitorio: elemento aún sin pintar).
    Otros errores se propagan."""
    for intento in range(1, max_intentos + 1):
        try:
            return func()
        except PWTimeout as e:
            if intento < max_intentos:
                logger.warning(
                    f"  reintento {intento}/{max_intentos} en '{nombre}': "
                    f"{type(e).__name__}"
                )
                time.sleep(espera)
            else:
                logger.error(f"  agotados {max_intentos} intentos en '{nombre}'")
                raise


# --- RPAChain: cadena de pasos ---
class RPAChain:
    """Ejecuta una secuencia de pasos compartiendo un dict ctx (con `page`).
    Si un paso falla, captura pantalla y devuelve ok=False sin seguir."""

    def __init__(self, nombre: str = "RPA"):
        self.nombre = nombre
        self.steps: list[tuple[str, Callable[[dict], Any]]] = []
        self.context: dict[str, Any] = {}

    def add_step(self, nombre: str, func: Callable[[dict], Any]) -> "RPAChain":
        self.steps.append((nombre, func))
        return self

    def run(self) -> dict[str, Any]:
        """Ejecuta los pasos en orden. Devuelve resumen estructurado."""
        logger.info("=" * 50)
        logger.info(f"INICIO: {self.nombre}")
        logger.info(f"Pasos programados: {len(self.steps)}")
        logger.info("=" * 50)

        t0 = time.monotonic()
        pasos_ok = 0
        screenshot_error: str | None = None

        for i, (nombre, func) in enumerate(self.steps, 1):
            logger.info(f"[{i}/{len(self.steps)}] {nombre}")
            try:
                func(self.context)
                pasos_ok += 1
            except Exception as e:
                logger.error(
                    f"[{i}/{len(self.steps)}] ERROR en {nombre}: "
                    f"{type(e).__name__}: {e}"
                )
                page: Page | None = self.context.get("page")
                if page is not None:
                    screenshot_error = self._captura_pantalla(page, i, nombre)
                duracion = round(time.monotonic() - t0, 2)
                return {
                    "ok": False,
                    "duration_s": duracion,
                    "steps_executed": pasos_ok,
                    "last_toast_text": self.context.get("last_toast"),
                    "extracted": self.context.get("extracted", {}),
                    "error": f"{type(e).__name__}: {e}",
                    "screenshot": screenshot_error,
                }

        duracion = round(time.monotonic() - t0, 2)
        logger.info("=" * 50)
        logger.info(f"FIN: {self.nombre} OK ({pasos_ok}/{len(self.steps)} pasos, {duracion}s)")
        logger.info("=" * 50)

        return {
            "ok": True,
            "duration_s": duracion,
            "steps_executed": pasos_ok,
            "last_toast_text": self.context.get("last_toast"),
            "extracted": self.context.get("extracted", {}),
            "error": None,
            "screenshot": None,
        }

    def _captura_pantalla(self, page: Page, paso_num: int, paso_nombre: str) -> str | None:
        """Captura PNG en cada error en data/screenshots/."""
        try:
            carpeta = ROOT / "data" / "screenshots"
            carpeta.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            etiqueta = paso_nombre.replace(" ", "_").replace("'", "")
            ruta = carpeta / f"{ts}_paso{paso_num}_{etiqueta}.png"
            page.screenshot(path=str(ruta))
            logger.error(f"  captura guardada en {ruta}")
            return str(ruta)
        except Exception as e:
            logger.warning(f"  no pude guardar la captura: {e}")
            return None


# --- builders de pasos: cada step del JSON pasa a una función ctx->... ---
def _sel(target: dict) -> str:
    """Traduce un target {by, value} al selector de Playwright."""
    by = target.get("by", "css")
    value = target["value"]
    if by == "css":
        return value
    if by == "id":
        return f"#{value}"
    if by == "name":
        return f'[name="{value}"]'
    if by == "xpath":
        return f"xpath={value}"
    raise ValueError(f"Selector 'by' no soportado: {by}")


def _step_wait(step: dict):
    ms = int(step.get("ms", 500))
    def fn(ctx: dict):
        ctx["page"].wait_for_timeout(ms)
    return fn


def _step_click(step: dict):
    sel = _sel(step["target"])
    def fn(ctx: dict):
        page: Page = ctx["page"]
        con_reintentos(lambda: page.click(sel), nombre=f"click {sel}")
    return fn


def _step_type(step: dict):
    sel = _sel(step["target"])
    value = str(step["value"])
    def fn(ctx: dict):
        page: Page = ctx["page"]
        con_reintentos(lambda: page.fill(sel, value), nombre=f"type {sel}")
    return fn


def _step_select(step: dict):
    sel = _sel(step["target"])
    value = str(step["value"])
    def fn(ctx: dict):
        page: Page = ctx["page"]
        con_reintentos(
            lambda: page.select_option(sel, value),
            nombre=f"select {sel}",
        )
    return fn


def _step_wait_for_text(step: dict):
    sel = _sel(step["target"])
    needle = step["contains"]
    def fn(ctx: dict):
        page: Page = ctx["page"]
        con_reintentos(
            lambda: page.wait_for_function(
                """([s, t]) => {
                    const el = document.querySelector(s);
                    return el && el.textContent && el.textContent.includes(t);
                }""",
                arg=[sel, needle],
            ),
            nombre=f"wait_for_text '{needle}'",
        )
        # Guardo el texto final para el resumen.
        try:
            ctx["last_toast"] = page.text_content(sel) or needle
        except Exception:
            ctx["last_toast"] = needle
    return fn


def _step_read_text(step: dict):
    """Lee el textContent de un selector y lo guarda en ctx[save_as].
    Sirve para capturar valores que el form muestra al usuario tras una
    acción (p. ej. el id `L-NNNN` que aparece en el toast tras un alta).
    El resumen final del workflow incluye `extracted` con todos los
    campos que cualquier read_text haya guardado."""
    sel = _sel(step["target"])
    nombre = step.get("save_as", "extracted_text")
    pattern = step.get("pattern")  # opcional, regex para extraer un sub-string
    def fn(ctx: dict):
        page: Page = ctx["page"]
        try:
            texto = page.text_content(sel) or ""
        except Exception:
            texto = ""
        valor = texto.strip()
        if pattern:
            import re as _re
            m = _re.search(pattern, valor)
            if m:
                # Si el regex tiene grupo, devuelvo el grupo 1; si no, todo el match.
                valor = m.group(1) if m.groups() else m.group(0)
        ctx.setdefault("extracted", {})[nombre] = valor
    return fn


_BUILDERS: dict[str, Callable[[dict], Callable[[dict], Any]]] = {
    "wait":          _step_wait,
    "click":         _step_click,
    "type":          _step_type,
    "select":        _step_select,
    "wait_for_text": _step_wait_for_text,
    "read_text":     _step_read_text,
}


# --- entrada pública: la usa la tool run_workflow ---
def run_workflow(
    workflow: dict,
    headless: bool = False,   # visible por defecto: la demo es el caso principal
    timeout_ms: int = DEFAULT_TIMEOUT_MS,
) -> dict[str, Any]:
    """Ejecuta un workflow ya renderizado y devuelve un resumen.
    Nunca lanza: ante cualquier fallo devuelve dict con ok=False."""
    url = workflow.get("url")
    wf_id = workflow.get("id", "?")

    if not url or "{{" in str(url):
        return {
            "ok": False,
            "duration_s": 0.0,
            "steps_executed": 0,
            "last_toast_text": None,
            "error": f"URL sin renderizar: {url!r}",
            "screenshot": None,
        }

    chain = RPAChain(nombre=f"workflow {wf_id}")

    # slow_mo: ralentiza cada acción en visible para que se vea la demo.
    raw_sm = os.getenv("RPA_SLOW_MO_MS", "").strip()
    if raw_sm.isdigit():
        slow_mo_ms = int(raw_sm)
    elif headless:
        slow_mo_ms = 0
    else:
        slow_mo_ms = DEFAULT_SLOW_MO_MS

    # --- pasos de gestión del navegador ---
    pw_holder: dict = {}

    # Flags de grabación opt-in vía env vars.
    # RPA_TRACE_ON_ERROR=1 → arranca tracing y guarda zip solo si la cadena falla.
    # RPA_RECORD_VIDEO=1   → graba vídeo .webm de toda la sesión.
    trace_on_error = _flag_env("RPA_TRACE_ON_ERROR")
    record_video = _flag_env("RPA_RECORD_VIDEO")

    def paso_abrir_navegador(ctx: dict):
        pw = sync_playwright().start()
        pw_holder["pw"] = pw
        browser = pw.chromium.launch(headless=headless, slow_mo=slow_mo_ms)

        # Vídeo: necesita pasar record_video_dir al crear el BrowserContext.
        # El archivo .webm se finaliza al hacer context.close().
        context_kwargs: dict = {}
        if record_video:
            videos_dir = ROOT / "data" / "videos"
            videos_dir.mkdir(parents=True, exist_ok=True)
            context_kwargs["record_video_dir"] = str(videos_dir)
            logger.info(f"  RPA_RECORD_VIDEO=1: vídeo -> {videos_dir}")

        browser_context = browser.new_context(**context_kwargs)

        # Tracing: arranca aquí siempre que el flag esté activo. Sin path al
        # parar -> se descarta. Con path -> se guarda. Solo se llama tracing.stop()
        # con path en el cleanup si hubo error en algún paso del workflow.
        if trace_on_error:
            browser_context.tracing.start(
                screenshots=True, snapshots=True, sources=True
            )
            logger.info("  RPA_TRACE_ON_ERROR=1: tracing activo (se guarda solo si falla)")

        page = browser_context.new_page()
        page.set_default_timeout(timeout_ms)
        page.goto(url)
        ctx["browser"] = browser
        ctx["browser_context"] = browser_context
        ctx["page"] = page

    def paso_cerrar_navegador(ctx: dict):
        try:
            if not headless and "page" in ctx:
                raw = os.getenv("RPA_VIEW_DELAY_MS", "").strip().lower()
                if raw.isdigit():
                    ms = int(raw)
                    if ms > 0:
                        ctx["page"].wait_for_timeout(ms)
                elif sys.stdin is not None and sys.stdin.isatty():
                    # consola interactiva (CLI): espero Enter para inspeccionar.
                    try:
                        input("[RPA] Navegador abierto. Pulsa Enter para cerrarlo... ")
                    except EOFError:
                        ctx["page"].wait_for_timeout(10_000)
                else:
                    # entornos no interactivos (uvicorn, IDE, scripts): espero
                    # 10 segundos y cierro sin bloquear el flujo.
                    ctx["page"].wait_for_timeout(10_000)

            # Cierre del tracing antes que del context (Playwright lo exige).
            browser_context = ctx.get("browser_context")
            had_error = bool(ctx.get("had_error"))
            if browser_context is not None and trace_on_error:
                try:
                    if had_error:
                        traces_dir = ROOT / "data" / "traces"
                        traces_dir.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        trace_path = traces_dir / f"{ts}_trace.zip"
                        browser_context.tracing.stop(path=str(trace_path))
                        logger.error(f"  trace guardado en {trace_path}")
                        logger.error(f"  visualizalo con: playwright show-trace {trace_path}")
                    else:
                        # cadena ok -> tracing se descarta, no inflo el disco.
                        browser_context.tracing.stop()
                except Exception as e:
                    logger.warning(f"  no pude cerrar tracing: {e}")

            # Cerrar context (finaliza el vídeo si lo había) y luego browser.
            if browser_context is not None:
                try:
                    page = ctx.get("page")
                    video_path = None
                    if record_video and page is not None:
                        try:
                            # page.video.path() solo es válido tras context.close().
                            # Lo capturo antes para loguearlo cuando se cierre.
                            video_path = page.video.path() if page.video else None
                        except Exception:
                            video_path = None
                    browser_context.close()
                    if record_video and video_path:
                        logger.info(f"  vídeo guardado en {video_path}")
                except Exception:
                    pass
            browser = ctx.get("browser")
            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass
        finally:
            pw = pw_holder.get("pw")
            if pw is not None:
                pw.stop()

    chain.add_step("Abrir navegador y navegar a la URL", paso_abrir_navegador)

    # --- pasos del workflow JSON ---
    for i, step in enumerate(workflow.get("steps", []), 1):
        stype = step["type"]
        if stype not in _BUILDERS:
            return {
                "ok": False,
                "duration_s": 0.0,
                "steps_executed": 0,
                "last_toast_text": None,
                "error": f"Tipo de step no soportado: {stype}",
                "screenshot": None,
            }
        chain.add_step(f"step {i}: {stype}", _BUILDERS[stype](step))

    chain.add_step("Cerrar navegador", paso_cerrar_navegador)

    # Lanzo la cadena. El cierre se intenta siempre (try/except + finally).
    resumen = chain.run()

    # Si la cadena cortó antes del paso "Cerrar navegador", marco el flag
    # de error en ctx para que el cierre guarde el trace y lo invoco.
    if resumen.get("ok") is False:
        chain.context["had_error"] = True
        try:
            paso_cerrar_navegador(chain.context)
        except Exception:
            pass

    return resumen
