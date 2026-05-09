# Carga de workflows desde procedures/. Punto único para tools, RAG y tests.
# Cacheo el contenido entero (lru_cache) porque se toca varias veces por turno.
from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCEDURES_DIR = ROOT / "procedures"


@lru_cache(maxsize=1)
def _load_all() -> tuple[dict, ...]:
    """Lee todos los *.workflow.json una sola vez. Devuelve tupla (lru_cache
    necesita hashable); los consumidores reciben deepcopy."""
    out = []
    for path in sorted(PROCEDURES_DIR.glob("*.workflow.json")):
        with path.open("r", encoding="utf-8") as f:
            out.append(json.load(f))
    return tuple(out)


def load_workflow(workflow_id: str) -> dict | None:
    """Carga el workflow con ese id. None si no existe."""
    for wf in _load_all():
        if wf.get("id") == workflow_id:
            return copy.deepcopy(wf)
    return None


def iter_workflows() -> list[dict]:
    """Todos los workflows del directorio."""
    return [copy.deepcopy(wf) for wf in _load_all()]


def clear_cache() -> None:
    """Invalida la caché. Útil tras grabar un workflow nuevo en runtime."""
    _load_all.cache_clear()
