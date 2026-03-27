# systems/hud.py — HUD: corações, vidas, interação

import pygame
from settings import PALETTE_SERTAO as P, BLACK, GOLD, SCREEN_W, SCREEN_H
from art.fx import Particle, ParticleSystem
import math


def _draw_heart(surf, x, y, full=True):
    """Desenha coração 12x12 pixel art."""
    filled = P["heart_red"] if full else P["heart_empty"]
    dark   = (160, 25, 25) if full else (50, 20, 20)
    light  = (255, 100, 100) if full else (100, 50, 50)

    # Forma de coração
    shape = [
        "    XX  XX    ",
        "  XXXXXXXX  ",
        "  XXXXXXXXXX",
        "  XXXXXXXXXX",
        "   XXXXXXXXX",
        "    XXXXXXX ",
        "     XXXXX  ",
        "      XXX   ",
        "       X    ",
    ]
    # Versão simplificada 12x12
    pts = [
        (2,1),(3,1),(4,1),(7,1),(8,1),(9,1),
        (1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),
        (1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),
        (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),
        (2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),
        (3,6),(4,6),(5,6),(6,6),(7,6),(8,6),
        (4,7),(5,7),(6,7),(7,7),
        (5,8),(6,8),
    ]
    for hx, hy in pts:
        surf.set_at((x + hx, y + hy), filled)
    # Highlight
    for hx, hy in [(3,2),(4,2),(3,3)]:
        surf.set_at((x+hx, y+hy), light)
    # Outline
    outline_pts = [(1,1),(5,0),(6,0),(10,1),(11,2),(11,3),(11,4),(10,5),(9,6),(8,7),(7,8),(6,9),(5,9),(4,8),(3,7),(2,6),(1,5),(0,4),(0,3),(0,2)]
    for hx, hy in outline_pts:
        if 0 <= x+hx < surf.get_width() and 0 <= y+hy < surf.get_height():
            surf.set_at((x+hx, y+hy), BLACK)


class HUD:
    def __init__(self, karma_system=None):
        self.karma = karma_system
        self._font = None
        self._small_font = None
        # Partículas do HUD
        self.particles = []
        # Indicador de interação
        self.interaction_text = ""
        self.interaction_timer = 0

    def _init_fonts(self):
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("Courier New", 11, bold=True)
            except Exception:
                self._font = pygame.font.Font(None, 14)
        if self._small_font is None:
            try:
                self._small_font = pygame.font.SysFont("Courier New", 10)
            except Exception:
                self._small_font = pygame.font.Font(None, 12)

    def show_interaction(self, text):
        self.interaction_text = text
        self.interaction_timer = 5  # mantém enquanto chamar

    def emit_heart_break(self, heart_index):
        """Coração quebrado vira partículas."""
        hx = 8 + heart_index * 16
        hy = 8
        for _ in range(4):
            import random, math
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            p = Particle(hx, hy, P["heart_red"],
                        math.cos(angle)*speed, math.sin(angle)*speed - 1,
                        life=25, size=2)
            self.particles.append(p)

    def update(self):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()
        if self.interaction_timer > 0:
            self.interaction_timer -= 1

    def draw(self, surf, player_hp, player_max_hp=3):
        self._init_fonts()

        # ── Fundo do HUD (canto superior esquerdo) ──
        hud_bg = pygame.Surface((60, 20))
        hud_bg.set_alpha(180)
        hud_bg.fill(P["hud_bg"])
        surf.blit(hud_bg, (4, 4))
        pygame.draw.rect(surf, GOLD, (4, 4, 60, 20), 1)

        # ── Corações ──
        for i in range(player_max_hp):
            full = i < player_hp
            _draw_heart(surf, 8 + i * 16, 6, full)

        # ── Partículas de coração ──
        for p in self.particles:
            p.draw(surf)

        # ── Indicador de interação ──
        if self.interaction_timer > 0 and self.interaction_text:
            text = f"[X] {self.interaction_text}"
            ts = self._small_font.render(text, True, GOLD)
            bg = pygame.Surface((ts.get_width() + 8, ts.get_height() + 4))
            bg.fill(P["hud_bg"])
            bg.set_alpha(200)
            bx = (SCREEN_W - bg.get_width()) // 2
            by = SCREEN_H - 110
            surf.blit(bg, (bx, by))
            pygame.draw.rect(surf, GOLD, (bx, by, bg.get_width(), bg.get_height()), 1)
            surf.blit(ts, (bx + 4, by + 2))
