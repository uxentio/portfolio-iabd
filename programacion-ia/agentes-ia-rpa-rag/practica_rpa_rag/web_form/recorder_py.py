"""Recorder Python con vista propia (Chromium controlado por Playwright).

Levanta una ventana de Chromium aparte del navegador del sistema, inyecta
un script que registra `click`/`input`/`change` con selectores estables y,
al cerrar, exporta un `.workflow.json` con el mismo DSL que consume el
runner del agente. Pensado para grabar contra páginas externas (Google
Forms, httpbin, paneles de admin) donde no se puede inyectar el panel JS
embebido del proyecto.

Uso típico (grabar el formulario de httpbin con placeholders):

    python web_form/recorder_py.py \\
        https://httpbin.org/forms/post \\
        encargo_libro_v2 \\
        --titulo "Encargo de libro (httpbin) v2" \\
        --app httpbin_forms \\
        --placeholders custname,custtel,custemail,size,delivery,comments \\
        --tag encargo --tag externo

Comportamiento:
  1. Abre Chromium en `--url`. El usuario interactúa con la página: rellena
     campos, selecciona opciones, pulsa botones.
  2. Cada acción queda registrada en `window.__pyRec.steps` en el navegador.
     Los inputs cuyo `name`/`id` aparezca en `--placeholders` se exportan
     como `{{name}}` (placeholders del workflow); el resto guarda el valor
     literal tecleado.
  3. Cuando termines, vuelve a la consola y pulsa Enter (o cierra la
     ventana de Chromium): el script lee los pasos, monta la estructura
     del workflow JSON y lo escribe en `procedures/<id>.workflow.json`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent.parent
PROCEDURES_DIR = ROOT / "procedures"


# Script que se inyecta en la página antes de cualquier navegación. Mismo
# patrón de captura que el recorder JS embebido (capture=true para no
# perder eventos cuyo handler de la página haga stopPropagation).
_RECORDER_JS = r"""
(() => {
  if (window.__pyRec) return;  // idempotente: solo una vez por contexto.
  window.__pyRec = { steps: [], placeholders: __PLACEHOLDERS_JSON__ };

  function _selector(el) {
    if (el.id)   return '#' + el.id;
    if (el.name) return '[name="' + el.name + '"]';
    return el.tagName.toLowerCase();
  }

  // Si el name/id está en la lista que pasó el CLI, sustituyo el valor
  // tecleado por {{name}} para que el workflow sea reutilizable.
  function _valueOrPlaceholder(el) {
    const key = el.name || el.id;
    if (key && window.__pyRec.placeholders.includes(key)) {
      return '{{' + key + '}}';
    }
    return el.value ?? '';
  }

  document.addEventListener('click', (e) => {
    const tag = e.target.tagName;
    // Inputs/select/textarea ya disparan input/change; aquí solo clicks puros.
    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
    window.__pyRec.steps.push({
      type: 'click',
      target: { by: 'css', value: _selector(e.target) },
    });
  }, true);

  document.addEventListener('input', (e) => {
    const tag = e.target.tagName;
    if (tag !== 'INPUT' && tag !== 'TEXTAREA') return;
    const sel = _selector(e.target);
    const val = _valueOrPlaceholder(e.target);
    // Dedupe: si el usuario corrige varias veces el mismo input me quedo
    // solo con el último valor.
    window.__pyRec.steps = window.__pyRec.steps.filter(
      (s) => !(s.type === 'type' && s.target.value === sel)
    );
    window.__pyRec.steps.push({
      type: 'type',
      target: { by: 'css', value: sel },
      value: val,
    });
  }, true);

  document.addEventListener('change', (e) => {
    if (e.target.tagName !== 'SELECT') return;
    window.__pyRec.steps.push({
      type: 'select',
      target: { by: 'css', value: _selector(e.target) },
      value: _valueOrPlaceholder(e.target),
    });
  }, true);

  // Banner discreto arriba a la derecha para que el usuario sepa que está
  // grabando. No interfiere con eventos del formulario.
  const banner = document.createElement('div');
  banner.id = '__pyrec_banner';
  banner.textContent = '● recorder_py';
  Object.assign(banner.style, {
    position: 'fixed', top: '8px', right: '8px', zIndex: 2147483647,
    background: '#dc2626', color: '#fff', font: '600 12px system-ui',
    padding: '4px 10px', borderRadius: '999px', boxShadow: '0 2px 6px rgba(0,0,0,.35)',
    pointerEvents: 'none',
  });
  document.documentElement.appendChild(banner);
})();
"""


def _construir_param_schema(placeholders: list[str]) -> dict:
    """Param_schema básico con todos los placeholders como string requerido.
    El alumno puede afinarlo a mano (enum, número, opcional...) tras grabar."""
    return {
        nombre: {"type": "string", "required": True}
        for nombre in placeholders
    }


def grabar_workflow(
    url: str,
    workflow_id: str,
    titulo: str | None,
    descripcion: str | None,
    app: str,
    tags: list[str],
    placeholders: list[str],
    out_dir: Path,
) -> Path:
    """Levanta Chromium, registra acciones y devuelve la ruta del JSON."""
    js_inyectado = _RECORDER_JS.replace(
        "__PLACEHOLDERS_JSON__", json.dumps(placeholders)
    )

    print(f"[recorder_py] abriendo {url}")
    print(f"[recorder_py] placeholders activos: {placeholders or '(ninguno)'}")
    print("[recorder_py] interactúa con la página. Cuando termines:")
    print("[recorder_py]   - vuelve a esta consola y pulsa Enter, o")
    print("[recorder_py]   - cierra la ventana del Chromium")
    print()

    steps: list[dict] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=20)
        context = browser.new_context(
            viewport={"width": 1280, "height": 820},
        )
        context.add_init_script(js_inyectado)
        page = context.new_page()
        page.goto(url)

        # Espero a que el usuario pulse Enter en la consola, o a que cierre
        # la ventana. Si cierra la ventana antes, el page.evaluate falla y
        # caigo al except, recuperando lo que hay grabado hasta ese punto.
        try:
            input("[recorder_py] (Enter para detener y guardar) ")
        except (KeyboardInterrupt, EOFError):
            print()

        try:
            steps = page.evaluate("window.__pyRec ? window.__pyRec.steps : []")
        except Exception as e:
            print(f"[recorder_py] aviso: no pude leer pasos del navegador ({e}).")
            print("[recorder_py] probablemente cerraste la ventana antes. Sin pasos que guardar.")
            steps = []
        finally:
            try:
                browser.close()
            except Exception:
                pass

    if not steps:
        print("[recorder_py] no hay pasos que guardar. Saliendo sin escribir.")
        sys.exit(1)

    # Estructura final del workflow. Mismo orden que el recorder JS:
    # wait inicial + pasos del usuario.
    workflow = {
        "id": workflow_id,
        "titulo": titulo or workflow_id.replace("_", " ").capitalize(),
        "descripcion": descripcion or (
            f"Workflow grabado con recorder_py contra {url}. "
            "Ajusta param_schema, tags y descripcion antes de indexar."
        ),
        "app": app,
        "url": url,
        "tags": tags,
        "param_schema": _construir_param_schema(placeholders),
        "steps": [{"type": "wait", "ms": 500}, *steps],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{workflow_id}.workflow.json"
    out_path.write_text(
        json.dumps(workflow, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[recorder_py] {len(steps)} pasos -> {out_path}")
    print("[recorder_py] siguiente paso: revisa el JSON, ajusta param_schema/tags")
    print("[recorder_py] y reindexa el RAG con: python rag/index_procedures.py")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Graba un workflow contra cualquier URL usando Playwright.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "EJEMPLOS\n"
            "  # Grabar contra el formulario de httpbin (5 campos):\n"
            "  python web_form/recorder_py.py https://httpbin.org/forms/post encargo_v2 \\\n"
            "      --placeholders custname,custtel,custemail,size,comments\n\n"
            "  # Grabar contra el formulario local de alta de libro:\n"
            "  python web_form/recorder_py.py http://localhost:8080/index.html alta_libro_v2 \\\n"
            "      --placeholders titulo,autor,editorial,anio,isbn,paginas,categoria,copias_total\n"
        ),
    )
    parser.add_argument("url", help="URL contra la que grabar (puede ser externa).")
    parser.add_argument("id", help="Id del workflow (será el nombre del archivo).")
    parser.add_argument("--titulo", default=None, help="Título humano del workflow.")
    parser.add_argument("--descripcion", default=None, help="Descripción para el RAG.")
    parser.add_argument("--app", default="external", help="Etiqueta de la 'app' (default: external).")
    parser.add_argument(
        "--placeholders", default="",
        help="Lista separada por comas con los name/id de los inputs que deben "
             "exportarse como {{placeholder}} (los demás guardarán el valor literal).",
    )
    parser.add_argument(
        "--tag", action="append", default=[], dest="tags",
        help="Tag para el RAG (repetible: --tag externo --tag encargo).",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=PROCEDURES_DIR,
        help=f"Carpeta donde escribir el .workflow.json (default: {PROCEDURES_DIR}).",
    )
    args = parser.parse_args(argv)

    placeholders = [p.strip() for p in args.placeholders.split(",") if p.strip()]
    grabar_workflow(
        url=args.url,
        workflow_id=args.id,
        titulo=args.titulo,
        descripcion=args.descripcion,
        app=args.app,
        tags=args.tags,
        placeholders=placeholders,
        out_dir=args.out_dir,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
