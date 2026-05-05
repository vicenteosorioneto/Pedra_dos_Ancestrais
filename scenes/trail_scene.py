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
from systems.rewards import RewardPickup, draw_rewards, update_rewards
from entities.player import Player
from entities.bat_enemy import BatEnemy
from core.camera import Camera
from art.fx import ParticleSystem, ScreenEffects, draw_stars


def _build_trail_map():
    COLS = 92
    ROWS = 22
    data = [[0] * COLS for _ in range(ROWS)]

    # Chão base
    for col in range(COLS):
        data[17][col] = 1
        data[18][col] = 2
        data[19][col] = 3
        data[20][col] = 3
        data[21][col] = 3

    # Degraus subindo da esquerda para direita (trilha mais longa)
    steps = [
        (2,  15, range(16, 26)),
        (3,  14, range(36, 46)),
        (4,  13, range(60, 70)),
    ]
    for dy, row, cols in steps:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 8   # pedra_castelo
                for y in range(row+1, min(row+3, ROWS)):
                    data[y][col] = 2

    # Reabre a faixa de caminhada depois dos blocos decorativos.
    for col in range(COLS):
        data[16][col] = 0
        data[17][col] = 1
        data[18][col] = 2
        data[19][col] = 3
        data[20][col] = 3
        data[21][col] = 3

    # Plataformas flutuantes com pedra de castelo
    platforms = [
        (range(12, 18), 13),
        (range(22, 28), 11),
        (range(35, 41), 12),
        (range(46, 52), 10),
        (range(58, 64), 9),
        (range(68, 74), 8),
        (range(78, 84), 7),
    ]
    for cols, row in platforms:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 8

    # 5 altares espalhados pela trilha
    altar_positions = [(15, 17), (30, 17), (47, 17), (63, 17), (79, 17)]

    # 3 inscrições de pedra (registros) ao longo da trilha
    registro_positions = [(22, 17), (52, 17), (71, 17)]

    # Parede de bloqueio no fim da trilha (toda a altura)
    WALL_COLS = range(86, 90)
    for col in WALL_COLS:
        for row in range(0, ROWS):
            data[row][col] = 8   # pedra_castelo — sólido

    for col in WALL_COLS:
        for row in range(0, ROWS):
            data[row][col] = 0
        data[17][col] = 1
        data[18][col] = 2
        data[19][col] = 3
        data[20][col] = 3
        data[21][col] = 3

    return data, COLS, ROWS, altar_positions, registro_positions, list(WALL_COLS)


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
    cx = SCREEN_W // 2 - offset % (SCREEN_W + 300)
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


class Registro:
    """Inscrição de pedra — leitura concede sabedoria (karma.leu_registro)."""
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
        col     = (120, 100, 70) if not self.read else (70, 55, 38)
        col_top = (90, 70, 45)   if not self.read else (55, 40, 25)
        # Base da placa
        pygame.draw.rect(surf, col,     (sx,   sy + 4, self.W, self.H - 4))
        pygame.draw.rect(surf, col_top, (sx+2, sy,     self.W - 4, 6))
        # Linhas gravadas (texto antigo)
        glyph = (200, 170, 80) if not self.read else (100, 85, 40)
        for row in range(3):
            pygame.draw.line(surf, glyph,
                             (sx + 2, sy + 7 + row * 3),
                             (sx + self.W - 2, sy + 7 + row * 3))
        # Brilho pulsante se não lido
        if not self.read:
            pulse = int(abs(math.sin(self.time * 0.07)) * 55) + 30
            gsurf = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (220, 180, 40, pulse), (11, 11), 11)
            surf.blit(gsurf, (sx - 5, sy - 5))


