# scenes/base_scene.py — contrato base para todas as cenas

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from core.scene_manager import SceneManager
    from core.event_bus import EventBus
    from core.input_manager import InputManager
    from systems.karma import KarmaSystem


class BaseScene:
    """
    Classe base para todas as cenas do jogo.

    Toda cena deve herdar desta classe e implementar ao menos
    handle_event(), update() e draw().

    Ciclo de vida:
        on_enter()   — chamado ao empilhar ou substituir a cena
        on_exit()    — chamado ao remover da pilha
        on_resume()  — chamado ao voltar ao topo após pop de outra cena
    """

    def __init__(
        self,
        scene_manager: SceneManager,
        bus: EventBus,
        karma: KarmaSystem,
        input_manager: InputManager,
    ) -> None:
        self.scene_manager = scene_manager
        self.bus           = bus
        self.karma         = karma
        self.input         = input_manager

    # ── Ciclo de vida ────────────────────────────────────────────────────────

    def on_enter(self) -> None:
        """Inicializar recursos. Chamado uma vez ao entrar na cena."""

    def on_exit(self) -> None:
        """Liberar recursos. Chamado ao sair da cena."""

    def on_resume(self) -> None:
        """Chamado quando a cena volta ao topo da pilha (após pop de outra)."""

    # ── Loop ─────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa eventos pygame."""

    def update(self) -> None:
        """Atualiza lógica de jogo (chamado a cada frame)."""

    def draw(self, surf: pygame.Surface) -> None:
        """Renderiza na superfície interna 640×360."""
