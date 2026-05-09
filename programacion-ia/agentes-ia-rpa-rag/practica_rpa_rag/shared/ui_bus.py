# Bus de eventos middleware -> UI. Una asyncio.Queue por thread_id.
# El productor (sync) cruza al loop con loop.call_soon_threadsafe.
from __future__ import annotations

import asyncio
import contextlib
from typing import Any


class UIEventBus:
    """Pub/sub en memoria con una cola por thread_id (1 turno = 1 SSE)."""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[dict[str, Any] | None]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def attach_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """La API la llama al arrancar para fijar el loop receptor."""
        self._loop = loop

    @contextlib.contextmanager
    def subscribe(self, thread_id: str):
        """Suscripción para un thread. Al salir, descarto lo pendiente."""
        q: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
        self._queues[thread_id] = q
        try:
            yield q
        finally:
            self._queues.pop(thread_id, None)

    def publish(self, thread_id: str, event: dict[str, Any]) -> None:
        """Mete un evento en la cola desde código sync (hilo del agente).
        Si no hay loop o suscripción, descarto en silencio."""
        if self._loop is None:
            return
        q = self._queues.get(thread_id)
        if q is None:
            return
        self._loop.call_soon_threadsafe(q.put_nowait, event)

    def close(self, thread_id: str) -> None:
        """Sentinel None para que el consumidor sepa que se acabó."""
        if self._loop is None:
            return
        q = self._queues.get(thread_id)
        if q is None:
            return
        self._loop.call_soon_threadsafe(q.put_nowait, None)


# Instancia compartida para todo el proceso.
bus = UIEventBus()
