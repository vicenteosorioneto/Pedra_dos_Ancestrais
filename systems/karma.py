# systems/karma.py — sistema de karma silencioso (refatorado)

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from shared.enums import GameEvent

if TYPE_CHECKING:
    from core.event_bus import EventBus


@dataclass
class KarmaSummary:
    """Snapshot do estado de karma para leitura externa."""
    coragem:        int
    ganancia:       int
    sabedoria:      int
    divida_iracema: bool | None
    final:          str


class KarmaSystem:
    """
    Rastreia silenciosamente as escolhas morais do jogador ao longo do jogo.
    Pode ser usado com ou sem EventBus.

    Com EventBus: reage automaticamente a eventos do jogo (enemy_killed,
    dialogue_closed, pot_broken) e publica karma_changed após cada mudança.

    Sem EventBus: os métodos podem ser chamados diretamente pelas cenas.
    """

    def __init__(self, bus: EventBus | None = None) -> None:
        self.coragem:        int        = 0   # 0–5
        self.ganancia:       int        = 0   # 0–5
        self.sabedoria:      int        = 0   # 0–5
        self.divida_iracema: bool | None = None

        self._bus = bus
        if bus:
            bus.subscribe(GameEvent.ENEMY_KILLED,     self._on_enemy_killed)
            bus.subscribe(GameEvent.POT_BROKEN,       self._on_pot_broken)
            bus.subscribe(GameEvent.DIALOGUE_CLOSED,  self._on_dialogue_closed)
            bus.subscribe(GameEvent.ITEM_COLLECTED,   self._on_item_collected)

    # ── Reações automáticas a eventos ────────────────────────────────────────

    def _on_enemy_killed(self, **_) -> None:
        self.enfrentou_inimigo()

    def _on_pot_broken(self, **_) -> None:
        self.destruiu_pote_decorativo()

    def _on_dialogue_closed(self, npc_key: str = "", **_) -> None:
        self.conversou_com_npc()

    def _on_item_collected(self, is_trap: bool = False, **_) -> None:
        if is_trap:
            self.pegou_item_armadilha()

    def _publish(self) -> None:
        if self._bus:
            self._bus.publish(GameEvent.KARMA_CHANGED, summary=self.get_summary())

    # ── Coragem ──────────────────────────────────────────────────────────────

    def ajudou_espirito(self) -> None:
        self.coragem = min(5, self.coragem + 1)
        self._publish()

    def enfrentou_inimigo(self) -> None:
        self.coragem = min(5, self.coragem + 1)
        self._publish()

    def ignorou_npc_em_perigo(self) -> None:
        self.coragem = max(0, self.coragem - 1)
        self._publish()

    # ── Ganância ─────────────────────────────────────────────────────────────

    def pegou_item_armadilha(self) -> None:
        self.ganancia = min(5, self.ganancia + 1)
        self._publish()

    def destruiu_pote_decorativo(self) -> None:
        self.ganancia = min(5, self.ganancia + 1)
        self._publish()

    def deixou_item_valioso(self) -> None:
        self.ganancia = max(0, self.ganancia - 1)
        self._publish()

    # ── Sabedoria ────────────────────────────────────────────────────────────

    def leu_registro(self) -> None:
        self.sabedoria = min(5, self.sabedoria + 1)
        self._publish()

    def resolveu_puzzle_perfeito(self) -> None:
        self.sabedoria = min(5, self.sabedoria + 1)
        self._publish()

    def conversou_com_npc(self) -> None:
        self.sabedoria = min(5, self.sabedoria + 1)
        self._publish()

    # ── Iracema ──────────────────────────────────────────────────────────────

    def aceitou_trato_honrou(self) -> None:
        self.divida_iracema = True
        self._publish()

    def aceitou_trato_traiu(self) -> None:
        self.divida_iracema = False
        self._publish()

    def recusou_trato(self) -> None:
        self.divida_iracema = None
        self._publish()

    # ── Final ────────────────────────────────────────────────────────────────

    @property
    def final_type(self) -> str:
        if self.ganancia >= 3:
            return "ruim"
        if (self.coragem >= 2 and self.sabedoria >= 2
                and self.ganancia <= 1 and self.divida_iracema == True):
            return "verdadeiro"
        return "neutro"

    def get_summary(self) -> KarmaSummary:
        return KarmaSummary(
            coragem=self.coragem,
            ganancia=self.ganancia,
            sabedoria=self.sabedoria,
            divida_iracema=self.divida_iracema,
            final=self.final_type,
        )
