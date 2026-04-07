# scenes/intro_scene.py — tela de título

import pygame
import math
import random
from settings import SCREEN_W, SCREEN_H, PALETTE_SERTAO as P, BLACK, GOLD, SCENE_VILLAGE
from art.fx import Particle


def _draw_pedra_castelo_large(surf, cx, cy):
    """Desenha a Pedra do Castelo como pixel art no centro da tela de título."""
    rock_mid   = P["rock_mid"]
    rock_dark  = P["rock_dark"]
    rock_light = P["rock_light"]
    shadow_col = (60, 40, 20)

    # Sombra base
    pygame.draw.ellipse(surf, shadow_col, (cx - 80, cy + 85, 160, 20))

    # Coluna central (mais alta) — 3 blocos
    pygame.draw.rect(surf, rock_dark,  (cx - 22, cy - 80, 44, 170))
    pygame.draw.rect(surf, rock_mid,   (cx - 20, cy - 80, 40, 170))
    pygame.draw.rect(surf, rock_light, (cx + 8,  cy - 75, 8,  160))
    # Topo ameado da coluna central
    for i in range(-20, 21, 10):
        pygame.draw.rect(surf, rock_dark, (cx + i - 4, cy - 95, 8, 18))
    pygame.draw.rect(surf, rock_mid, (cx - 20, cy - 82, 40, 10))

    # Coluna esquerda (média)
    pygame.draw.rect(surf, rock_dark,  (cx - 62, cy - 40, 34, 130))
    pygame.draw.rect(surf, rock_mid,   (cx - 60, cy - 40, 30, 130))
    pygame.draw.rect(surf, rock_light, (cx - 34, cy - 35, 6,  120))
    # Topo ameado esquerdo
    for i in range(-60, -25, 10):
        pygame.draw.rect(surf, rock_dark, (cx + i, cy - 55, 8, 18))
    pygame.draw.rect(surf, rock_mid, (cx - 60, cy - 44, 30, 8))

    # Coluna direita (pequena)
    pygame.draw.rect(surf, rock_dark,  (cx + 28, cy - 20, 30, 110))
    pygame.draw.rect(surf, rock_mid,   (cx + 30, cy - 20, 26, 110))
    pygame.draw.rect(surf, rock_light, (cx + 48, cy - 16, 6,  100))
    # Topo ameado direito
    for i in range(28, 60, 10):
        pygame.draw.rect(surf, rock_dark, (cx + i, cy - 35, 8, 18))
    pygame.draw.rect(surf, rock_mid, (cx + 28, cy - 24, 26, 8))

    # "Janelas" / cavidades escuras
    cavidades = [
        (cx - 10, cy - 60, 8, 12),   # janela central alta
        (cx - 8,  cy - 30, 6, 10),   # janela central baixa
        (cx - 52, cy - 20, 6, 10),   # janela esquerda
        (cx - 48, cy + 10, 5, 8),    # janela esquerda baixo
        (cx + 36, cy     , 5, 8),    # janela direita
    ]
    for rect in cavidades:
        pygame.draw.rect(surf, (10, 5, 20), rect)
        # Brilho leve âmbar dentro
        r = pygame.Rect(rect)
        pygame.draw.rect(surf, (60, 40, 10), (r.x+1, r.y+1, max(1, r.w-2), 2))

    # Base rochosa irregular
    base_pts = [
        (cx - 80, cy + 90), (cx - 70, cy + 80), (cx - 60, cy + 88),
        (cx - 40, cy + 82), (cx - 22, cy + 88), (cx,      cy + 90),
        (cx + 22, cy + 86), (cx + 45, cy + 88), (cx + 58, cy + 82),
        (cx + 75, cy + 90), (cx + 80, cy + 110), (cx - 80, cy + 110),
    ]
    pygame.draw.polygon(surf, rock_dark, base_pts)

    # Rachaduras verticais
    pygame.draw.line(surf, rock_dark, (cx - 5, cy - 78), (cx - 3, cy - 20), 1)
    pygame.draw.line(surf, rock_dark, (cx + 8, cy - 50), (cx + 10, cy + 40), 1)
    pygame.draw.line(surf, rock_dark, (cx - 45, cy - 38), (cx - 43, cy + 20), 1)


