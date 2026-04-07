# gameplay/enemies/guardian_statue.py — guardião estátua (mini-boss)

from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from gameplay.enemies.base_enemy import Enemy
from art.sprites import get_guardian_frame

if TYPE_CHECKING:
    from systems.tilemap import Tilemap
    from gameplay.player.player import Player


class GuardianStatue(Enemy):
    SPEED_P1            = 0.6
    SPEED_P2            = 1.2
    SHOCKWAVE_INTERVAL  = 120

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, w=26, h=44)
        self.hp     = 8
        self.max_hp = 8
        self.damage = 0   # dano via knockback, não HP direto
        self.phase  = 1
        self.speed  = self.SPEED_P1

        self.anim_frame      = 0
        self.anim_timer      = 0
        self.shockwave_timer = 0
        self.shockwaves: list[dict] = []
        self.defeated        = False
        self._dialogue_shown = False
        self.awaken_timer    = 60

    def update(self, tilemap: Tilemap, player_rect: pygame.Rect | None = None) -> None:
        if self.defeated:
            return

        if self.hp <= 4:
            self.phase = 2
            self.speed = self.SPEED_P2

        if player_rect:
            px = player_rect.centerx
            if px > self.x + self.w // 2:
                self.vx     = self.speed
                self.facing = 1
            else:
                self.vx     = -self.speed
                self.facing = -1

        self.apply_gravity()
        self.collide_tilemap(tilemap)

        if self.phase == 2:
            self.shockwave_timer += 1
            if self.shockwave_timer >= self.SHOCKWAVE_INTERVAL:
                self.shockwave_timer = 0
                self._create_shockwave()

        self.shockwaves = [sw for sw in self.shockwaves if sw["life"] > 0]
        for sw in self.shockwaves:
            sw["x"]    += sw["vx"]
            sw["life"] -= 1

        self.anim_timer += 1
        if self.anim_timer >= 20:
            self.anim_timer = 0
            self.anim_frame = 1 - self.anim_frame

        if self.awaken_timer > 0:
            self.awaken_timer -= 1

    def _create_shockwave(self) -> None:
        cx = int(self.x + self.w // 2)
        cy = int(self.y + self.h)
        base: dict = {"y": float(cy), "life": 40, "w": 8, "h": 6}
        self.shockwaves.append({**base, "x": float(cx), "vx":  3.0})
        self.shockwaves.append({**base, "x": float(cx), "vx": -3.0})

    def check_shockwave_hit(self, player_rect: pygame.Rect) -> bool:
        for sw in self.shockwaves:
            sr = pygame.Rect(int(sw["x"]) - sw["w"] // 2, int(sw["y"]) - sw["h"], sw["w"], sw["h"])
            if sr.colliderect(player_rect):
                return True
        return False

    def knockback_player(self, player: Player) -> None:
        player.vx = 4.0 if self.facing == 1 else -4.0
        player.vy = -3.0

    def defeat(self) -> None:
        self.defeated = True
        self.alive    = False

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float) -> None:
        frame  = 1 if self.awaken_timer > 0 else self.anim_frame
        sprite = get_guardian_frame(frame)
        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        surf.blit(sprite, (sx, sy))

        # Ondas de choque (fase 2)
        for sw in self.shockwaves:
            wx = int(sw["x"] - cam_x) - sw["w"] // 2
            wy = int(sw["y"] - cam_y) - sw["h"]
            pygame.draw.ellipse(surf, (200, 130, 30), (wx, wy, sw["w"], sw["h"]))

        # Barra de HP
        bx = sx
        by = sy - 8
        bw = self.w
        bh = 4
        pygame.draw.rect(surf, (30, 20, 10), (bx, by, bw, bh))
        hp_color = (220, 40, 40) if self.phase == 1 else (220, 130, 30)
        pygame.draw.rect(surf, hp_color, (bx, by, int(bw * self.hp / self.max_hp), bh))
        pygame.draw.rect(surf, (0, 0, 0), (bx, by, bw, bh), 1)
