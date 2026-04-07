# tests/test_event_bus.py — testes do EventBus
# Executar com: pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.event_bus import EventBus


class TestEventBus:
    def test_subscribe_e_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe("teste", lambda **d: received.append(d))
        bus.publish("teste", valor=42)
        assert received == [{"valor": 42}]

    def test_multiplos_subscribers(self):
        bus = EventBus()
        a, b = [], []
        bus.subscribe("ev", lambda **d: a.append(d))
        bus.subscribe("ev", lambda **d: b.append(d))
        bus.publish("ev", x=1)
        assert len(a) == 1
        assert len(b) == 1

    def test_evento_sem_subscribers_nao_quebra(self):
        bus = EventBus()
        bus.publish("evento_sem_ninguem", x=1)  # não deve lançar

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        cb = lambda **d: received.append(d)
        bus.subscribe("ev", cb)
        bus.unsubscribe("ev", cb)
        bus.publish("ev", x=1)
        assert received == []

    def test_subscribe_nao_duplica(self):
        bus = EventBus()
        count = []
        cb = lambda **_: count.append(1)
        bus.subscribe("ev", cb)
        bus.subscribe("ev", cb)  # segunda vez deve ser ignorada
        bus.publish("ev")
        assert len(count) == 1

    def test_clear_remove_todos(self):
        bus = EventBus()
        received = []
        bus.subscribe("ev", lambda **d: received.append(d))
        bus.clear()
        bus.publish("ev", x=1)
        assert received == []
