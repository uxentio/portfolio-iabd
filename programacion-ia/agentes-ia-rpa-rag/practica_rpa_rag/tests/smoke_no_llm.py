# Smoke checks deterministas sin LM Studio: sintaxis, workflows,
# Pydantic, templating y RAG. Detecta regresiones rápido.
from __future__ import annotations

import json
import os
import py_compile
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# --- 1) sintaxis ---
def check_syntax() -> bool:
    print("[1] Comprobando sintaxis de todos los .py")
    fail = 0
    for sub in ("agent", "rag", "shared", "web_form"):
        d = ROOT / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.py")):
            try:
                py_compile.compile(str(f), doraise=True)
                print(f"    OK   {sub}/{f.name}")
            except py_compile.PyCompileError as e:
                print(f"    FAIL {sub}/{f.name}: {e}")
                fail += 1
    return fail == 0


# --- 2) carga de workflows ---
def check_workflows() -> bool:
    print("[2] Comprobando workflows en procedures/")
    from shared.procedures import iter_workflows, load_workflow
    expected_keys = {"id", "titulo", "descripcion", "app", "url", "tags", "param_schema", "steps"}
    ok = True
    for wf in iter_workflows():
        missing = expected_keys - set(wf.keys())
        if missing:
            print(f"    FAIL {wf.get('id')}: faltan campos {missing}")
            ok = False
        else:
            print(f"    OK   {wf['id']}  ({len(wf['steps'])} steps)")
    if not iter_workflows():
        print("    FAIL no hay workflows en procedures/")
        ok = False
    # smoke load_workflow
    sample = iter_workflows()[0]["id"]
    if load_workflow(sample) is None:
        print(f"    FAIL load_workflow('{sample}') devolvió None")
        ok = False
    return ok


# --- 3) Pydantic ---
def check_pydantic() -> bool:
    print("[3] Comprobando validación Pydantic dinámica")
    from shared.models import build_model_from_schema, validate_params
    schema = {
        "titulo":       {"type": "string",  "required": True},
        "autor":        {"type": "string",  "required": True},
        "copias_total": {"type": "integer", "required": True},
        "categoria":    {"type": "enum",    "values": ["novela", "ensayo", "poesia"], "required": True},
    }
    Model = build_model_from_schema(schema)
    if "titulo" not in Model.model_fields:
        print("    FAIL Pydantic no construyó el campo titulo")
        return False
    valid = validate_params(schema, {"titulo": "X", "autor": "Y", "copias_total": 3, "categoria": "novela"})
    if valid != {"titulo": "X", "autor": "Y", "copias_total": 3, "categoria": "novela"}:
        print(f"    FAIL validate_params devolvió {valid}")
        return False
    # caso negativo: un enum inválido debe lanzar ValidationError
    try:
        validate_params(schema, {"titulo": "X", "autor": "Y", "copias_total": 3, "categoria": "lo_que_sea"})
        print("    FAIL Pydantic aceptó un enum inválido")
        return False
    except Exception:
        pass
    print("    OK   tipos correctos y enum rechazado")
    return True


# --- 4) templating ---
def check_templating() -> bool:
    print("[4] Comprobando templating de placeholders")
    from shared.templating import render_workflow
    from shared.procedures import load_workflow
    wf = load_workflow("alta_libro")
    if wf is None:
        print("    FAIL no encuentro alta_libro")
        return False
    rendered = render_workflow(wf, {
        "FORM_URL": "http://localhost:8080/index.html",
        "titulo": "Cien años de soledad",
        "autor": "García Márquez, Gabriel",
        "editorial": "Cátedra",
        "anio": 1967,
        "isbn": "978-84-376-0494-7",
        "paginas": 471,
        "idioma": "es",
        "categoria": "novela",
        "copias_total": 3,
    })
    if "{{" in json.dumps(rendered, ensure_ascii=False):
        print("    FAIL quedan placeholders sin sustituir")
        return False
    print(f"    OK   url = {rendered['url']}")
    return True


# --- 5) RAG (indexa y prueba 5 queries) ---
def check_rag() -> bool:
    print("[5] Comprobando RAG (indexa los workflows y prueba 5 queries)")
    chroma = ROOT / "rag" / ".chroma"
    if chroma.exists():
        shutil.rmtree(chroma)
    import importlib
    from rag import index_procedures
    importlib.reload(index_procedures)
    index_procedures.main()

    from rag.search_procedures import search

    # Para cada query, lista de workflows aceptables. El dominio es biblioteca
    # regional con préstamos, sin precio. Los workflows oficiales son:
    # alta_libro, baja_libro, ajuste_copias, prestamo_libro,
    # devolucion_libro, encargo_libro.
    pruebas = [
        ("Da de alta el libro Cien años de soledad de García Márquez con 3 ejemplares",
            ["alta_libro"]),
        ("Registra en el fondo este libro nuevo",
            ["alta_libro"]),
        ("Retira del fondo el R-0007 que se ha perdido",
            ["baja_libro"]),
        ("Expurga el R-0003 por deterioro",
            ["baja_libro"]),
        ("Presta el R-0003 al socio S-0042 durante 14 días",
            ["prestamo_libro"]),
        ("Apunta el préstamo del libro X al lector Y",
            ["prestamo_libro"]),
        ("El socio S-0042 devuelve el R-0003",
            ["devolucion_libro"]),
        ("Cierra el préstamo P-0007",
            ["devolucion_libro"]),
        ("Añade 2 copias más al título R-0003",
            ["ajuste_copias"]),
        ("Pon 5 ejemplares del libro R-0042",
            ["ajuste_copias"]),
        ("encárgame un libro en formato tapa dura a la tienda externa",
            ["encargo_libro"]),
    ]
    ok = 0
    for q, esperados in pruebas:
        hits = search(q, k=3)
        top = hits[0]["id"] if hits else None
        mark = "OK  " if top in esperados else "FAIL"
        if top in esperados:
            ok += 1
        print(f"    [{mark}] {q[:55]:55}  ->  {top}  (esperados: {esperados})")
    print(f"    Aciertos top-1: {ok}/{len(pruebas)}")
    # Umbral 7/11: con MiniLM y queries vagas alguna cae en un vecino.
    return ok >= 7


# --- runner ---
def main() -> int:
    os.chdir(ROOT)
    checks = [
        ("sintaxis",    check_syntax),
        ("workflows",   check_workflows),
        ("pydantic",    check_pydantic),
        ("templating",  check_templating),
        ("rag",         check_rag),
    ]
    results = []
    for name, fn in checks:
        try:
            ok = fn()
        except Exception as e:
            print(f"    EXCEPTION en {name}: {e}")
            ok = False
        results.append((name, ok))
        print()

    print("-" * 60)
    print("Resumen:")
    for name, ok in results:
        print(f"   {name:12}  {'OK' if ok else 'FAIL'}")
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
