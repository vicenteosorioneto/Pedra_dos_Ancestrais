# scenes/village_scene.py — Ato 1: Vila externa

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
from entities.npc import VillagerNPC, ElderNPC, ComercianteNPC, CriancaNPC, MoradorMedoNPC
from core.camera import Camera
from art.fx import ParticleSystem, ScreenEffects


# ── Geração do tilemap da vila ─────────────────────────────────────────────────

def _build_village_map():
    """
    78 colunas x 22 linhas
    Tile IDs: 0=ar, 1=pedra_topo, 2=pedra_meio, 3=pedra_base,
              4=terra, 5=cacto_base, 6=cacto_topo, 7=trepadeira,
              8=pedra_castelo, 13=grama_seca, 14=pote, 15=caixote
    """
    COLS = 78
    ROWS = 22
    data = [[0] * COLS for _ in range(ROWS)]

    # Chão principal: linhas 14-21
    for col in range(COLS):
        data[14][col] = 1   # topo
        data[15][col] = 2   # meio
        data[16][col] = 2
        data[17][col] = 3   # base
        data[18][col] = 3
        data[19][col] = 4   # terra
        data[20][col] = 4
        data[21][col] = 4

    # Plataformas flutuantes
    def platform(cols_range, row, top=1, mid=2, base=3, height=2):
        for c in cols_range:
            data[row][c] = top
            for dy in range(1, height+1):
                if row + dy < ROWS:
                    data[row+dy][c] = mid if dy < height else base

    platform(range(8, 13),  10)
    platform(range(18, 22),  8)
    platform(range(28, 34), 11)
    platform(range(42, 47),  9)
    platform(range(52, 57), 12)
    platform(range(62, 67), 10)   # plataforma extra
    platform(range(70, 75), 11)   # plataforma extra

    # Cactos (no chão, y=13)
    for cx in [5, 15, 24, 37, 48, 60, 72]:
        if cx < COLS:
            data[13][cx] = 6   # topo cacto
            data[14][cx] = 5   # base cacto

    # Potes
    for px in [3, 20, 45, 65]:
        if px < COLS:
            data[13][px] = 14  # pote sobre o chão

    # Caixotes
    for bx in [35, 50, 68]:
        if bx < COLS:
            data[13][bx] = 15

    # Trepadeiras pendendo de plataformas
    vine_cols = [9, 10, 29, 30, 43, 53, 63, 71]
    for vc in vine_cols:
        if vc < COLS:
            for vy in range(1, 4):
                row = 11 + vy
                if 0 <= row < ROWS and data[row][vc] == 0:
                    data[row][vc] = 7

    return data, COLS, ROWS


# ── Fundo parallax ────────────────────────────────────────────────────────────

def _draw_sky(surf, cam_x, world_w):
    """Gradiente de céu do sertão."""
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        if t < 0.4:
            t2 = t / 0.4
            r = int(80  + t2 * (220 - 80))
            g = int(20  + t2 * (80  - 20))
            b = int(20  + t2 * (40  - 20))
        else:
            t2 = (t - 0.4) / 0.6
            r = int(220 + t2 * (255 - 220))
            g = int(80  + t2 * (200 - 80))
            b = int(40  + t2 * (80  - 40))
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))


def _draw_sun(surf, cam_x):
    offset = int(cam_x * 0.05)
    sx = SCREEN_W - 80 - offset % SCREEN_W
    sy = 30
    # Raios de sol
    sun_c = P["sun"]
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ex = sx + int(math.cos(rad) * 20)
        ey = sy + int(math.sin(rad) * 20)
        pygame.draw.line(surf, (255, 220, 100), (sx, sy), (ex, ey), 1)
    pygame.draw.circle(surf, sun_c, (sx, sy), 12)
    pygame.draw.circle(surf, (255, 255, 200), (sx, sy), 8)


def _draw_pedra_bg(surf, cam_x):
    """Pedra do Castelo no layer de parallax (layer 1, vel 0.15)."""
    offset = int(cam_x * 0.15)
    cx = SCREEN_W // 2 + 60 - offset % (SCREEN_W + 200)
    cy = SCREEN_H - 130
    _draw_pedra_bg_art(surf, cx, cy, scale=0.7)


