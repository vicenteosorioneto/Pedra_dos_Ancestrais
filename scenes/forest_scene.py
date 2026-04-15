# scenes/forest_scene.py — Ato 1, Área 2: Floresta da Pedra (entardecer)
#
# Fluxo: VillageScene → ForestScene → RuinsScene
# Conteúdo:
#   - Plataformas entre árvores com trepadeiras
#   - 3 morcegos (primeiro encontro com inimigos para muitos jogadores)
#   - NPC: Peregrino (aponta para as ruínas e o altar)
#   - 2 Registros ancestrais (lore sobre o caminho sagrado)

import pygame
import math
from settings import (
    SCREEN_W, SCREEN_H, TILE_SIZE, PALETTE_SERTAO as P, BLACK, GOLD
)
from systems.tilemap import Tilemap
from systems.dialogue import DialogueBox, SystemMessage
from systems.hud import HUD
from entities.player import Player
from entities.bat_enemy import BatEnemy
from core.camera import Camera
from art.fx import ParticleSystem, ScreenEffects


# ── Geração do mapa ────────────────────────────────────────────────────────────

def _build_forest_map():
    COLS = 52
    ROWS = 22
    data = [[0] * COLS for _ in range(ROWS)]

    # Chão base
    for col in range(COLS):
        data[16][col] = 1   # pedra_topo
        data[17][col] = 2   # pedra_meio
        data[18][col] = 4   # terra
        data[19][col] = 4
        data[20][col] = 4
        data[21][col] = 4

    # Plataformas de pedra
    platforms = [
        (range(5,  11), 12),
        (range(18, 24), 10),
        (range(30, 36), 12),
        (range(42, 48),  9),
    ]
    for cols, row in platforms:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 1
                if row + 1 < ROWS:
                    data[row + 1][col] = 2

    # Trepadeiras pendendo das plataformas
    for vc in [6, 7, 19, 20, 31, 32, 43, 44]:
        if vc < COLS:
            for vy in range(1, 4):
                row = 14 + vy
                if 0 <= row < ROWS and data[row][vc] == 0:
                    data[row][vc] = 7

    # Grama seca decorativa no chão
    for col in range(2, COLS - 2, 5):
        if data[15][col] == 0:
            data[15][col] = 13

    registro_positions = [(14, 16), (38, 16)]
    return data, COLS, ROWS, registro_positions


# ── Objeto: inscrição ancestral ────────────────────────────────────────────────

class ForestRegistro:
    W = 12
    H = 16

    def __init__(self, x, y, key):
        self.x    = float(x)
        self.y    = float(y)
        self.key  = key
        self.read = False
        self.time = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self):
        self.time += 1

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if not (-20 < sx < SCREEN_W + 20):
            return
        col     = (100, 80, 55) if not self.read else (60, 48, 32)
        col_top = (75, 58, 35)  if not self.read else (48, 36, 22)
        pygame.draw.rect(surf, col,     (sx,   sy + 4, self.W, self.H - 4))
        pygame.draw.rect(surf, col_top, (sx+2, sy,     self.W - 4, 6))
        glyph = (180, 150, 70) if not self.read else (90, 75, 35)
        for row in range(3):
            pygame.draw.line(surf, glyph,
                             (sx + 2, sy + 7 + row * 3),
                             (sx + self.W - 2, sy + 7 + row * 3))
        if not self.read:
            pulse = int(abs(math.sin(self.time * 0.07)) * 55) + 30
            gsurf = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (180, 150, 70, pulse), (11, 11), 11)
            surf.blit(gsurf, (sx - 5, sy - 5))


# ── Funções de fundo ───────────────────────────────────────────────────────────

def _draw_dusk_sky(surf):
    """Céu de entardecer: gradiente roxo-laranja."""
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        if t < 0.5:
            t2 = t / 0.5
            r = int(45  + t2 * 120)
            g = int(15  + t2 * 40)
            b = int(70  + t2 * 20)
        else:
            t2 = (t - 0.5) / 0.5
            r = int(165 + t2 * 60)
            g = int(55  + t2 * 80)
            b = int(90  - t2 * 40)
        pygame.draw.line(surf, (min(255, r), min(255, g), max(0, b)), (0, y), (SCREEN_W, y))


