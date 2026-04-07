# core/input_manager.py — mapeamento de ações de jogo

from __future__ import annotations
from dataclasses import dataclass, field
import pygame


@dataclass
class InputState:
    """
    Snapshot de input de um frame.
    Player e outros sistemas recebem isso — nunca pygame.K_* diretamente.
    """
    move_left:  bool = False
    move_right: bool = False
    jump:       bool = False
    attack:     bool = False
    interact:   bool = False
    pause:      bool = False


# Mapeamento padrão: ação → lista de teclas aceitas
DEFAULT_BINDINGS: dict[str, list[int]] = {
    "move_left":  [pygame.K_LEFT,  pygame.K_a],
    "move_right": [pygame.K_RIGHT, pygame.K_d],
    "jump":       [pygame.K_SPACE, pygame.K_UP, pygame.K_w],
    "attack":     [pygame.K_z,     pygame.K_j],
    "interact":   [pygame.K_x,     pygame.K_k],
    "pause":      [pygame.K_ESCAPE],
}


class InputManager:
    """
    Lê o estado atual do teclado e retorna um InputState.
    Para remapear: substitua DEFAULT_BINDINGS ou passe bindings customizados.
    """

    def __init__(self, bindings: dict[str, list[int]] | None = None) -> None:
        self._bindings = bindings or DEFAULT_BINDINGS

    def poll(self) -> InputState:
        """Retorna o InputState do frame atual."""
        keys = pygame.key.get_pressed()
        return InputState(
            move_left  = any(keys[k] for k in self._bindings["move_left"]),
            move_right = any(keys[k] for k in self._bindings["move_right"]),
            jump       = any(keys[k] for k in self._bindings["jump"]),
            attack     = any(keys[k] for k in self._bindings["attack"]),
            interact   = any(keys[k] for k in self._bindings["interact"]),
            pause      = any(keys[k] for k in self._bindings["pause"]),
        )
