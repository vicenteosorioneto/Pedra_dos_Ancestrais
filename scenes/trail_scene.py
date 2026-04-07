# scenes/trail_scene.py — Ato 2: Trilha da Pedra (noturna)

import pygame
import math
import random
from settings import (
    SCREEN_W, SCREEN_H, TILE_SIZE, PALETTE_SERTAO as P, BLACK, GOLD
)
from systems.tilemap import Tilemap
from systems.dialogue import DialogueBox, SystemMessage
from systems.hud import HUD
from entities.player import Player
from entities.bat_enemy import BatEnemy
from core.camera import Camera
from art.fx import ParticleSystem, ScreenEffects, draw_stars


def _build_trail_map():
    COLS = 70
    ROWS = 22
    data = [[0] * COLS for _ in range(ROWS)]

    # Chão base
    for col in range(COLS):
        data[18][col] = 1
        data[19][col] = 2
        data[20][col] = 3
        data[21][col] = 3

    # Degraus subindo da esquerda para direita
    steps = [
        (0,  18, range(0, 10)),
        (1,  17, range(8, 18)),
        (2,  16, range(16, 26)),
        (3,  15, range(24, 34)),
        (2,  16, range(32, 42)),
        (4,  14, range(40, 50)),
        (3,  15, range(48, 58)),
        (5,  13, range(56, 68)),
    ]
    for dy, row, cols in steps:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 8   # pedra_castelo
                for y in range(row+1, min(row+3, ROWS)):
                    data[y][col] = 2

    # Plataformas flutuantes com pedra de castelo
    platforms = [
        (range(12, 18), 13),
        (range(22, 28), 11),
        (range(35, 41), 12),
        (range(46, 52), 10),
        (range(58, 64), 9),
    ]
    for cols, row in platforms:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 8

    # Altares (3 posições)
    altar_positions = [(20, 17), (38, 15), (55, 13)]

    return data, COLS, ROWS, altar_positions


def _draw_night_sky(surf, cam_x):
    """Céu noturno com gradiente roxo."""
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        r = int(20  + t * 30)
        g = int(10  + t * 20)
        b = int(40  + t * 30)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))


def _draw_moon(surf, cam_x):
    offset = int(cam_x * 0.05)
    mx = SCREEN_W // 2 - offset % SCREEN_W
    my = 40
    pygame.draw.circle(surf, (240, 235, 200), (mx, my), 22)
    pygame.draw.circle(surf, (220, 215, 170), (mx, my), 22, 1)
    # brilho lunar difuso
    glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (240, 235, 200, 30), (40, 40), 40)
    surf.blit(glow_surf, (mx - 40, my - 40))


def _draw_pedra_bg_trail(surf, cam_x):
    """Pedra do Castelo maior e mais próxima."""
    from scenes.village_scene import _draw_pedra_bg_art
    offset = int(cam_x * 0.15)
    cx = SCREEN_W - 100 - offset % (SCREEN_W + 300)
    cy = SCREEN_H - 100
    _draw_pedra_bg_art(surf, cx, cy, scale=1.2)


def _draw_torch(surf, tx, ty, cam_x, cam_y, time):
    """Tocha pixel art com chama animada."""
    sx = tx - cam_x
    sy = ty - cam_y
    if not (-20 < sx < SCREEN_W + 20):
        return
    # Poste
    pygame.draw.rect(surf, (80, 55, 25), (int(sx), int(sy), 3, 20))
    # Chama (animada)
    flicker = int(math.sin(time * 0.15 + tx * 0.1) * 2)
    flame_pts = [
        (int(sx) + 1, int(sy) - 8 + flicker),
        (int(sx) - 2, int(sy) - 2),
        (int(sx) + 4, int(sy) - 2),
    ]
    pygame.draw.polygon(surf, (255, 160, 30), flame_pts)
    pygame.draw.circle(surf, (255, 220, 80), (int(sx)+1, int(sy)-4), 3)
    # Luz em volta
    glow = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 140, 30, 40), (15, 15), 15)
    surf.blit(glow, (int(sx) - 14, int(sy) - 14))


