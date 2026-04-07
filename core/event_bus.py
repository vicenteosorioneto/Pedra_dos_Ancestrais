# core/event_bus.py — pub/sub desacoplado entre sistemas

from __future__ import annotations
from collections import defaultdict
from typing import Any, Callable


class EventBus:
    """
    Bus de eventos simples. Sistemas publicam eventos sem saber quem vai reagir.

    Uso:
        bus = EventBus()
        bus.subscribe("player_damaged", my_callback)
        bus.publish("player_damaged", hp=2, max_hp=3, x=100, y=200)
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable[..., None]) -> None:
        """Registra callback para um tipo de evento."""
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable[..., None]) -> None:
        """Remove callback de um tipo de evento."""
        listeners = self._subscribers.get(event, [])
        if callback in listeners:
            listeners.remove(callback)

    def publish(self, event: str, **data: Any) -> None:
        """Publica evento para todos os callbacks registrados."""
        for cb in list(self._subscribers.get(event, [])):
            cb(**data)

    def clear(self) -> None:
        """Remove todos os listeners (útil ao trocar de cena)."""
        self._subscribers.clear()