def _draw_forest_layers(surf, cam_x, time):
    """Silhuetas de árvores em 2 camadas de parallax."""
    # Camada traseira — mais clara, velocidade lenta
    for i in range(0, SCREEN_W + 240, 55):
        bx = int((i - cam_x * 0.07) % (SCREEN_W + 240)) - 100
        h  = 100 + (i % 5) * 16
        tw = 5 + (i % 3)
        pygame.draw.rect(surf, (30, 18, 10), (bx + tw // 2 - 2, SCREEN_H - h, 5, h))
        for lv in range(3):
            lw = 32 - lv * 7
            lh = 24 - lv * 4
            lx = bx - lw // 2 + tw // 2
            ly = SCREEN_H - h - 10 - lv * 16
            pygame.draw.ellipse(surf, (22, 45, 22), (lx, ly, lw, lh))

    # Camada dianteira — mais escura, oscila suavemente
    for i in range(0, SCREEN_W + 360, 75):
        bx = int((i * 7 - cam_x * 0.20) % (SCREEN_W + 360)) - 120
        h  = 130 + (i % 6) * 12
        tw = 7 + (i % 4)
        sway = int(math.sin(time * 0.025 + i * 0.08) * 2)
        pygame.draw.rect(surf, (15, 8, 4), (bx + sway, SCREEN_H - h, tw, h))
        for lv in range(4):
            lw = 44 - lv * 8
            lh = 30 - lv * 5
            lx = bx + sway - lw // 2 + tw // 2
            ly = SCREEN_H - h - 14 - lv * 18
            col = (10 + lv * 2, 30 + lv * 2, 12 + lv * 2)
            if lw > 0 and lh > 0:
                pygame.draw.ellipse(surf, col, (lx, ly, lw, lh))


# ── Cena ───────────────────────────────────────────────────────────────────────

class ForestScene:
    WORLD_COLS = 52
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

    def _go_to_menu(self):
        from scenes.intro_scene import IntroScene
        from systems.karma import KarmaSystem
        new_karma = KarmaSystem(self.bus)
        self.scene_manager.replace(IntroScene(self.scene_manager, self.bus, new_karma, self.input))

    def _setup(self):
        map_data, cols, rows, registro_positions = _build_forest_map()
        self.tilemap   = Tilemap(map_data)
        self.camera    = Camera(self.WORLD_W, self.WORLD_H)
        self.particles = ParticleSystem()
        self.fx        = ScreenEffects(SCREEN_W, SCREEN_H)
        self.dialogue  = DialogueBox()
        self.sys_msg   = SystemMessage()
        self.hud       = HUD(self.karma)
        self.hud.set_scene_label("ATO 1 — FLORESTA")
        self.time      = 0
        self._paused   = False
        self._transitioning   = False
        self._transition_timer = 0

        # Player — herda HP se veio de cena anterior
        start_y = 15 * TILE_SIZE - Player.H
        self.player = Player(30, start_y, self.bus)
        if self._prev_player:
            self.player.hp = max(1, self._prev_player.hp)

        # Inimigos
        bat_y = 7 * TILE_SIZE
        self.enemies = [
            BatEnemy(200, bat_y),
            BatEnemy(370, bat_y - 10),
            BatEnemy(560, bat_y + 5),
        ]

        # NPC: Peregrino (usa sprite de ElderNPC para distinção visual)
        from entities.npc import ElderNPC
        ground_y = 15 * TILE_SIZE - Player.H
        self._peregrino = ElderNPC(120, ground_y)
        self._peregrino_talked = False

        # Registros ancestrais
        self.registros = [
            ForestRegistro(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE - 16, f"registro_floresta_{i}")
            for i, pos in enumerate(registro_positions)
        ]

        self.fx.fade_in(frames=22)
        self._ready = True

    # ── Eventos ──────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if not self._ready:
            return
        if self.hud.death_active:
            if event.type == pygame.KEYDOWN:
                if self.hud._showing_controls:
                    if event.key in (pygame.K_c, pygame.K_ESCAPE):
                        self.hud.hide_controls()
                elif self.hud.death_ready_for_input:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.hud.hide_death()
                        self._setup()
                    elif event.key == pygame.K_ESCAPE:
                        self.hud.hide_death()
                        self._go_to_menu()
                    elif event.key == pygame.K_c:
                        self.hud.show_controls()
            return
        if self.dialogue.active:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_x, pygame.K_k, pygame.K_RETURN, pygame.K_SPACE):
                self.dialogue.advance()
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._paused = not self._paused
                self.hud.set_pause(self._paused)
            if event.key == pygame.K_m and self._paused:
                self._paused = False
                self.hud.set_pause(False)
                self._go_to_menu()
            if event.key == pygame.K_RETURN and self._paused:
                self._paused = False
                self.hud.set_pause(False)
            if event.key in (pygame.K_x, pygame.K_k) and not self._paused:
                self._try_interact_npc()
                self._try_interact_registro()

    def _try_interact_npc(self):
        pr  = self.player.rect
        npc = self._peregrino
        if (abs(pr.centerx - npc.rect.centerx) < 50 and
                abs(pr.centery - npc.rect.centery) < 50 and
                not self._peregrino_talked):
            self._peregrino_talked = True
            npc.frozen = True
            self.karma.conversou_com_npc()
            def _unfreeze(n=npc):
                n.frozen = False
            self.dialogue.open("peregrino_floresta", avatar_surf=npc.get_avatar(), on_close=_unfreeze)

    def _try_interact_registro(self):
        pr = self.player.rect
        for registro in self.registros:
            if (abs(pr.centerx - registro.rect.centerx) < 35 and
                    abs(pr.centery - registro.rect.centery) < 45):
                if not registro.read:
                    registro.read = True
                    self.karma.leu_registro()
                    self.dialogue.open(registro.key)
                    self.sys_msg.show("Inscrição ancestral lida.", 80)
                return

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self):
        if not self._ready or self._paused:
            return
        if self.hud.death_active:
            self.hud.update()
            return

        self.time += 1

        if not self.dialogue.active:
            self.player.update(self.input.poll(), self.tilemap, self.particles)

        # NPC
        self._peregrino.update()
        pr  = self.player.rect
        npc = self._peregrino
        if (abs(pr.centerx - npc.rect.centerx) < 50 and
                abs(pr.centery - npc.rect.centery) < 50 and
                not self._peregrino_talked):
            self.hud.show_interaction("conversar com Peregrino")

        # Morcegos
        for enemy in self.enemies:
            enemy.update(self.tilemap, self.player.rect)
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(1):
                    self.fx.camera_shake(4, 12)
                    self.hud.notify_damage()

        if self.player.attack_active:
            ar = self.player.attack_rect
            for enemy in self.enemies:
                if enemy.alive and ar.colliderect(enemy.rect):
                    if enemy.take_damage(1):
                        enemy.emit_death_particles(self.particles)
                        self.karma.enfrentou_inimigo()

        self.enemies = [e for e in self.enemies if e.alive]

        # Registros
        for registro in self.registros:
            registro.update()

        if not self.dialogue.active:
            for registro in self.registros:
                if (abs(pr.centerx - registro.rect.centerx) < 35 and
                        abs(pr.centery - registro.rect.centery) < 45):
                    if not registro.read:
                        self.hud.show_interaction("ler inscrição")
                    break

        self.dialogue.update()
        self.sys_msg.update()
        self.particles.update()
        self.fx.update()
        self.hud.update()

        self.camera.update(
            self.player.x + Player.W // 2,
            self.player.y + Player.H // 2,
        )

        if self.player.dead and not self.hud.death_active:
            self.hud.show_death()

        # Transição → RuinsScene
        if self.player.x > self.NEXT_SCENE_X - 50 and not self._transitioning:
            self._transitioning    = True
            self._transition_timer = 25
            self.fx.fade_out(25)

        if self._transitioning:
            self._transition_timer -= 1
            if self._transition_timer <= 0:
                self._transitioning = False
                from scenes.ruins_scene import RuinsScene
                self.scene_manager.replace(
                    RuinsScene(self.scene_manager, self.bus, self.karma, self.input, self.player)
                )

        if self.player.x < 0:
            self.player.x = 0

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, surf):
        if not self._ready:
            surf.fill((0, 0, 0))
            return

        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)

        _draw_dusk_sky(surf)
        _draw_forest_layers(surf, cam_x, self.time)

        self.tilemap.draw(surf, cam_x, cam_y, SCREEN_W, SCREEN_H)

        self._peregrino.draw(surf, cam_x, cam_y)

        for registro in self.registros:
            registro.draw(surf, cam_x, cam_y)

        for enemy in self.enemies:
            enemy.draw(surf, cam_x, cam_y)

        self.particles.draw(surf, cam_x, cam_y)
        self.player.draw(surf, cam_x, cam_y)

        self.hud.draw(surf, self.player.hp, self.player.max_hp)
        self.dialogue.draw(surf)
        self.sys_msg.draw(surf)
        self.fx.draw(surf)

        # Seta de saída
        if self.player.x > self.WORLD_W - 100:
            if not hasattr(self, '_arrow_font'):
                try:
                    self._arrow_font = pygame.font.SysFont("Courier New", 11)
                except Exception:
                    self._arrow_font = pygame.font.Font(None, 14)
            arr = self._arrow_font.render("→ Ruínas Ancestrais", True, GOLD)
            surf.blit(arr, (SCREEN_W - arr.get_width() - 8, SCREEN_H // 2))
