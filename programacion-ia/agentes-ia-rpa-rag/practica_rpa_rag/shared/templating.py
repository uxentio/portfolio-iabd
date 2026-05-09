"""Sustitución de placeholders {{nombre}} en workflows JSON.
Recorre el JSON recursivamente. Si una cadena es solo el placeholder, se
respeta el tipo (int/float); si está embebido, se interpola como texto."""
from __future__ import annotations

import copy
import re
from typing import Any, Dict

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def _render_string(text: str, params: Dict[str, Any]) -> Any:
    # Caso 1: la cadena es exactamente un único placeholder -> respeto tipo
    m = re.fullmatch(r"\s*\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}\s*", text)
    if m:
        key = m.group(1)
        if key not in params:
            raise KeyError(f"Parámetro faltante en templating: '{key}'")
        return params[key]

    # Caso 2: interpolación dentro de una cadena
    def _sub(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in params:
            raise KeyError(f"Parámetro faltante en templating: '{key}'")
        return str(params[key])

    return _PLACEHOLDER_RE.sub(_sub, text)


def render_workflow(workflow: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Devuelve una copia del workflow con todos los placeholders sustituidos."""
    wf = copy.deepcopy(workflow)

    def walk(node: Any) -> Any:
        if isinstance(node, str):
            return _render_string(node, params)
        if isinstance(node, list):
            return [walk(x) for x in node]
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        return node

    return walk(wf)