class TrailScene:
    WORLD_COLS = 92
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
        map_data, cols, rows, altar_positions, registro_positions, wall_cols = _build_trail_map()
        self.tilemap   = Tilemap(map_data)
        self.camera    = Camera(self.WORLD_W, self.WORLD_H)
        self.particles = ParticleSystem()
        self.fx        = ScreenEffects(SCREEN_W, SCREEN_H)
        self.dialogue  = DialogueBox()
        self.sys_msg   = SystemMessage()
        self.hud       = HUD(self.karma)
        self.hud.set_scene_label("ATO 2 — TRILHA")
        self.hud.set_altar_progress(0, total=5)
        self.time      = 0
        self._paused   = False
        self._transitioning = False
        self._transition_timer = 0

        # Reutiliza HP do player anterior
        start_y = 17 * TILE_SIZE - Player.H
        self.player = Player(30, start_y, self.bus)
        if self._prev_player:
            self.player.hp = max(1, self._prev_player.hp)

        # Inimigos: 8 morcegos espalhados pela trilha mais longa
        bat_y = 10 * TILE_SIZE
        self.enemies = [
            BatEnemy(200, bat_y),
            BatEnemy(320, bat_y - 15),
            BatEnemy(450, bat_y + 10),
            BatEnemy(560, bat_y - 20),
            BatEnemy(680, bat_y, faster=True),
            BatEnemy(780, bat_y - 10),
            BatEnemy(900, bat_y + 5, faster=True),
            BatEnemy(1050, bat_y - 15, faster=True),
        ]

        # NPC - Velho da Pedra (conta a história dos altares)
        from entities.npc import ElderNPC
        self._velho = ElderNPC(80, start_y)
        self._velho_talked = False

        # 5 altares pela trilha
        self.altars = [
            Altar(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE - 16)
            for pos in altar_positions
        ]
        self._altars_activated = 0
        self._portal_open      = False
        self._wall_cols        = wall_cols
        self._wall_hint_shown  = False

        # 3 inscrições de pedra (registros)
        self.registros = [
            Registro(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE - 16, f"registro_{i}")
            for i, pos in enumerate(registro_positions)
        ]

        self.rewards = [
            RewardPickup(24 * TILE_SIZE, 17 * TILE_SIZE - 14, "heart", "Luz da trilha: +1 vida"),
            RewardPickup(59 * TILE_SIZE, 17 * TILE_SIZE - 14, "heart", "Luz da trilha: +1 vida"),
            RewardPickup(80 * TILE_SIZE, 17 * TILE_SIZE - 14, "wisdom", "Fragmento ancestral: sabedoria +1"),
        ]

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
        # Tela de morte — aceita ENTER, ESC e C
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
            if event.key in (pygame.K_x, pygame.K_k):
                self._try_interact_npc()
                self._try_interact_altar()
                self._try_interact_registro()

    def _try_interact_npc(self):
        pr = self.player.rect
        if hasattr(self, '_velho') and not self._velho_talked:
            npc = self._velho
            if abs(pr.centerx - npc.rect.centerx) < 50 and abs(pr.centery - npc.rect.centery) < 50:
                self._velho_talked = True
                self.karma.conversou_com_npc()
                self.dialogue.open("velho_da_pedra", avatar_surf=npc.get_avatar())
                return

    def _try_interact_altar(self):
        pr = self.player.rect
        for i, altar in enumerate(self.altars):
            if abs(pr.centerx - altar.rect.centerx) < 30 and abs(pr.centery - altar.rect.centery) < 40:
                if not altar.activated:
                    altar.activate()
                    self._altars_activated += 1
                    self.karma.resolveu_puzzle_perfeito()
                    self.particles.emit_phase_burst(int(altar.x) + 7, int(altar.y))
                    altar_key = f"altar_{self._altars_activated - 1}"
                    self.dialogue.open(altar_key)
                    self.sys_msg.show(f"Altar {self._altars_activated} de 5 aceso!", 90)
                    if self._altars_activated >= 5:
                        self._open_portal()
                return

    def _try_interact_registro(self):
        pr = self.player.rect
        for registro in self.registros:
            if abs(pr.centerx - registro.rect.centerx) < 35 and abs(pr.centery - registro.rect.centery) < 45:
                if not registro.read:
                    registro.read = True
                    self.karma.leu_registro()
                    self.dialogue.open(registro.key)
                    self.sys_msg.show("Inscrição antiga lida.", 80)
                return

    def _open_portal(self):
        """Remove a parede de bloqueio e abre o portal."""
        self._portal_open = True
        # Apaga os tiles da parede no tilemap
        for col in self._wall_cols:
            for row in range(self.WORLD_ROWS):
                self.tilemap.set_tile(col, row, 0)
            self.tilemap.set_tile(col, 17, 1)
            self.tilemap.set_tile(col, 18, 2)
            self.tilemap.set_tile(col, 19, 3)
            self.tilemap.set_tile(col, 20, 3)
            self.tilemap.set_tile(col, 21, 3)
        # Burst de luz no local da parede
        wall_x = self._wall_cols[0] * TILE_SIZE
        wall_y = 15 * TILE_SIZE
        self.particles.emit_boss_death(wall_x, wall_y)
        self.fx.camera_shake(5, 15)
        self.sys_msg.show("A entrada está aberta!", 180)

    def _go_to_menu(self):
        from scenes.intro_scene import IntroScene
        from systems.karma import KarmaSystem
        new_karma = KarmaSystem(self.bus)
        self.scene_manager.replace(IntroScene(self.scene_manager, self.bus, new_karma, self.input))

    def update(self):
        if not self._ready or self._paused:
            return
        if self.hud.death_active:
            self.hud.update()
            return

        self.time += 1

        if not self.dialogue.active:
            self.player.update(self.input.poll(), self.tilemap, self.particles)

        # Inimigos
        if hasattr(self, '_velho'):
            self._velho.update()
            pr = self.player.rect
            npc = self._velho
            if abs(pr.centerx - npc.rect.centerx) < 50 and abs(pr.centery - npc.rect.centery) < 50 and not self._velho_talked:
                self.hud.show_interaction("conversar")

        for enemy in self.enemies:
            enemy.update(self.tilemap, self.player.rect)

        # Colisão player-inimigo (sem karma — karma só ao derrotar)
        for enemy in self.enemies:
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(1):
                    self.fx.camera_shake(4, 12)
                    self.hud.notify_damage()

        # Colisão ataque-inimigo (karma apenas ao matar)
        if self.player.attack_active:
            ar = self.player.attack_rect
            for enemy in self.enemies:
                if enemy.alive and ar.colliderect(enemy.rect):
                    if enemy.take_damage(1):
                        enemy.emit_death_particles(self.particles)
                        self.karma.enfrentou_inimigo()

        self.enemies = [e for e in self.enemies if e.alive]

        # Altares
        for altar in self.altars:
            altar.update(self.particles)

        # Registros
        for registro in self.registros:
            registro.update()

        update_rewards(self.rewards, self.player, self.particles, self.sys_msg, self.karma, self.bus)

        self.dialogue.update()
        self.sys_msg.update()
        self.particles.update()
        self.fx.update()
        self.hud.set_altar_progress(self._altars_activated, total=5)
        self.hud.update()

        self.camera.update(
            self.player.x + Player.W // 2,
            self.player.y + Player.H // 2
        )

        # Indicador altar — mostra número do altar
        pr = self.player.rect
        interaction_shown = False
        for i, altar in enumerate(self.altars):
            if abs(pr.centerx - altar.rect.centerx) < 30 and abs(pr.centery - altar.rect.centery) < 40:
                if not altar.activated:
                    self.hud.show_interaction(f"ativar altar {i + 1}")
                    interaction_shown = True
                break

        # Indicador registro
        if not interaction_shown:
            for registro in self.registros:
                if abs(pr.centerx - registro.rect.centerx) < 35 and abs(pr.centery - registro.rect.centery) < 45:
                    if not registro.read:
                        self.hud.show_interaction("ler inscrição")
                    break

        # Hint quando player toca a parede sem ter os altares todos
        wall_x = self._wall_cols[0] * TILE_SIZE
        if (not self._portal_open
                and not self._wall_hint_shown
                and self.player.x > wall_x - 40):
            self._wall_hint_shown = True
            self.sys_msg.show("Ative os 5 altares para abrir o caminho.", 180)

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

        if self.player.dead and not self.hud.death_active:
            self.hud.show_death()

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

        # Registros
        for registro in self.registros:
            registro.draw(surf, cam_x, cam_y)

        draw_rewards(self.rewards, surf, cam_x, cam_y)

        # NPC Velho
        if hasattr(self, '_velho'):
            self._velho.draw(surf, cam_x, cam_y)

        # Inimigos
        for enemy in self.enemies:
            enemy.draw(surf, cam_x, cam_y)

        # Portal no fim da trilha
        px = self.NEXT_SCENE_X - 16 - cam_x
        py = 15 * TILE_SIZE - cam_y
        t = self.time
        portal_col = (80, 160, 220) if self._portal_open else (90, 70, 120)
        for ring in range(3):
            r = 12 + ring * 6 + int(math.sin(t * 0.1 + ring) * 3)
            alpha = (100 + int(math.sin(t * 0.1) * 50)) if self._portal_open else 55
            gsurf = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (*portal_col, alpha), (r+1, r+1), r, 2)
            surf.blit(gsurf, (px - r, py - r))
        if not self._portal_open:
            pygame.draw.line(surf, (150, 110, 170), (px - 16, py), (px + 16, py), 1)
            pygame.draw.line(surf, (150, 110, 170), (px, py - 16), (px, py + 16), 1)

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