def _draw_pedra_bg_art(surf, cx, cy, scale=1.0):
    """Versão menor da Pedra para o fundo."""
    s = scale
    rock_mid  = P["rock_mid"]
    rock_dark = P["rock_dark"]
    rock_light= P["rock_light"]

    def sc(v):
        return int(v * s)

    # Coluna central
    pygame.draw.rect(surf, rock_dark, (cx - sc(15), cy - sc(60), sc(30), sc(120)))
    pygame.draw.rect(surf, rock_mid,  (cx - sc(13), cy - sc(60), sc(26), sc(120)))
    # Ameias
    for i in range(-12, 14, 8):
        pygame.draw.rect(surf, rock_dark, (cx + sc(i) - sc(3), cy - sc(70), sc(5), sc(12)))

    # Coluna esquerda
    pygame.draw.rect(surf, rock_dark, (cx - sc(42), cy - sc(35), sc(22), sc(95)))
    pygame.draw.rect(surf, rock_mid,  (cx - sc(40), cy - sc(35), sc(18), sc(95)))
    for i in range(-40, -17, 8):
        pygame.draw.rect(surf, rock_dark, (cx + sc(i), cy - sc(43), sc(5), sc(10)))

    # Coluna direita
    pygame.draw.rect(surf, rock_dark, (cx + sc(20), cy - sc(20), sc(20), sc(80)))
    pygame.draw.rect(surf, rock_mid,  (cx + sc(22), cy - sc(20), sc(16), sc(80)))
    for i in range(20, 40, 8):
        pygame.draw.rect(surf, rock_dark, (cx + sc(i), cy - sc(28), sc(5), sc(10)))

    # Janelas/buracos
    for jx, jy, jw, jh in [
        (cx - sc(7),  cy - sc(45), sc(6),  sc(9)),
        (cx - sc(5),  cy - sc(20), sc(5),  sc(7)),
        (cx - sc(33), cy - sc(18), sc(5),  sc(7)),
        (cx + sc(25), cy - sc(8),  sc(4),  sc(6)),
    ]:
        pygame.draw.rect(surf, (10, 5, 20), (jx, jy, max(3, jw), max(3, jh)))

    # Base
    base_pts = [
        (cx - sc(50), cy + sc(60)), (cx - sc(40), cy + sc(55)),
        (cx,          cy + sc(60)), (cx + sc(40), cy + sc(57)),
        (cx + sc(50), cy + sc(60)), (cx + sc(50), cy + sc(75)),
        (cx - sc(50), cy + sc(75)),
    ]
    pygame.draw.polygon(surf, rock_dark, base_pts)


def _draw_mountains(surf, cam_x):
    """Montanhas distantes (layer 2, vel 0.30)."""
    offset = int(cam_x * 0.30)
    col = P["rock_dark"]
    # Silhueta montanhas
    for mx in range(0, SCREEN_W + 200, 80):
        bx = (mx - offset) % (SCREEN_W + 200) - 100
        h  = 40 + (mx % 5) * 10
        pts = [(bx, SCREEN_H - 60), (bx + 40, SCREEN_H - 60 - h), (bx + 80, SCREEN_H - 60)]
        pygame.draw.polygon(surf, col, pts)


def _draw_hills(surf, cam_x):
    """Colinas próximas (layer 3, vel 0.55)."""
    offset = int(cam_x * 0.55)
    col = P["soil"]
    for mx in range(0, SCREEN_W + 400, 120):
        bx = (mx - offset) % (SCREEN_W + 400) - 200
        h  = 20 + (mx % 4) * 8
        pts = [(bx, SCREEN_H - 10), (bx + 60, SCREEN_H - 10 - h), (bx + 120, SCREEN_H - 10)]
        pygame.draw.polygon(surf, col, pts)


# ── Cena principal ────────────────────────────────────────────────────────────

