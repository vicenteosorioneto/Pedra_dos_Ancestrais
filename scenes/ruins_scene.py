# scenes/ruins_scene.py — Ato 1, Área 3: Ruínas Ancestrais
#
# Fluxo: ForestScene → RuinsScene → TrailScene
# Conteúdo:
#   - Zona de contemplação (sem inimigos)
#   - 1 Altar antigo — 1º dos 5 selos do Guardião
#   - 2 Registros (lore sobre Iracema e os altares)
#   - Pôr do sol dramático com silhuetas de ruínas ao fundo

import pygame
import math
from settings import (
    SCREEN_W, SCREEN_H, TILE_SIZE, PALETTE_SERTAO as P, BLACK, GOLD
)
from systems.tilemap import Tilemap
from systems.dialogue import DialogueBox, SystemMessage
from systems.hud import HUD
from entities.player import Player
from core.camera import Camera
from art.fx import ParticleSystem, ScreenEffects


# ── Geração do mapa ────────────────────────────────────────────────────────────

def _build_ruins_map():
    COLS = 55
    ROWS = 22
    data = [[0] * COLS for _ in range(ROWS)]

    # Chão base — pedra de castelo (mais antiga que pedra comum)
    for col in range(COLS):
        data[16][col] = 8   # pedra_castelo
        data[17][col] = 8
        data[18][col] = 3   # pedra_base
        data[19][col] = 4   # terra
        data[20][col] = 4
        data[21][col] = 4

    # Plataformas de ruínas (alturas escalonadas)
    platforms = [
        (range(7,  15), 13),
        (range(22, 28), 11),
        (range(34, 42), 12),
        (range(46, 52),  9),
    ]
    for cols, row in platforms:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 8
                if row + 1 < ROWS:
                    data[row + 1][col] = 8

    # Pilares verticais de ruínas (colunas quebradas)
    for col in [5, 6, 18, 19, 31, 32, 43, 44]:
        if col < COLS:
            top = 7 if col in [5, 31] else 9   # pilares quebrados em alturas distintas
            for row in range(top, 16):
                if data[row][col] == 0:
                    data[row][col] = 8

    registro_positions = [(11, 16), (37, 16)]
    altar_pos = (26, 16)   # coluna, linha do chão

    return data, COLS, ROWS, registro_positions, altar_pos


# ── Objeto: inscrição das ruínas ──────────────────────────────────────────────

class RuinsRegistro:
    """Inscrição de pedra das ruínas — visual mais antigo e desgastado."""
    W = 14
    H = 18

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
        col     = (90, 70, 45) if not self.read else (55, 42, 28)
        col_top = (70, 52, 32) if not self.read else (44, 33, 21)
        pygame.draw.rect(surf, col,     (sx,   sy + 5, self.W, self.H - 5))
        pygame.draw.rect(surf, col_top, (sx+2, sy,     self.W - 4, 7))
        glyph = (160, 120, 50) if not self.read else (80, 60, 25)
        # Espiral de 3 anéis concêntricos
        cx_s, cy_s = sx + 7, sy + 11
        for r in range(3, 7, 2):
            pygame.draw.circle(surf, glyph, (cx_s, cy_s), r, 1)
        # Linhas horizontais de texto antigo
        for row in range(2):
            pygame.draw.line(surf, glyph,
                             (sx + 2, sy + 7 + row * 4),
                             (sx + self.W - 2, sy + 7 + row * 4))
        if not self.read:
            pulse = int(abs(math.sin(self.time * 0.06)) * 70) + 20
            gsurf = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (180, 130, 50, pulse), (14, 14), 14)
            surf.blit(gsurf, (sx - 7, sy - 5))


# ── Objeto: altar antigo ───────────────────────────────────────────────────────

