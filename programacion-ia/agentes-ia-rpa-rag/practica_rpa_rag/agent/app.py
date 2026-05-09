# Punto de entrada del agente RPA por consola.
# Uso: python agent/app.py [mensaje]
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# load_dotenv() ya lo hace shared/load_model.py al importarse abajo

from langchain_core.messages import (  # noqa: E402
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402

from agent.agent import build_agent  # noqa: E402
from agent.agent_langgraph import build_agent_lg  # noqa: E402


# --- Selección de backend ---
def _pick_backend() -> str:
    """LangGraph StateGraph custom por defecto. `--lc` (o
    AGENT_BACKEND=langchain) fuerza la versión con create_agent de LangChain."""
    if "--lc" in sys.argv:
        sys.argv.remove("--lc")
        return "langchain"
    return os.getenv("AGENT_BACKEND", "langgraph").lower()


# --- Trazas en consola ---
def _print_event(event: dict, printed_ids: set) -> None:
    """Filtra por id para no reimprimir mensajes ya vistos."""
    for msg in event.get("messages", []):
        mid = getattr(msg, "id", None) or id(msg)
        if mid in printed_ids:
            continue
        printed_ids.add(mid)

        if isinstance(msg, (HumanMessage, SystemMessage)):
            continue

        if isinstance(msg, AIMessage):
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    args_preview = str(tc.get("args", {}))
                    if len(args_preview) > 120:
                        args_preview = args_preview[:117] + "..."
                    print(f"[tool-call] {tc['name']}({args_preview})")
                continue
            content = (msg.content or "").strip()
            if content:
                print(f"agente> {content}")
            continue

        if isinstance(msg, ToolMessage):
            preview = (msg.content or "").replace("\n", " ").strip()
            if len(preview) > 200:
                preview = preview[:197] + "..."
            print(f"[tool-result {msg.name}] {preview}")


# --- Gestión de la pausa del StateGraph (HITL) ---
def _hitl_si_pausado(agent, thread_id: str, printed: set) -> None:
    """Si el grafo está pausado antes de confirmar_rpa, pregunta y reanuda."""
    config = {"configurable": {"thread_id": thread_id}}
    while True:
        try:
            state = agent.get_state(config)
        except Exception:
            return  # backends sin get_state -> no hay HITL
        if not state.next:
            return  # el grafo terminó

        # Último AIMessage con tool_calls
        msgs = state.values.get("messages", []) if state.values else []
        ai = next(
            (m for m in reversed(msgs)
             if isinstance(m, AIMessage) and getattr(m, "tool_calls", None)),
            None,
        )
        if ai is None:
            for ev in agent.stream(None, config=config, stream_mode="values"):
                _print_event(ev, printed)
            continue

        run_tcs = [tc for tc in ai.tool_calls if tc["name"] == "run_workflow"]

        if not run_tcs:
            for ev in agent.stream(None, config=config, stream_mode="values"):
                _print_event(ev, printed)
            continue

        # Pido confirmación
        print()
        print("  --- confirmación humana antes de ejecutar el RPA ---")
        for tc in run_tcs:
            print(f"  workflow_id : {tc['args'].get('workflow_id')}")
            print(f"  params      : {tc['args'].get('params')}")
        try:
            resp = input("  ¿Ejecutar? [s/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            resp = "n"
        print()

        if resp in {"s", "si", "sí", "y", "yes"}:
            for ev in agent.stream(None, config=config, stream_mode="values"):
                _print_event(ev, printed)
        else:
            # Inyecto cancelación y reanudo para que el agente la cuente.
            cancelaciones = [
                ToolMessage(
                    content='{"ok": false, "cancelled_by_user": true, '
                            '"error": "El usuario canceló la ejecución del RPA."}',
                    tool_call_id=tc["id"],
                    name="run_workflow",
                )
                for tc in run_tcs
            ]
            agent.update_state(config, {"messages": cancelaciones})
            print("(cancelado por el usuario)")
            for ev in agent.stream(None, config=config, stream_mode="values"):
                _print_event(ev, printed)


def _run_turn(agent, user_text: str, thread_id: str, printed: set) -> None:
    """Un turno del chat. `printed` se comparte entre turnos."""
    config = {"configurable": {"thread_id": thread_id}}
    for event in agent.stream(
        {"messages": [HumanMessage(content=user_text)]},
        config=config,
        stream_mode="values",
    ):
        _print_event(event, printed)
    # Si el grafo se quedó pausado por interrupt_before, gestiono el HITL.
    _hitl_si_pausado(agent, thread_id, printed)


# --- Construcción del agente ---
def _make_agent(backend: str, *, checkpointer, hitl: bool):
    """langgraph (default): StateGraph custom con HITL como nodo del grafo.
    langchain: create_agent con HITL como middleware."""
    if backend == "langchain":
        print(f"[backend] LangChain · create_agent  (HITL={hitl})")
        return build_agent(checkpointer=checkpointer, hitl=hitl)
    print(f"[backend] LangGraph · StateGraph custom  (HITL={hitl})")
    return build_agent_lg(checkpointer=checkpointer, hitl_before_run=hitl)


# --- Modo A: un solo turno ---
def run_single_turn(user_text: str, backend: str) -> None:
    """Ejecuta un único turno y termina. AVISO: en single-turn NO hay confirmación humana."""
    agent = _make_agent(backend, checkpointer=MemorySaver(), hitl=False)
    _run_turn(agent, user_text, thread_id="oneshot", printed=set())


# --- Modo B: chat interactivo ---
def _pick_thread_id() -> str:
    """Permite retomar conversaciones reusando el thread_id."""
    default = "default"
    try:
        answer = input(
            f"¿thread_id? (enter para usar '{default}', o escribe uno nuevo) "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        answer = ""
    return answer or default


def run_chat_loop(backend: str) -> None:
    # SqliteSaver si se puede; si no, MemorySaver (sin historial al cerrar).
    saver_cm = None
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        (ROOT / "data").mkdir(exist_ok=True)
        sqlite_path = str(ROOT / "data" / "checkpoints.sqlite")
        saver_cm = SqliteSaver.from_conn_string(sqlite_path)
        checkpointer = saver_cm.__enter__()
        persistent = True
    except Exception as e:
        print(f"(aviso) SqliteSaver no disponible, usando MemorySaver en RAM: {e}")
        checkpointer = MemorySaver()
        persistent = False

    try:
        thread_id = _pick_thread_id() if persistent else "session"
        agent = _make_agent(backend, checkpointer=checkpointer, hitl=True)

        print()
        print("Agente RPA listo. Escribe tu petición ('exit' o Ctrl+C para salir).")
        print(f"(thread_id = {thread_id} · persistente = {persistent})")
        print()

        # printed persiste entre turnos para no reimprimir el historial.
        printed: set = set()

        while True:
            try:
                user_text = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nHasta luego.")
                break
            if not user_text:
                continue
            if user_text.lower() in {"exit", "quit", "salir"}:
                print("Hasta luego.")
                break
            _run_turn(agent, user_text, thread_id, printed)
            print()
    finally:
        if saver_cm is not None:
            saver_cm.__exit__(None, None, None)


# --- Entrada ---
def main() -> None:
    backend = _pick_backend()  # consume "--lc" si aparece
    args = sys.argv[1:]
    if args:
        run_single_turn(" ".join(args), backend)
    else:
        run_chat_loop(backend)


if __name__ == "__main__":
    main()
