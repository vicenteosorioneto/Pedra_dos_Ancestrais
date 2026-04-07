# tests/test_karma.py — testes unitários do KarmaSystem
# Executar com: pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.karma import KarmaSystem, KarmaSummary
from core.event_bus import EventBus
from shared.enums import GameEvent


class TestKarmaFinals:
    def test_final_verdadeiro(self):
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        k.conversou_com_npc()
        k.conversou_com_npc()
        assert k.final_type == "verdadeiro"

    def test_final_ruim_por_ganancia(self):
        k = KarmaSystem()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        assert k.final_type == "ruim"

    def test_final_neutro(self):
        k = KarmaSystem()
        assert k.final_type == "neutro"

    def test_ganancia_nao_ultrapassa_5(self):
        k = KarmaSystem()
        for _ in range(10):
            k.pegou_item_armadilha()
        assert k.ganancia == 5

    def test_coragem_nao_ultrapassa_5(self):
        k = KarmaSystem()
        for _ in range(10):
            k.enfrentou_inimigo()
        assert k.coragem == 5

    def test_coragem_nao_vai_abaixo_de_0(self):
        k = KarmaSystem()
        for _ in range(5):
            k.ignorou_npc_em_perigo()
        assert k.coragem == 0


class TestKarmaComEventBus:
    def test_enemy_killed_incrementa_coragem(self):
        bus = EventBus()
        k = KarmaSystem(bus)
        bus.publish(GameEvent.ENEMY_KILLED)
        assert k.coragem == 1

    def test_pot_broken_incrementa_ganancia(self):
        bus = EventBus()
        k = KarmaSystem(bus)
        bus.publish(GameEvent.POT_BROKEN)
        assert k.ganancia == 1

    def test_dialogue_closed_incrementa_sabedoria(self):
        bus = EventBus()
        k = KarmaSystem(bus)
        bus.publish(GameEvent.DIALOGUE_CLOSED, npc_key="aldeao_1")
        assert k.sabedoria == 1

    def test_karma_publica_karma_changed(self):
        bus = EventBus()
        k = KarmaSystem(bus)
        received = []
        bus.subscribe(GameEvent.KARMA_CHANGED, lambda **d: received.append(d))
        k.enfrentou_inimigo()
        assert len(received) == 1
        assert received[0]["summary"].coragem == 1

    def test_get_summary_retorna_dataclass(self):
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.conversou_com_npc()
        s = k.get_summary()
        assert isinstance(s, KarmaSummary)
        assert s.coragem == 1
        assert s.sabedoria == 1
        assert s.final == "neutro"


class TestKarmaIracema:
    def test_honrou_trato(self):
        k = KarmaSystem()
        k.aceitou_trato_honrou()
        assert k.divida_iracema is True

    def test_traiu_trato(self):
        k = KarmaSystem()
        k.aceitou_trato_traiu()
        assert k.divida_iracema is False

    def test_recusou_trato(self):
        k = KarmaSystem()
        k.aceitou_trato_honrou()
        k.recusou_trato()
        assert k.divida_iracema is None