class RuinsAltar:
    """Altar das Ruínas — 1º dos 5 selos que aprisionam o Guardião."""

    VISUAL_H = 22   # altura visual total (usado para posicionar no chão)

    def __init__(self, x, y):
        self.x          = float(x)
        self.y          = float(y)
        self.activated  = False
        self.time       = 0

    @property
    def rect(self):
        """Hitbox de interação (generosa)."""
        return pygame.Rect(int(self.x) - 14, int(self.y), 32, self.VISUAL_H)

    def activate(self):
        self.activated = True

    def update(self, particle_sys):
        self.time += 1
        if self.activated and self.time % 5 == 0:
            particle_sys.emit_altar(int(self.x), int(self.y))

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if not (-50 < sx < SCREEN_W + 50):
            return

        t = self.time
        active = self.activated

        stone   = (90, 70, 45)
        dark    = (50, 35, 15)
        lit     = (200, 150, 40) if active else (80, 60, 35)
        glyph_c = (240, 195, 55) if active else (110, 85, 38)

        # Base larga
        pygame.draw.rect(surf, dark,  (sx - 14, sy + 14, 32, 8))
        pygame.draw.rect(surf, stone, (sx - 12, sy + 12, 28, 4))
        # Pedestal
        pygame.draw.rect(surf, stone, (sx - 8,  sy + 4,  20, 10))
        pygame.draw.rect(surf, dark,  (sx - 8,  sy + 4,  20, 10), 1)
        # Topo
        pygame.draw.rect(surf, lit,   (sx - 5,  sy,      14, 6))
        pygame.draw.rect(surf, dark,  (sx - 5,  sy,      14, 6), 1)

        # Símbolo de 5 pontos (pentagrama simplificado)
        cx_s, cy_s = sx + 2, sy + 3
        for angle in range(0, 360, 72):
            rad = math.radians(angle)
            px = cx_s + int(math.cos(rad) * 4)
            py = cy_s + int(math.sin(rad) * 4)
            if 0 <= px < SCREEN_W and 0 <= py < SCREEN_H:
                surf.set_at((px, py), glyph_c)
        if 0 <= cx_s < SCREEN_W and 0 <= cy_s < SCREEN_H:
            surf.set_at((cx_s, cy_s), glyph_c)

        # Aura pulsante quando ativo
        if active:
            alpha = 60 + int(math.sin(t * 0.10) * 45)
            asurf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(asurf, (200, 150, 40, alpha), (25, 25), 25)
            surf.blit(asurf, (sx - 23, sy - 23))


# ── Funções de fundo ───────────────────────────────────────────────────────────

def _draw_sunset_sky(surf):
    """Pôr do sol dramático — laranja → roxo-escuro."""
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        if t < 0.3:
            t2 = t / 0.3
            r = int(80  + t2 * 160)
            g = int(30  + t2 * 70)
            b = int(80  + t2 * 10)
        elif t < 0.65:
            t2 = (t - 0.3) / 0.35
            r = int(240 - t2 * 60)
            g = int(100 + t2 * 50)
            b = int(90  - t2 * 50)
        else:
            t2 = (t - 0.65) / 0.35
            r = int(180 - t2 * 80)
            g = int(150 - t2 * 90)
            b = int(40  + t2 * 20)
        pygame.draw.line(surf, (min(255, r), min(255, g), max(0, b)), (0, y), (SCREEN_W, y))


def _draw_ruins_bg(surf, cam_x):
    """Silhuetas de colunas e vigas de ruínas ao fundo (parallax lento)."""
    offset = int(cam_x * 0.10)
    col    = (38, 26, 14)
    cap_c  = (52, 36, 20)

    for i in range(0, SCREEN_W + 500, 90):
        bx = int((i - offset) % (SCREEN_W + 500)) - 100
        h  = 75 + (i % 5) * 18
        w  = 9 + (i % 3) * 2
        # Fuste da coluna
        pygame.draw.rect(surf, col, (bx, SCREEN_H - h, w, h))
        # Capitel (topo ornamentado)
        pygame.draw.rect(surf, cap_c, (bx - 4, SCREEN_H - h - 7, w + 8, 7))
        # Detalhe de fratura (coluna parcialmente quebrada)
        if i % 180 == 0:
            frac_y = SCREEN_H - h + h // 3
            pygame.draw.line(surf, cap_c, (bx, frac_y), (bx + w, frac_y + 5), 2)

    # Vigas horizontais entre colunas (algumas caídas)
    for i in range(0, SCREEN_W + 600, 180):
        bx = int((i * 2 - offset) % (SCREEN_W + 600)) - 80
        by = SCREEN_H - 120 - (i % 4) * 15
        # Viga horizontal (lintel)
        pygame.draw.rect(surf, col, (bx, by, 80, 8))
        pygame.draw.rect(surf, cap_c, (bx, by, 80, 3))


# ── Cena ───────────────────────────────────────────────────────────────────────

