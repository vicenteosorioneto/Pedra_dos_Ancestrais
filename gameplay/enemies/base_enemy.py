# gameplay/enemies/base_enemy.py — classe base de inimigo

from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from systems.tilemap import Tilemap


class Enemy:
    """
    Base para todos os inimigos. Fornece física, colisão AABB e controle de dano.
    Subclasses devem implementar update() e draw().
    """

    def __init__(self, x: float, y: float, w: int = 12, h: int = 28) -> None:
        self.x  = float(x)
        self.y  = float(y)
        self.w  = w
        self.h  = h
        self.vx = 0.0
        self.vy = 0.0

        self.hp      = 2
        self.max_hp  = 2
        self.facing  = 1
        self.alive   = True
        self.damage  = 1
        self.on_ground = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def center(self) -> tuple[int, int]:
        return (int(self.x + self.w / 2), int(self.y + self.h / 2))

    def take_damage(self, amount: int = 1) -> bool:
        """Aplica dano. Retorna True se o inimigo morreu."""
        if not self.alive:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.hp    = 0
            self.alive = False
            return True
        return False

    def apply_gravity(self, gravity: float = 0.4, max_fall: float = 8.0) -> None:
        self.vy = min(self.vy + gravity, max_fall)

    def collide_tilemap(self, tilemap: Tilemap) -> None:
        """Resolve colisão AABB com o tilemap."""
        self.x += self.vx
        r = self.rect
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                self.x  = tile_r.left - self.w if self.vx > 0 else float(tile_r.right)
                self.vx = 0.0
                r = self.rect

        self.y += self.vy
        r = self.rect
        self.on_ground = False
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                if self.vy > 0:
                    self.y         = float(tile_r.top - self.h)
                    self.on_ground = True
                    self.vy        = 0.0
                else:
                    self.y  = float(tile_r.bottom)
                    self.vy = 0.0
                r = self.rect

    def update(self, tilemap: Tilemap, player_rect: pygame.Rect | None = None) -> None:
        raise NotImplementedError

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float) -> None:
        raise NotImplementedError
