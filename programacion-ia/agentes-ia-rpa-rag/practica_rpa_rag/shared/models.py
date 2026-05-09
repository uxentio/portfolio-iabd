"""Modelos Pydantic dinámicos para validar parámetros de workflows.
Construyen un modelo en runtime desde el param_schema del JSON."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, create_model


# --- Construcción dinámica desde el param_schema del workflow ---
_PY_TYPES = {
    "string": str,
    "str": str,
    "integer": int,
    "int": int,
    "float": float,
    "number": float,
    "boolean": bool,
    "bool": bool,
}


def build_model_from_schema(
    schema: dict[str, dict[str, Any]],
    model_name: str = "WorkflowParams",
) -> type[BaseModel]:
    """Crea en runtime un modelo Pydantic v2 a partir del param_schema."""
    fields: dict[str, tuple] = {}

    for name, spec in schema.items():
        tipo = spec.get("type", "string")
        required = spec.get("required", True)
        description = spec.get("description", "")

        if tipo == "enum":
            values = spec.get("values", [])
            enum_cls = Enum(  # type: ignore[misc]
                f"{name.capitalize()}Enum",
                {v: v for v in values},
                type=str,
            )
            py_type = enum_cls
        else:
            py_type = _PY_TYPES.get(tipo, str)

        default = ... if required else None
        fields[name] = (py_type, Field(default, description=description))

    return create_model(model_name, **fields)  # type: ignore[call-overload]


def validate_params(
    schema: dict[str, dict[str, Any]],
    data: dict[str, Any],
) -> dict[str, Any]:
    """Valida `data` contra el `param_schema` y devuelve un dict serializable.
    mode="json" convierte Enums a su .value (lo que el templating necesita)."""
    Model = build_model_from_schema(schema)
    obj = Model(**data)
    return obj.model_dump(mode="json")
