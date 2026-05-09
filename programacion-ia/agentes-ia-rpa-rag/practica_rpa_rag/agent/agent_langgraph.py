# Backend LangGraph del agente.
# StateGraph propio con 4 nodos: agente, tools_seguras, confirmar_rpa,
# ejecutar_rpa. El HITL es un nodo del grafo, no un middleware.
from __future__ import annotations

import contextvars
import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402

from agent.tools import (  # noqa: E402
    ALL_TOOLS,
    search_procedures,
    list_procedures,
    extract_parameters,
    consultar_libreria_externa,
    listar_catalogo,
    listar_prestamos,
    buscar_libro,
    run_workflow,
)
from shared.events import AgentEventType  # noqa: E402
from shared.load_model import get_llm  # noqa: E402
from shared.prompts import AGENT_SYSTEM_PROMPT  # noqa: E402
from shared.ui_bus import bus as _ui_bus  # noqa: E402


# --- Middleware ---
# LangGraph no trae middleware nativo: cada nodo se envuelve con
# _with_middleware para correr hooks before/after.
class LGMiddleware:
    """Base para middlewares de nodo en LangGraph."""

    def before_node(self, state: dict, name: str) -> None:
        return None

    def after_node(self, state: dict, name: str) -> None:
        return None


def _with_middleware(node_fn, name: str, middlewares: list):
    """Envuelve un nodo con los hooks before/after."""
    if not middlewares:
        return node_fn

    def wrapped(state):
        for m in middlewares:
            try:
                m.before_node(state, name)
            except Exception as e:
                # Si un middleware lanza, no propago la excepción al grafo.
                print(
                    f"[middleware {type(m).__name__}.before_node] error: {e}",
                    file=sys.stderr,
                )
        result = node_fn(state)
        # Vista del estado tras el nodo (simulo el merge de add_messages).
        merged_messages = list(state.get("messages", []))
        for m_msg in (result or {}).get("messages", []):
            merged_messages.append(m_msg)
        merged_state = {**state, "messages": merged_messages}
        for m in middlewares:
            try:
                m.after_node(merged_state, name)
            except Exception as e:
                print(
                    f"[middleware {type(m).__name__}.after_node] error: {e}",
                    file=sys.stderr,
                )
        return result

    return wrapped


# ContextVar (no global) para soportar peticiones concurrentes con su thread_id.
current_thread_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_thread_id", default="default"
)


class UIFeedbackLGMiddleware(LGMiddleware):
    """Publica eventos en el UI bus desde los nodos del grafo."""

    def after_node(self, state: dict, name: str) -> None:
        msgs = state.get("messages") or []
        if not msgs:
            return
        last = msgs[-1]
        thread = current_thread_id.get()

        if isinstance(last, AIMessage):
            tool_calls = getattr(last, "tool_calls", None) or []
            for tc in tool_calls:
                _ui_bus.publish(thread, {
                    "type": AgentEventType.TOOL_CALL,
                    "name": tc["name"],
                    "args": tc.get("args", {}),
                })
            if not tool_calls:
                content = (last.content or "").strip()
                if content:
                    _ui_bus.publish(thread, {"type": AgentEventType.ANSWER, "content": content})

        elif isinstance(last, ToolMessage):
            _ui_bus.publish(thread, {
                "type": AgentEventType.TOOL_RESULT,
                "name": last.name,
                "content": str(last.content or ""),
            })


# --- Estado del grafo ---
class AgentState(TypedDict):
    """Estado entre nodos. add_messages concatena los mensajes nuevos."""
    messages: Annotated[list[BaseMessage], add_messages]


# Límite de mensajes recientes que viajan al LLM en cada turno. Sin esto
# el contexto crece sin límite y cada turno paga más prompt eval. Con 12
# (~3 turnos completos de tool_call + tool_result + response) el LLM
# tiene memoria suficiente para encadenar la cadena actual sin arrastrar
# turnos antiguos que confunden al modelo y disparan los tokens.
MAX_HISTORIAL_MENSAJES = 12


def _recortar_historial(msgs: list[BaseMessage]) -> list[BaseMessage]:
    """Mantiene el SystemMessage inicial + los últimos N mensajes.
    Si el último mensaje recortado es un ToolMessage huérfano (sin su
    AIMessage previo con tool_call), avanza para no romper la coherencia
    que algunos modelos exigen."""
    if len(msgs) <= MAX_HISTORIAL_MENSAJES + 1:
        return list(msgs)
    sistema = msgs[0] if msgs and isinstance(msgs[0], SystemMessage) else None
    cola = list(msgs[-MAX_HISTORIAL_MENSAJES:])
    # Si la cola arranca con un ToolMessage, tira el primer elemento hasta
    # que arranque con HumanMessage o AIMessage (evita "tool result without
    # tool call" que algunos modelos rechazan).
    while cola and isinstance(cola[0], ToolMessage):
        cola.pop(0)
    return ([sistema] if sistema else []) + cola


# --- Nodos ---
# El nodo del agente es una factoría: build_agent_lg le pasa el LLM
# concreto (con o sin override de modelo) y devuelve la función que el
# StateGraph va a registrar como nodo. Así se puede compilar grafos
# con modelos distintos en runtime sin tocar estado global.
def _make_nodo_agente(llm_con_tools):
    def nodo_agente(state: AgentState) -> dict:
        """LLM principal: mira el historial y decide qué hacer."""
        msgs = state["messages"]
        if not msgs or not isinstance(msgs[0], SystemMessage):
            msgs = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + list(msgs)
        # Recorto el historial antes de invocar al LLM. Crítico para no
        # disparar el prompt eval en hardware modesto (CPU + GPU 2GB).
        msgs = _recortar_historial(msgs)
        respuesta = llm_con_tools.invoke(msgs)
        return {"messages": [respuesta]}
    return nodo_agente