class IntroScene:
    def __init__(self, scene_manager, bus, karma, input_manager):
        self.scene_manager = scene_manager
        self.bus           = bus
        self.karma         = karma
        self.input         = input_manager
        self.blink_timer = 0
        self.blink_state = True
        self.particles   = []
        self.time        = 0
        self._font_title = None
        self._font_sub   = None
        self._font_press = None
        self._initialized = False

        # Seed fixa para estrelas
        self._star_rng = random.Random(7)
        self._stars = []

    def on_enter(self):
        self._initialized = False

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def _init(self):
        if self._initialized:
            return
        self._initialized = True
        try:
            self._font_title = pygame.font.SysFont("Courier New", 22, bold=True)
            self._font_sub   = pygame.font.SysFont("Courier New", 11)
            self._font_press = pygame.font.SysFont("Courier New", 11, bold=True)
        except Exception:
            self._font_title = pygame.font.Font(None, 28)
            self._font_sub   = pygame.font.Font(None, 14)
            self._font_press = pygame.font.Font(None, 14)

        # Gera estrelas com seed fixa
        for _ in range(80):
            x = self._star_rng.randint(0, SCREEN_W - 1)
            y = self._star_rng.randint(0, SCREEN_H // 3)
            sz = self._star_rng.choice([1, 1, 1, 2])
            self._stars.append((x, y, sz))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_game()

    def _start_game(self):
        from scenes.village_scene import VillageScene
        self.scene_manager.replace(VillageScene(self.scene_manager, self.bus, self.karma, self.input))

    def update(self):
        self._init()
        self.time += 1
        self.blink_timer += 1
        if self.blink_timer >= 40:
            self.blink_timer = 0
            self.blink_state = not self.blink_state

        # Partículas de poeira subindo
        if self.time % 8 == 0:
            import random as r2
            x = r2.randint(0, SCREEN_W)
            self.particles.append(Particle(
                x, SCREEN_H,
                color=(160, 120, 80),
                vx=r2.uniform(-0.3, 0.3),
                vy=r2.uniform(-0.8, -0.3),
                life=r2.randint(60, 120),
                size=1
            ))
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

    def draw(self, surf):
        self._init()

        # ── Gradiente de céu ──
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            # roxo no topo → vermelho → laranja na base
            if t < 0.3:
                t2 = t / 0.3
                r = int(80  + t2 * (180 - 80))
                g = int(30  + t2 * (50  - 30))
                b = int(100 + t2 * (50  - 100))
            elif t < 0.7:
                t2 = (t - 0.3) / 0.4
                r = int(180 + t2 * (255 - 180))
                g = int(50  + t2 * (140 - 50))
                b = int(50  + t2 * (60  - 50))
            else:
                t2 = (t - 0.7) / 0.3
                r = int(255)
                g = int(140 + t2 * (200 - 140))
                b = int(60  + t2 * (80  - 60))
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))

        # ── Estrelas ──
        for sx, sy, sz in self._stars:
            if sz == 1:
                surf.set_at((sx, sy), (220, 220, 200))
            else:
                pygame.draw.rect(surf, (240, 240, 220), (sx, sy, 2, 2))

        # ── Lua ──
        moon_x, moon_y = 60, 45
        pygame.draw.circle(surf, (240, 235, 200), (moon_x, moon_y), 18)
        pygame.draw.circle(surf, (220, 215, 170), (moon_x, moon_y), 18, 1)
        # sombra da lua
        pygame.draw.circle(surf, (200, 190, 140), (moon_x + 6, moon_y - 4), 12)

        # ── Pedra do Castelo ──
        _draw_pedra_castelo_large(surf, SCREEN_W // 2, SCREEN_H // 2 + 20)

        # ── Partículas de poeira ──
        for p in self.particles:
            p.draw(surf)

        # ── Título ──
        title  = self._font_title.render("A PEDRA DOS ANCESTRAIS", True, GOLD)
        shadow = self._font_title.render("A PEDRA DOS ANCESTRAIS", True, (40, 20, 0))
        tx = (SCREEN_W - title.get_width()) // 2
        ty = 18
        surf.blit(shadow, (tx + 2, ty + 2))
        surf.blit(title,  (tx, ty))

        # ── Subtítulo ──
        sub = self._font_sub.render("Uma lenda do Piauí", True, (220, 180, 120))
        sx  = (SCREEN_W - sub.get_width()) // 2
        surf.blit(sub, (sx, ty + 28))

        # ── "Pressione ENTER" piscante ──
        if self.blink_state:
            press = self._font_press.render("Pressione ENTER para começar", True, (255, 220, 120))
            px = (SCREEN_W - press.get_width()) // 2
            surf.blit(press, (px, SCREEN_H - 30))

        # ── Controles ──
        ctrl = self._font_sub.render("WASD/Setas: mover  |  Espaço: pular  |  Z: atacar  |  X: interagir", True, (160, 140, 100))
        cx   = (SCREEN_W - ctrl.get_width()) // 2
        surf.blit(ctrl, (cx, SCREEN_H - 16))
