# gameplay/npcs/npc.py — NPCs com diálogos e patrulha simples

from __future__ import annotations
import pygame
from typing import Callable
from art.sprites import get_npc_villager, get_npc_elder


class NPC:
    W          = 12
    H          = 28
    WALK_SPEED = 0.5

    def __init__(
        self,
        x: float,
        y: float,
        npc_key: str,
        sprite_fn: Callable | None = None,
        patrol_range: float = 0,
    ) -> None:
        self.x   = float(x)
        self.y   = float(y)
        self.npc_key      = npc_key
        self.sprite_fn    = sprite_fn
        self.patrol_origin = float(x)
        self.patrol_range  = float(patrol_range)
        self.facing    = 1
        self.walk_dir  = 1
        self.walk_timer = 0
        self.pause_timer = 0
        self.anim_frame  = 0
        self.anim_timer  = 0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self) -> None:
        if self.patrol_range <= 0:
            return
        if self.pause_timer > 0:
            self.pause_timer -= 1
            return

        self.x       += self.walk_dir * self.WALK_SPEED
        self.facing   = self.walk_dir

        if self.x > self.patrol_origin + self.patrol_range:
            self.walk_dir    = -1
            self.pause_timer = 60
        elif self.x < self.patrol_origin - self.patrol_range:
            self.walk_dir    = 1
            self.pause_timer = 60

        self.anim_timer += 1
        if self.anim_timer >= 12:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float) -> None:
        sprite = self.sprite_fn(direction=self.facing) if self.sprite_fn else get_npc_villager(0, self.facing)
        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        surf.blit(sprite, (int(self.x - cam_x) - 2, int(self.y - cam_y) - 4))

    def get_avatar(self) -> pygame.Surface:
        """Surface para uso no avatar da caixa de diálogo."""
        return self.sprite_fn(direction=1) if self.sprite_fn else get_npc_villager(0, 1)


class VillagerNPC(NPC):
    def __init__(self, x: float, y: float, variant: int = 0, patrol_range: float = 40) -> None:
        super().__init__(
            x, y,
            npc_key=f"aldeao_{variant + 1}",
            sprite_fn=lambda direction: get_npc_villager(variant, direction),
            patrol_range=0 if variant >= 2 else patrol_range,
        )
        self.variant = variant


class ElderNPC(NPC):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x, y,
            npc_key="zequinha",
            sprite_fn=lambda direction: get_npc_elder(direction),
            patrol_range=0,
        )


class ComercianteNPC(NPC):
    """Comerciante da vila — usa visual de aldeão variante 2."""
    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x, y,
            npc_key="comerciante",
            sprite_fn=lambda direction: get_npc_villager(2, direction),
            patrol_range=0,
        )