# run_workflow va aparte (rama confirmar_rpa + ejecutar_rpa) para poder pausar.
# Aquí entran todas las tools idempotentes: lectura del RAG, listados,
# validación de parámetros y consultas externas. Si alguna falta, el LLM la
# invoca y el ToolNode no sabe ejecutarla → el agente queda en bucle.
_tools_seguras = ToolNode([
    search_procedures,
    list_procedures,
    extract_parameters,
    consultar_libreria_externa,
    listar_catalogo,
    listar_prestamos,
    buscar_libro,
])


def nodo_tools_seguras(state: AgentState) -> dict:
    return _tools_seguras.invoke(state)


def nodo_confirmar_rpa(state: AgentState) -> dict:
    """Nodo de pausa antes del RPA. El grafo se compila con
    interrupt_before=["confirmar_rpa"] y se pausa aquí."""
    return {"messages": []}


def nodo_ejecutar_rpa(state: AgentState) -> dict:
    """Ejecuta el RPA leyendo el último AIMessage con tool_calls."""
    msgs = state["messages"]
    last = msgs[-1] if msgs else None

    # Si lo último ya es una cancelación inyectada por la UI, no hago nada.
    if isinstance(last, ToolMessage):
        return {"messages": []}

    if not isinstance(last, AIMessage) or not getattr(last, "tool_calls", None):
        return {"messages": []}

    nuevos: list[BaseMessage] = []
    for tc in last.tool_calls:
        if tc["name"] != "run_workflow":
            continue
        try:
            resultado = run_workflow.invoke(tc.get("args", {}))
            nuevos.append(ToolMessage(
                content=str(resultado),
                tool_call_id=tc["id"],
                name="run_workflow",
            ))
        except Exception as e:
            nuevos.append(ToolMessage(
                content=f"Error ejecutando run_workflow: {e}",
                tool_call_id=tc["id"],
                name="run_workflow",
            ))
    return {"messages": nuevos}


# --- Edges condicionales ---
def router_agente(state: AgentState) -> Literal["tools_seguras", "confirmar_rpa", "__end__"]:
    """Tras el nodo agente, decide a dónde ir según los tool_calls."""
    last = state["messages"][-1]
    tool_calls = getattr(last, "tool_calls", None) or []
    if not tool_calls:
        return "__end__"

    nombres = {tc["name"] for tc in tool_calls}
    if "run_workflow" in nombres:
        return "confirmar_rpa"
    return "tools_seguras"


# --- Construcción del grafo ---
def build_agent_lg(
    *,
    checkpointer=None,
    hitl_before_run: bool = True,
    middlewares: list[LGMiddleware] | None = None,
    model: str | None = None,
):
    """Monta y compila el StateGraph.
    `hitl_before_run` activa interrupt_before en confirmar_rpa (CLI).
    `model` permite construir un grafo con un modelo distinto al del
    .env (lo usa la API cuando el cliente elige otro del Picker)."""
    middlewares = middlewares or []

    # LLM y nodo agente per-build. get_llm reusa la instancia perezosa
    # cuando no se pide modelo concreto, o construye una nueva si la API
    # cambió de modelo en runtime.
    llm_con_tools = get_llm(model).bind_tools(ALL_TOOLS)
    nodo_agente = _make_nodo_agente(llm_con_tools)

    builder = StateGraph(AgentState)

    # Cada nodo se envuelve con los hooks de los middlewares.
    builder.add_node("agente",        _with_middleware(nodo_agente,        "agente",        middlewares))
    builder.add_node("tools_seguras", _with_middleware(nodo_tools_seguras, "tools_seguras", middlewares))
    builder.add_node("confirmar_rpa", _with_middleware(nodo_confirmar_rpa, "confirmar_rpa", middlewares))
    builder.add_node("ejecutar_rpa",  _with_middleware(nodo_ejecutar_rpa,  "ejecutar_rpa",  middlewares))

    builder.add_edge(START, "agente")
    builder.add_conditional_edges(
        "agente",
        router_agente,
        {
            "tools_seguras": "tools_seguras",
            "confirmar_rpa": "confirmar_rpa",
            "__end__": END,
        },
    )
    builder.add_edge("tools_seguras", "agente")
    builder.add_edge("confirmar_rpa", "ejecutar_rpa")
    builder.add_edge("ejecutar_rpa", "agente")

    compile_kwargs: dict = {}
    if checkpointer is not None:
        compile_kwargs["checkpointer"] = checkpointer
    if hitl_before_run:
        # Pausa justo antes de confirmar_rpa: la UI/CLI decide si reanudar.
        compile_kwargs["interrupt_before"] = ["confirmar_rpa"]

    return builder.compile(**compile_kwargs)


# --- Helper API: corre el grafo publicando en el UI bus ---
async def stream_with_feedback(agent, message: str, thread_id: str) -> None:
    """Ejecuta un turno fijando el thread_id en el contextvar."""
    config = {"configurable": {"thread_id": thread_id}}
    token = current_thread_id.set(thread_id)
    try:
        async for _ in agent.astream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="values",
        ):
            pass
    finally:
        current_thread_id.reset(token)
        _ui_bus.close(thread_id)