class VillageScene:
    WORLD_COLS = 78
    WORLD_ROWS = 22
    WORLD_W    = WORLD_COLS * TILE_SIZE  # 1248
    WORLD_H    = WORLD_ROWS * TILE_SIZE  # 352

    NEXT_SCENE_X = (WORLD_COLS - 2) * TILE_SIZE  # saída à direita

    def __init__(self, scene_manager, bus, karma, input_manager):
        self.scene_manager = scene_manager
        self.bus           = bus
        self.karma         = karma
        self.input         = input_manager
        self._ready        = False

    def on_enter(self):
        self._ready = False
        self._setup()

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def _setup(self):
        map_data, cols, rows = _build_village_map()
        self.tilemap  = Tilemap(map_data)
        self.camera   = Camera(self.WORLD_W, self.WORLD_H)
        self.player   = Player(60, 190, self.bus)  # começa à esquerda
        self.particles= ParticleSystem()
        self.fx       = ScreenEffects(SCREEN_W, SCREEN_H)
        self.dialogue = DialogueBox()
        self.sys_msg  = SystemMessage()
        self.hud      = HUD(self.karma)
        self.hud.set_scene_label("ATO 1 — VILA")

        # NPCs — estrutura única evita bug de desincronização de índices
        ground_y = 14 * TILE_SIZE - Player.H
        self._npc_slots = [
            {"npc": VillagerNPC(120, ground_y, variant=0, patrol_range=40),
             "key": "aldeao_0",    "name": "Aldeão",          "talked": False},
            {"npc": CriancaNPC(300, ground_y),
             "key": "crianca",     "name": "Criança",         "talked": False},
            {"npc": VillagerNPC(420, ground_y, variant=1, patrol_range=0),
             "key": "aldeao_2",    "name": "Aldeão",          "talked": False},
            {"npc": ElderNPC(560, ground_y),
             "key": "zequinha",    "name": "Seu Zequinha",    "talked": False},
            {"npc": VillagerNPC(620, ground_y, variant=2, patrol_range=0),
             "key": "aldeao_2",    "name": "Aldeão",          "talked": False},
            {"npc": ComercianteNPC(740, ground_y),
             "key": "comerciante", "name": "Comerciante",     "talked": False},
            {"npc": MoradorMedoNPC(920, ground_y),
             "key": "morador_medo","name": "Morador",         "talked": False},
        ]
        self._zequinha_disappeared = False
        self._transitioning        = False
        self._transition_timer     = 0

        self._paused = False
        self._ready  = True

        # Fade in
        self.fx.fade_in(frames=20)

    def handle_event(self, event):
        if not self._ready:
            return

        # Tela de morte — só aceita ENTER e ESC
        if self.hud.death_active:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.hud.death_ready_for_input:
                    self.hud.hide_death()
                    self._setup()
                elif event.key == pygame.K_ESCAPE and self.hud.death_ready_for_input:
                    self.hud.hide_death()
                    self._go_to_menu()
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
            if event.key in (pygame.K_RETURN,) and self._paused:
                self._paused = False
                self.hud.set_pause(False)
            # Interagir com NPC
            if not self._paused:
                if event.key in (pygame.K_x, pygame.K_k):
                    self._try_interact()

    def _try_interact(self):
        pr = self.player.rect
        for slot in self._npc_slots:
            npc = slot["npc"]
            if abs(pr.centerx - npc.rect.centerx) < 40 and abs(pr.centery - npc.rect.centery) < 40:
                # Criança tem dois diálogos: primeiro e segundo
                if slot["key"] == "crianca":
                    if not slot["talked"]:
                        slot["talked"] = True
                        self.karma.conversou_com_npc()
                        self.dialogue.open("crianca", avatar_surf=npc.get_avatar())
                    elif not slot.get("talked_2", False):
                        slot["talked_2"] = True
                        self.dialogue.open("crianca_2", avatar_surf=npc.get_avatar())
                    return

                if not slot["talked"]:
                    slot["talked"] = True
                    self.karma.conversou_com_npc()

                def on_close(s=slot):
                    if s["key"] == "zequinha" and not self._zequinha_disappeared:
                        self._zequinha_disappeared = True
                        # Partículas de desaparecimento espiritual
                        cx = int(s["npc"].x + s["npc"].W // 2)
                        cy = int(s["npc"].y + s["npc"].H // 2)
                        self.particles.emit_boss_death(cx, cy)
                        self.sys_msg.show("Zequinha... sumiu?", 150)

                self.dialogue.open(slot["key"], avatar_surf=npc.get_avatar(), on_close=on_close)
                return

    def update(self):
        if not self._ready or self._paused:
            return
        if self.hud.death_active:
            self.hud.update()
            return

        if not self.dialogue.active:
            self.player.update(self.input.poll(), self.tilemap, self.particles)

        self.dialogue.update()
        self.sys_msg.update()

        # Atualiza NPCs e remove Zequinha se desapareceu
        if self._zequinha_disappeared:
            self._npc_slots = [s for s in self._npc_slots if s["key"] != "zequinha"]
            self._zequinha_disappeared = False   # evita re-filtrar todo frame

        for slot in self._npc_slots:
            slot["npc"].update()

        self.particles.update()
        self.fx.update()
        self.hud.update()

        # Morte do player
        if self.player.dead and not self.hud.death_active:
            self.hud.show_death()

        # Câmera segue player
        self.camera.update(
            self.player.x + Player.W // 2,
            self.player.y + Player.H // 2
        )

        # Indicador de interação com nome do NPC
        pr = self.player.rect
        for slot in self._npc_slots:
            npc = slot["npc"]
            if abs(pr.centerx - npc.rect.centerx) < 40 and abs(pr.centery - npc.rect.centery) < 40:
                self.hud.show_interaction(f"conversar com {slot['name']}")
                break

        # Transição para próxima cena
        if self.player.x > self.NEXT_SCENE_X and not self._transitioning:
            self._go_to_trail()

        # Timer de transição — aqui no update, não no draw
        if self._transitioning:
            self._transition_timer -= 1
            if self._transition_timer <= 0:
                self._transitioning = False
                from scenes.trail_scene import TrailScene
                self.scene_manager.replace(
                    TrailScene(self.scene_manager, self.bus, self.karma, self.input, self.player)
                )

        # Impede sair pela esquerda
        if self.player.x < 0:
            self.player.x = 0

    def _go_to_menu(self):
        from scenes.intro_scene import IntroScene
        from systems.karma import KarmaSystem
        new_karma = KarmaSystem(self.bus)
        self.scene_manager.replace(IntroScene(self.scene_manager, self.bus, new_karma, self.input))

    def _go_to_trail(self):
        self.fx.fade_out(frames=20)
        self._transitioning    = True
        self._transition_timer = 20

    def draw(self, surf):
        if not self._ready:
            surf.fill((0, 0, 0))
            return

        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)

        # ── Fundo parallax ──
        _draw_sky(surf, cam_x, self.WORLD_W)
        _draw_sun(surf, cam_x)
        _draw_pedra_bg(surf, cam_x)
        _draw_mountains(surf, cam_x)
        _draw_hills(surf, cam_x)

        # ── Tilemap ──
        self.tilemap.draw(surf, cam_x, cam_y, SCREEN_W, SCREEN_H)

        # ── NPCs ──
        for slot in self._npc_slots:
            slot["npc"].draw(surf, cam_x, cam_y)

        # ── Partículas ──
        self.particles.draw(surf, cam_x, cam_y)

        # ── Player ──
        self.player.draw(surf, cam_x, cam_y)

        # ── HUD ──
        self.hud.draw(surf, self.player.hp, self.player.max_hp)

        # ── Diálogo ──
        self.dialogue.draw(surf)
        self.sys_msg.draw(surf)

        # ── Efeitos de tela ──
        self.fx.draw(surf)

        # ── Seta de saída à direita ──
        if self.player.x > self.WORLD_W - 80:
            if not hasattr(self, '_arrow_font'):
                try:
                    self._arrow_font = pygame.font.SysFont("Courier New", 11)
                except Exception:
                    self._arrow_font = pygame.font.Font(None, 14)
            arr = self._arrow_font.render("→ Trilha da Pedra", True, GOLD)
            surf.blit(arr, (SCREEN_W - arr.get_width() - 8, SCREEN_H // 2))