class RuinsScene:
    WORLD_COLS = 55
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
        map_data, cols, rows, registro_positions, altar_pos = _build_ruins_map()
        self.tilemap   = Tilemap(map_data)
        self.camera    = Camera(self.WORLD_W, self.WORLD_H)
        self.particles = ParticleSystem()
        self.fx        = ScreenEffects(SCREEN_W, SCREEN_H)
        self.dialogue  = DialogueBox()
        self.sys_msg   = SystemMessage()
        self.hud       = HUD(self.karma)
        self.hud.set_scene_label("ATO 1 — RUÍNAS")
        self.time      = 0
        self._paused   = False
        self._transitioning   = False
        self._transition_timer = 0
        self._altar_hint_shown = False

        # Player
        start_y = 15 * TILE_SIZE - Player.H
        self.player = Player(30, start_y, self.bus)
        if self._prev_player:
            self.player.hp = max(1, self._prev_player.hp)

        # Altar central — posicionado rente ao chão
        floor_y = altar_pos[1] * TILE_SIZE   # y do tile do chão
        altar_x = altar_pos[0] * TILE_SIZE
        altar_y = floor_y - RuinsAltar.VISUAL_H
        self.altar          = RuinsAltar(altar_x, altar_y)
        self._altar_done    = False

        # Registros
        self.registros = [
            RuinsRegistro(
                pos[0] * TILE_SIZE,
                pos[1] * TILE_SIZE - 18,
                f"registro_ruinas_{i}",
            )
            for i, pos in enumerate(registro_positions)
        ]

        self.fx.fade_in(frames=28)
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
                self._try_interact_altar()
                self._try_interact_registro()

    def _try_interact_altar(self):
        if self._altar_done:
            return
        pr = self.player.rect
        if pr.inflate(40, 40).colliderect(self.altar.rect):
            self._altar_done = True
            self.altar.activate()
            self.karma.resolveu_puzzle_perfeito()
            self.particles.emit_phase_burst(int(self.altar.x), int(self.altar.y))
            self.fx.camera_shake(4, 14)
            self.sys_msg.show("O primeiro selo desperta...", 160)
            self.dialogue.open("altar_ruinas", on_close=self._on_altar_close)

    def _on_altar_close(self):
        self.sys_msg.show("Quatro altares restam. Siga a trilha à frente.", 200)

    def _try_interact_registro(self):
        pr = self.player.rect
        for registro in self.registros:
            if (abs(pr.centerx - registro.rect.centerx) < 35 and
                    abs(pr.centery - registro.rect.centery) < 45):
                if not registro.read:
                    registro.read = True
                    self.karma.leu_registro()
                    self.dialogue.open(registro.key)
                    self.sys_msg.show("Inscrição antiga lida.", 80)
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

        pr = self.player.rect

        # Altar
        self.altar.update(self.particles)

        # Hint do altar ao entrar na área central
        if not self._altar_hint_shown and self.player.x > 200:
            self._altar_hint_shown = True
            self.sys_msg.show("Ruínas Ancestrais — [X] para interagir com o altar", 220)

        # Indicadores de interação
        if not self.dialogue.active:
            if not self._altar_done and pr.inflate(40, 40).colliderect(self.altar.rect):
                self.hud.show_interaction("ativar altar antigo")
            else:
                for registro in self.registros:
                    if (abs(pr.centerx - registro.rect.centerx) < 35 and
                            abs(pr.centery - registro.rect.centery) < 45):
                        if not registro.read:
                            self.hud.show_interaction("ler inscrição")
                        break

        for registro in self.registros:
            registro.update()

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

        # Transição → TrailScene
        if self.player.x > self.NEXT_SCENE_X - 50 and not self._transitioning:
            self._transitioning    = True
            self._transition_timer = 25
            self.fx.fade_out(25)

        if self._transitioning:
            self._transition_timer -= 1
            if self._transition_timer <= 0:
                self._transitioning = False
                from scenes.trail_scene import TrailScene
                self.scene_manager.replace(
                    TrailScene(self.scene_manager, self.bus, self.karma, self.input, self.player)
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

        _draw_sunset_sky(surf)
        _draw_ruins_bg(surf, cam_x)

        self.tilemap.draw(surf, cam_x, cam_y, SCREEN_W, SCREEN_H)

        self.altar.draw(surf, cam_x, cam_y)

        for registro in self.registros:
            registro.draw(surf, cam_x, cam_y)

        self.particles.draw(surf, cam_x, cam_y)
        self.player.draw(surf, cam_x, cam_y)

        self.hud.draw(surf, self.player.hp, self.player.max_hp)
        self.dialogue.draw(surf)
        self.sys_msg.draw(surf)
        self.fx.draw(surf)

        # Seta de saída (aparece sempre que o altar foi ativado ou chegou perto do fim)
        if self.player.x > self.WORLD_W - 120:
            if not hasattr(self, '_arrow_font'):
                try:
                    self._arrow_font = pygame.font.SysFont("Courier New", 11)
                except Exception:
                    self._arrow_font = pygame.font.Font(None, 14)
            arr = self._arrow_font.render("→ Trilha da Pedra", True, GOLD)
            surf.blit(arr, (SCREEN_W - arr.get_width() - 8, SCREEN_H // 2))