class Altar:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.activated = False
        self.activate_timer = 0
        self.time = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), 14, 16)

    def activate(self):
        if not self.activated:
            self.activated = True
            self.activate_timer = 60
        return not self.activated

    def update(self, particle_sys):
        self.time += 1
        if self.activate_timer > 0:
            self.activate_timer -= 1
        if self.activated and self.time % 4 == 0:
            particle_sys.emit_altar(
                int(self.x) + 7,
                int(self.y)
            )

    def draw(self, surf, cam_x, cam_y, time):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if not (-20 < sx < SCREEN_W + 20):
            return

        # Base do altar
        col = (180, 130, 50) if self.activated else (100, 80, 60)
        pygame.draw.rect(surf, col, (sx, sy + 8, 14, 8))
        pygame.draw.rect(surf, col, (sx + 2, sy, 10, 10))

        # Símbolo dos guardiões (espiral simples)
        glyph_col = (220, 180, 80) if self.activated else (80, 60, 40)
        cx, cy = sx + 7, sy + 5
        for a in range(0, 360, 45):
            rad = math.radians(a)
            px  = cx + int(math.cos(rad) * 3)
            py  = cy + int(math.sin(rad) * 3)
            if 0 <= px < SCREEN_W and 0 <= py < SCREEN_H:
                surf.set_at((px, py), glyph_col)
        # Centro
        surf.set_at((cx, cy), glyph_col)

        # Pulsação quando ativo
        if self.activated:
            pscale = 1.0 + 0.3 * abs(math.sin(time * 0.1))
            pygame.draw.circle(surf, (200, 150, 30), (cx, cy),
                               int(6 * pscale), 1)


