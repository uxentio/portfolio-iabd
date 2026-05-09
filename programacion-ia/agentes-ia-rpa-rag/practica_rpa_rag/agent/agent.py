# Versión LangChain del agente: create_agent (LangChain 1.x) con tres
# middlewares (logging, HITL, feedback al UI bus). La traducción a
# LangGraph con StateGraph propio vive en agent_langgraph.py.
from __future__ import annotations

import functools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import HumanMessage

from agent.tools import ALL_TOOLS  # noqa: E402
from shared.events import AgentEventType  # noqa: E402
from shared.load_model import get_llm  # noqa: E402
from shared.prompts import AGENT_SYSTEM_PROMPT  # noqa: E402
from shared.ui_bus import bus as _ui_bus  # noqa: E402


# Mismo límite que en agent_langgraph.py para que los dos backends se
# comporten igual respecto al historial. Recortar aquí evita que el
# prompt eval crezca sin control en hardware modesto.
MAX_HISTORIAL_MENSAJES = 12


class LimitHistoryMiddleware(AgentMiddleware):
    """Recorta el historial antes de cada invocación al LLM. Mantiene el
    SystemMessage inicial (si existe) más los últimos N mensajes. Si la
    cola arranca con un ToolMessage huérfano se descarta para no romper
    la coherencia tool_call/tool_result que algunos modelos exigen."""

    def before_model(self, state, runtime):
        from langchain_core.messages import SystemMessage as _SysMsg, ToolMessage as _ToolMsg
        msgs = state.get("messages", [])
        if len(msgs) <= MAX_HISTORIAL_MENSAJES + 1:
            return None
        sistema = msgs[0] if msgs and isinstance(msgs[0], _SysMsg) else None
        cola = list(msgs[-MAX_HISTORIAL_MENSAJES:])
        while cola and isinstance(cola[0], _ToolMsg):
            cola.pop(0)
        nuevo = ([sistema] if sistema else []) + cola
        # Mutar in-place el state para que create_agent vea la lista recortada.
        state["messages"] = nuevo
        return None


class LoggingMiddleware(AgentMiddleware):
    """Imprime por consola la tool que se va a llamar y su resultado."""

    def before_model(self, state, runtime):
        n = len(state["messages"])
        print(f"[agente] paso {n}: voy a llamar al LLM")
        return None

    def after_model(self, state, runtime):
        last = state["messages"][-1]
        tool_calls = getattr(last, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                args_preview = str(tc.get("args", {}))
                if len(args_preview) > 120:
                    args_preview = args_preview[:117] + "..."
                print(f"[tool-call] {tc['name']}({args_preview})")
        else:
            content = getattr(last, "content", "") or ""
            if content:
                print("[agente] respuesta final (sin más tools).")
        return None


class ConfirmRunWorkflowMiddleware(AgentMiddleware):
    """Pide confirmación por consola antes de ejecutar run_workflow (solo CLI)."""

    def before_tool(self, state, runtime):
        tool_name = getattr(runtime, "tool_name", None) or getattr(runtime, "name", None)
        tool_args = getattr(runtime, "tool_args", None) or getattr(runtime, "args", {}) or {}

        if tool_name != "run_workflow":
            return None

        print()
        print("  --- confirmación humana antes de ejecutar el RPA ---")
        print(f"  workflow_id : {tool_args.get('workflow_id')}")
        print(f"  params      : {tool_args.get('params')}")
        print(f"  headless    : {tool_args.get('headless', False)}")
        resp = input("  ¿Ejecutar? [s/N] ").strip().lower()
        print()

        if resp in {"s", "si", "sí", "y", "yes"}:
            return None  # sigue el flujo normal

        # Cancelado: devuelvo un resultado falso para que el agente lo cuente.
        return {
            "tool_output": {
                "ok": False,
                "cancelled_by_user": True,
                "error": "El usuario no confirmó la ejecución del workflow.",
            }
        }


class UIFeedbackMiddleware(AgentMiddleware):
    """Publica los eventos del agente en el UI bus para que la UI pinte en directo."""

    @staticmethod
    def _thread_id_from(runtime) -> str:
        try:
            return runtime.config["configurable"]["thread_id"]
        except Exception:
            return "default"

    def after_model(self, state, runtime):
        last = state["messages"][-1]
        thread = self._thread_id_from(runtime)
        for tc in getattr(last, "tool_calls", None) or []:
            _ui_bus.publish(thread, {
                "type": AgentEventType.TOOL_CALL,
                "name": tc["name"],
                "args": tc.get("args", {}),
            })
        # Respuesta final (sin tool_calls): también la publico.
        if not getattr(last, "tool_calls", None):
            content = getattr(last, "content", "") or ""
            if content:
                _ui_bus.publish(thread, {"type": AgentEventType.ANSWER, "content": content})
        return None

    def after_tool(self, state, runtime):
        last = state["messages"][-1]  # ToolMessage con el resultado
        name = getattr(last, "name", "?")
        content = getattr(last, "content", "") or ""
        thread = self._thread_id_from(runtime)
        _ui_bus.publish(thread, {"type": AgentEventType.TOOL_RESULT, "name": name, "content": str(content)})
        return None


@functools.cache
def _create_agent_signature():
    """Cache de la signature de create_agent. La versión de LangChain
    no cambia en caliente, así que evitamos reflejar la signature en
    cada build_agent (cada cambio de modelo reconstruye el agente)."""
    import inspect
    return inspect.signature(create_agent).parameters


def build_agent(
    *,
    checkpointer=None,
    hitl: bool = False,
    ui_feedback: bool = False,
    model: str | None = None,
):
    """Monta el agente. `hitl` añade confirmación previa a run_workflow (CLI);
    `ui_feedback` publica eventos en el UI bus (API). `model` permite
    sobreescribir el modelo del .env en runtime (lo usa la API cuando el
    cliente elige otro modelo del Picker rellenado con /v1/models)."""
    # Orden: LimitHistory primero para que recorte el state antes de que
    # los demás hooks lo vean.
    middlewares = [LimitHistoryMiddleware(), LoggingMiddleware()]
    if ui_feedback:
        middlewares.append(UIFeedbackMiddleware())
    if hitl:
        middlewares.append(ConfirmRunWorkflowMiddleware())

    # El kwarg para el system prompt cambia entre versiones de LangChain.
    sig = _create_agent_signature()
    kwargs: dict = {
        "model": get_llm(model),
        "tools": ALL_TOOLS,
        "checkpointer": checkpointer,
        "middleware": middlewares,
    }
    if "prompt" in sig:
        kwargs["prompt"] = AGENT_SYSTEM_PROMPT
    elif "system_prompt" in sig:
        kwargs["system_prompt"] = AGENT_SYSTEM_PROMPT
    elif "state_modifier" in sig:
        kwargs["state_modifier"] = AGENT_SYSTEM_PROMPT

    return create_agent(**kwargs)


async def stream_with_feedback(agent, message: str, thread_id: str) -> None:
    """Lanza el agente y cierra el bus al final para avisar al consumidor."""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        async for _ in agent.astream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="values",
        ):
            pass
    finally:
        _ui_bus.close(thread_id)
