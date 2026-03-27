# entities/guardian_statue.py — guardião estátua (mini-boss)

import pygame
from entities.enemy import Enemy
from art.sprites import get_guardian_frame


class GuardianStatue(Enemy):
    SPEED_P1   = 0.6
    SPEED_P2   = 1.2
    SHOCKWAVE_INTERVAL = 120

    def __init__(self, x, y):
        super().__init__(x, y, w=26, h=44)
        self.hp     = 8
        self.max_hp = 8
        self.damage = 0   # não causa dano de morte, apenas knockback
        self.phase  = 1   # 1 ou 2
        self.speed  = self.SPEED_P1
        self.anim_frame = 0
        self.anim_timer = 0
        self.shockwave_timer = 0
        self.shockwaves = []  # lista de ondas ativas
        self.defeated = False
        self._dialogue_shown = False
        # Piscar olhos ao acordar
        self.awaken_timer = 60

    def update(self, tilemap, player_rect=None):
        if self.defeated:
            return

        # Fase 2 ao HP baixo
        if self.hp <= 4:
            self.phase = 2
            self.speed = self.SPEED_P2

        # Mover em direção ao player
        if player_rect:
            px = player_rect.centerx
            if px > self.x + self.w//2:
                self.vx = self.speed
                self.facing = 1
            else:
                self.vx = -self.speed
                self.facing = -1

        self.apply_gravity()
        self.collide_tilemap(tilemap)

        # Fase 2: soca o chão
        if self.phase == 2:
            self.shockwave_timer += 1
            if self.shockwave_timer >= self.SHOCKWAVE_INTERVAL:
                self.shockwave_timer = 0
                self._create_shockwave()

        # Atualizar ondas
        self.shockwaves = [sw for sw in self.shockwaves if sw["life"] > 0]
        for sw in self.shockwaves:
            sw["x"] += sw["vx"]
            sw["life"] -= 1

        # Animação
        self.anim_timer += 1
        if self.anim_timer >= 20:
            self.anim_timer = 0
            self.anim_frame = 1 - self.anim_frame

        # Contar down de acordar
        if self.awaken_timer > 0:
            self.awaken_timer -= 1

    def _create_shockwave(self):
        """Cria ondas de choque nas duas direções."""
        cx = int(self.x + self.w//2)
        cy = int(self.y + self.h)
        self.shockwaves.append({"x": float(cx), "y": float(cy), "vx": 3.0, "life": 40, "w": 8, "h": 6})
        self.shockwaves.append({"x": float(cx), "y": float(cy), "vx": -3.0, "life": 40, "w": 8, "h": 6})

    def check_shockwave_hit(self, player_rect):
        """Retorna True se player foi atingido por onda de choque."""
        for sw in self.shockwaves:
            sr = pygame.Rect(int(sw["x"]) - sw["w"]//2, int(sw["y"]) - sw["h"],
                             sw["w"], sw["h"])
            if sr.colliderect(player_rect):
                return True
        return False

    def knockback_player(self, player):
        """Empurra player sem causar dano de morte."""
        if self.facing == 1:
            player.vx = 4.0
        else:
            player.vx = -4.0
        player.vy = -3.0

    def defeat(self):
        self.defeated = True
        self.alive    = False

    def draw(self, surf, cam_x, cam_y):
        # Frame 1 quando acordando, 0 normal
        frame = 1 if self.awaken_timer > 0 else self.anim_frame
        sprite = get_guardian_frame(frame)

        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        surf.blit(sprite, (sx, sy))

        # Ondas de choque (fase 2)
        for sw in self.shockwaves:
            wx = int(sw["x"] - cam_x) - sw["w"]//2
            wy = int(sw["y"] - cam_y) - sw["h"]
            alpha = int(200 * sw["life"] / 40)
            pygame.draw.ellipse(surf, (200, 130, 30), (wx, wy, sw["w"], sw["h"]))

        # Barra de HP (mini-boss)
        bar_x = int(self.x - cam_x)
        bar_y = int(self.y - cam_y) - 8
        bar_w = self.w
        bar_h = 4
        pygame.draw.rect(surf, (30, 20, 10), (bar_x, bar_y, bar_w, bar_h))
        hp_ratio = self.hp / self.max_hp
        hp_color = (220, 40, 40) if self.phase == 1 else (220, 130, 30)
        pygame.draw.rect(surf, hp_color, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
        pygame.draw.rect(surf, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 1)