class TrailScene:
    WORLD_COLS = 70
    WORLD_ROWS = 22
    WORLD_W    = WORLD_COLS * TILE_SIZE
    WORLD_H    = WORLD_ROWS * TILE_SIZE
    NEXT_SCENE_X = (WORLD_COLS - 2) * TILE_SIZE

    def __init__(self, scene_manager, bus, karma, input_manager, player=None):
        self.scene_manager = scene_manager
        self.bus           = bus
        self.karma         = karma
        self.input         = input_manager
        self._prev_player  = player
        self._ready        = False

    def on_enter(self):
        self._setup()

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def _setup(self):
        map_data, cols, rows, altar_positions = _build_trail_map()
        self.tilemap   = Tilemap(map_data)
        self.camera    = Camera(self.WORLD_W, self.WORLD_H)
        self.particles = ParticleSystem()
        self.fx        = ScreenEffects(SCREEN_W, SCREEN_H)
        self.dialogue  = DialogueBox()
        self.sys_msg   = SystemMessage()
        self.hud       = HUD(self.karma)
        self.time      = 0
        self._paused   = False
        self._transitioning = False
        self._transition_timer = 0

        # Reutiliza HP do player anterior
        start_y = 17 * TILE_SIZE - Player.H
        self.player = Player(30, start_y, self.bus)
        if self._prev_player:
            self.player.hp = max(1, self._prev_player.hp)

        # Inimigos: 3 morcegos
        bat_y = 10 * TILE_SIZE
        self.enemies = [
            BatEnemy(200, bat_y),
            BatEnemy(350, bat_y - 20),
            BatEnemy(500, bat_y + 15),
        ]

        # Altares
        self.altars = [
            Altar(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE - 16)
            for pos in altar_positions
        ]
        self._altars_activated = 0
        self._portal_open = False

        # Tochas
        self.torches = [
            (col * TILE_SIZE, row * TILE_SIZE - 30)
            for col in range(5, self.WORLD_COLS, 12)
            for row in [18]
        ]

        # Gera superfície de estrelas (uma vez)
        self._star_surf = pygame.Surface((SCREEN_W, SCREEN_H // 2))
        self._star_surf.fill((0, 0, 0))
        self._star_surf.set_colorkey((0, 0, 0))
        draw_stars(self._star_surf, count=150, seed=42)

        self.fx.fade_in(frames=20)
        self._ready = True

    def handle_event(self, event):
        if not self._ready:
            return
        if self.dialogue.active:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_x, pygame.K_k, pygame.K_RETURN, pygame.K_SPACE):
                self.dialogue.advance()
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._paused = not self._paused
            if event.key in (pygame.K_x, pygame.K_k):
                self._try_interact_altar()

    def _try_interact_altar(self):
        pr = self.player.rect
        for altar in self.altars:
            if abs(pr.centerx - altar.rect.centerx) < 30 and abs(pr.centery - altar.rect.centery) < 40:
                if not altar.activated:
                    altar.activate()
                    self._altars_activated += 1
                    self.karma.resolveu_puzzle_perfeito()
                    self.sys_msg.show(f"Altar ativado! ({self._altars_activated}/3)", 90)
                    if self._altars_activated >= 3:
                        self._portal_open = True
                        self.sys_msg.show("A entrada está aberta!", 150)
                return

    def update(self):
        if not self._ready or self._paused:
            return

        self.time += 1

        if not self.dialogue.active:
            self.player.update(self.input.poll(), self.tilemap, self.particles)

        # Inimigos
        for enemy in self.enemies:
            enemy.update(self.tilemap, self.player.rect)

        # Colisão player-inimigo
        for enemy in self.enemies:
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(1):
                    self.fx.camera_shake(4, 12)
                    self.karma.enfrentou_inimigo()

        # Colisão ataque-inimigo
        if self.player.attack_active:
            ar = self.player.attack_rect
            for enemy in self.enemies:
                if enemy.alive and ar.colliderect(enemy.rect):
                    killed = enemy.take_damage(1)
                    if killed:
                        enemy.emit_death_particles(self.particles)
                        self.karma.enfrentou_inimigo()

        self.enemies = [e for e in self.enemies if e.alive]

        # Altares
        for altar in self.altars:
            altar.update(self.particles)

        self.dialogue.update()
        self.sys_msg.update()
        self.particles.update()
        self.fx.update()
        self.hud.update()

        self.camera.update(
            self.player.x + Player.W // 2,
            self.player.y + Player.H // 2
        )

        # Indicador altar
        pr = self.player.rect
        for altar in self.altars:
            if abs(pr.centerx - altar.rect.centerx) < 30 and abs(pr.centery - altar.rect.centery) < 40:
                if not altar.activated:
                    self.hud.show_interaction("examinar altar")
                break

        # Transição para caverna
        if self._portal_open and self.player.x > self.NEXT_SCENE_X - 50:
            if not self._transitioning:
                self._transitioning = True
                self._transition_timer = 25
                self.fx.fade_out(25)

        if self._transitioning:
            self._transition_timer -= 1
            if self._transition_timer <= 0:
                self._transitioning = False
                from scenes.cave_scene import CaveScene
                self.scene_manager.replace(CaveScene(self.scene_manager, self.bus, self.karma, self.input, self.player))

        if self.player.x < 0:
            self.player.x = 0

    def draw(self, surf):
        if not self._ready:
            surf.fill((0, 0, 0))
            return

        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)

        # Céu noturno
        _draw_night_sky(surf, cam_x)
        # Estrelas
        surf.blit(self._star_surf, (0, 0))
        # Lua
        _draw_moon(surf, cam_x)
        # Pedra do Castelo maior
        _draw_pedra_bg_trail(surf, cam_x)

        # Tilemap
        self.tilemap.draw(surf, cam_x, cam_y, SCREEN_W, SCREEN_H)

        # Tochas
        for tx, ty in self.torches:
            _draw_torch(surf, tx, ty, cam_x, cam_y, self.time)

        # Altares
        for altar in self.altars:
            altar.draw(surf, cam_x, cam_y, self.time)

        # Inimigos
        for enemy in self.enemies:
            enemy.draw(surf, cam_x, cam_y)

        # Portal (se aberto)
        if self._portal_open:
            px = self.NEXT_SCENE_X - 16 - cam_x
            py = 12 * TILE_SIZE - cam_y
            t = self.time
            for ring in range(3):
                r = 12 + ring * 6 + int(math.sin(t * 0.1 + ring) * 3)
                alpha = 100 + int(math.sin(t * 0.1) * 50)
                gsurf = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
                pygame.draw.circle(gsurf, (80, 160, 220, alpha), (r+1, r+1), r, 2)
                surf.blit(gsurf, (px - r, py - r))

        # Partículas
        self.particles.draw(surf, cam_x, cam_y)

        # Player
        self.player.draw(surf, cam_x, cam_y)

        # HUD
        self.hud.draw(surf, self.player.hp, self.player.max_hp)
        self.dialogue.draw(surf)
        self.sys_msg.draw(surf)
        self.fx.draw(surf)

        # Indicador "portal à frente"
        if self._portal_open:
            if not hasattr(self, '_pfont'):
                try:
                    self._pfont = pygame.font.SysFont("Courier New", 11)
                except Exception:
                    self._pfont = pygame.font.Font(None, 14)
            pt = self._pfont.render("→ Entrada da Pedra", True, (80, 160, 220))
            surf.blit(pt, (SCREEN_W - pt.get_width() - 8, SCREEN_H // 2))
