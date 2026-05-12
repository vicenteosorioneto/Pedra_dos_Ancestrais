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


@dataclass(frozen=True)
class JourneySummary:
    """Narrative progress shown on the ending screen."""
    village_talks: int = 0
    village_talks_total: int = 0
    forest_records: int = 0
    forest_records_total: int = 0
    ruins_seals: int = 0
    ruins_seals_total: int = 0
    ruins_records: int = 0
    ruins_records_total: int = 0
    trail_altars: int = 0
    trail_altars_total: int = 0
    trail_records: int = 0
    trail_records_total: int = 0
    cave_records: int = 0
    cave_records_total: int = 0
    rewards: int = 0
    rewards_total: int = 0
    guardian_freed: bool = False
    iracema_choice: str = ""


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
        self._journey: dict[str, int | bool | str] = {}

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

    def record_progress(self, key: str, value: int | bool | str, total: int | None = None) -> None:
        """Stores named story progress for the ending recap."""
        self._journey[key] = value
        if total is not None:
            self._journey[f"{key}_total"] = total

    def add_reward_progress(self, collected: int, total: int) -> None:
        best = max(int(collected), int(self._journey.get("rewards", 0)))
        best_total = max(int(total), int(self._journey.get("rewards_total", 0)))
        self.record_progress("rewards", best, best_total)

    def get_journey_summary(self) -> JourneySummary:
        data = self._journey
        return JourneySummary(
            village_talks=int(data.get("village_talks", 0)),
            village_talks_total=int(data.get("village_talks_total", 0)),
            forest_records=int(data.get("forest_records", 0)),
            forest_records_total=int(data.get("forest_records_total", 0)),
            ruins_seals=int(data.get("ruins_seals", 0)),
            ruins_seals_total=int(data.get("ruins_seals_total", 0)),
            ruins_records=int(data.get("ruins_records", 0)),
            ruins_records_total=int(data.get("ruins_records_total", 0)),
            trail_altars=int(data.get("trail_altars", 0)),
            trail_altars_total=int(data.get("trail_altars_total", 0)),
            trail_records=int(data.get("trail_records", 0)),
            trail_records_total=int(data.get("trail_records_total", 0)),
            cave_records=int(data.get("cave_records", 0)),
            cave_records_total=int(data.get("cave_records_total", 0)),
            rewards=int(data.get("rewards", 0)),
            rewards_total=int(data.get("rewards_total", 0)),
            guardian_freed=bool(data.get("guardian_freed", False)),
            iracema_choice=str(data.get("iracema_choice", "")),
        )

    # ── Coragem ──────────────────────────────────────────────────────────────

    def ajudou_espirito(self) -> None:
        self.coragem = min(5, self.coragem + 1)
        self.record_progress("guardian_freed", True)
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
        self.record_progress("iracema_choice", "honrou")
        self._publish()

    def aceitou_trato_traiu(self) -> None:
        self.divida_iracema = False
        self.record_progress("iracema_choice", "traiu")
        self._publish()

    def recusou_trato(self) -> None:
        self.divida_iracema = None
        self.record_progress("iracema_choice", "recusou")
        self._publish()

    # ── Final ────────────────────────────────────────────────────────────────

    @property
    def final_type(self) -> str:
        if self.ganancia >= 3:
            return "ruim"
        if self.coragem >= 2 and self.sabedoria >= 2 and self.ganancia <= 1:
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
