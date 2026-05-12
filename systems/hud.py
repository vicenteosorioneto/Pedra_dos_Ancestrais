# systems/hud.py — HUD premium v4
# MELHORIAS:
# - Tela de morte com overlay gradual + texto + aguarda input
# - Tela de pausa premium com painel
# - Prompt de interação pulsante (não pisca)
# - Deduplicação de mensagens
# - Label de ato mais visível

import pygame
import math
from settings import PALETTE_SERTAO as P, BLACK, GOLD, SCREEN_W, SCREEN_H
from art.fx import Particle


def _draw_heart(surf, x, y, full=True):
    """Coração 12x12 pixel art com highlight e sombra."""
    filled = P["heart_red"] if full else P["heart_empty"]
    light  = (255, 110, 110) if full else (100, 50, 50)
    shadow = (140, 20, 20)   if full else (40, 15, 15)

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
        c = light if (hx <= 3 and hy <= 3) else shadow if hy >= 7 else filled
        surf.set_at((x+hx, y+hy), c)
    for hx, hy in [(3,2),(4,2),(3,3)]:
        surf.set_at((x+hx, y+hy), light)
    outline_pts = [
        (1,1),(5,0),(6,0),(10,1),(11,2),(11,3),(11,4),(10,5),
        (9,6),(8,7),(7,8),(6,9),(5,9),(4,8),(3,7),(2,6),(1,5),(0,4),(0,3),(0,2),
    ]
    for hx, hy in outline_pts:
        if 0 <= x+hx < surf.get_width() and 0 <= y+hy < surf.get_height():
            surf.set_at((x+hx, y+hy), BLACK)


class HUD:
    HP_BOX_X = 4
    HP_BOX_Y = 4
    HP_BOX_W = 96
    HP_BOX_H = 30

    def __init__(self, karma_system=None):
        self.karma = karma_system
        self._font        = None
        self._small_font  = None
        self._big_font    = None
        self.particles: list[Particle] = []
        self.interaction_text  = ""
        self.interaction_timer = 0
        self._altar_count = -1
        self._altar_total = 3
        self._objectives = []
        self._scene_label = ""
        self._damage_timer = 0
        self._prev_hp = -1
        self._tick = 0

        # Morte premium
        self._death_timer = -1
        self._death_alpha = 0
        self._showing_controls = False

        # Pausa premium
        self._paused   = False
        self._pause_cb_menu = None

    def _init_fonts(self):
        if self._font is None:
            try:
                self._font       = pygame.font.SysFont("Courier New", 16, bold=True)
                self._small_font = pygame.font.SysFont("Courier New", 14)
                self._big_font   = pygame.font.SysFont("Courier New", 28, bold=True)
            except Exception:
                self._font       = pygame.font.Font(None, 20)
                self._small_font = pygame.font.Font(None, 18)
                self._big_font   = pygame.font.Font(None, 34)

    # ── API pública ──────────────────────────────────────────────────────────

    def notify_damage(self):
        self._damage_timer = 22
        for i in range(3):
            self.emit_heart_break(i)

    def set_scene_label(self, text):
        self._scene_label = text

    def set_altar_progress(self, count, total=3):
        self._altar_count = count
        self._altar_total = total

    def clear_altar_progress(self):
        self._altar_count = -1

    def set_objectives(self, objectives):
        self._objectives = list(objectives or [])

    def show_interaction(self, text):
        self.interaction_text  = text
        self.interaction_timer = 5

    def emit_heart_break(self, heart_index):
        import random
        hx = self.HP_BOX_X + 8 + heart_index * 16
        hy = self.HP_BOX_Y + 6
        for _ in range(4):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            p = Particle(hx, hy, P["heart_red"],
                         math.cos(angle)*speed, math.sin(angle)*speed-1.0,
                         life=25, size=2)
            self.particles.append(p)

    def show_death(self):
        if self._death_timer < 0:
            self._death_timer = 0

    def hide_death(self):
        self._death_timer = -1
        self._death_alpha = 0
        self._showing_controls = False

    def show_controls(self):
        self._showing_controls = True

    def hide_controls(self):
        self._showing_controls = False

    @property
    def death_active(self):
        return self._death_timer >= 0

    @property
    def death_ready_for_input(self):
        return self._death_timer > 110

    def set_pause(self, paused, menu_cb=None):
        self._paused = paused
        self._pause_cb_menu = menu_cb

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self):
        self._tick += 1
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()
        if self.interaction_timer > 0:
            self.interaction_timer -= 1
        if self._damage_timer > 0:
            self._damage_timer -= 1
        if self._death_timer >= 0:
            self._death_timer += 1
            self._death_alpha = min(200, self._death_timer * 4)

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, surf, player_hp, player_max_hp=3):
        self._init_fonts()
        self._draw_hp_area(surf, player_hp, player_max_hp)
        self._draw_altar_counter(surf)
        self._draw_objectives(surf)
        self._draw_scene_label(surf)
        self._draw_interaction(surf)
        for p in self.particles:
            p.draw(surf)
        if self._death_timer >= 0:
            self._draw_death(surf)
        if self._paused:
            self._draw_pause(surf)

    def _draw_hp_area(self, surf, hp, max_hp):
        shake = 0
        if self._damage_timer > 0:
            shake = int(math.sin(self._damage_timer * 1.9) * 2)
        bx = self.HP_BOX_X + shake
        by = self.HP_BOX_Y
        bw = self.HP_BOX_W
        bh = self.HP_BOX_H

        hud_bg = pygame.Surface((bw, bh))
        hud_bg.set_alpha(190)
        hud_bg.fill(P["hud_bg"])
        surf.blit(hud_bg, (bx, by))

        if self._damage_timer > 0:
            intensity = min(120, self._damage_timer * 8)
            flash = pygame.Surface((bw, bh), pygame.SRCALPHA)
            flash.fill((200, 30, 30, intensity))
            surf.blit(flash, (bx, by))

        border_col = (220, 60, 60) if self._damage_timer > 0 else (55, 44, 20)
        pygame.draw.rect(surf, border_col, (bx, by, bw, bh), 1)
        pygame.draw.rect(surf, GOLD,       (bx+1, by+1, bw-2, bh-2), 1)

        for i in range(max_hp):
            hx = bx + 8 + i * 18
            hy = by + 9
            _draw_heart(surf, hx, hy, full=(i < hp))

    def _draw_altar_counter(self, surf):
        if self._altar_count < 0: return
        n, total = self._altar_count, self._altar_total
        done = (n >= total)
        bx = self.HP_BOX_X
        by = self.HP_BOX_Y + self.HP_BOX_H + 3
        bw = max(self.HP_BOX_W, 28 + total * 18 + self._small_font.render(f"{n}/{total}", True, GOLD).get_width())
        bh = 24

        bg = pygame.Surface((bw, bh))
        bg.set_alpha(175)
        bg.fill(P["hud_bg"])
        surf.blit(bg, (bx, by))

        border_col = (80, 200, 100) if done else GOLD
        pygame.draw.rect(surf, border_col, (bx, by, bw, bh), 1)

        # Triângulos (altares)
        spacing = 17 if total > 3 else 20
        for i in range(total):
            col = (220, 180, 60) if i < n else (40, 32, 15)
            tx = bx + 8 + i * spacing
            ty = by + 5
            pygame.draw.polygon(surf, col, [(tx+6, ty), (tx+1, ty+9), (tx+11, ty+9)])
            pygame.draw.polygon(surf, (160, 130, 40) if i < n else (25,20,8),
                                [(tx+6, ty), (tx+1, ty+9), (tx+11, ty+9)], 1)

        label = self._small_font.render(f"{n}/{total}", True,
                                        (100,220,120) if done else (180,160,100))
        surf.blit(label, (bx+bw-label.get_width()-6, by+4))

    def _draw_objectives(self, surf):
        if not self._objectives:
            return

        rows = []
        for item in self._objectives:
            if len(item) == 2:
                label, done = item
                text = f"{label} ({1 if done else 0}/1)"
                complete = bool(done)
            else:
                label, count, total = item[:3]
                count = max(0, min(int(count), int(total)))
                complete = count >= int(total)
                text = f"{label} ({count}/{total})"
            rows.append((text, complete))

        bx = self.HP_BOX_X
        by = self.HP_BOX_Y + self.HP_BOX_H + 6
        if self._altar_count >= 0:
            by += 28

        width = max(210, max(self._small_font.render(t, True, GOLD).get_width() for t, _ in rows) + 18)
        row_h = self._small_font.get_height() + 3
        height = 22 + len(rows) * row_h
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        surf.blit(bg, (bx, by))
        pygame.draw.rect(surf, (55, 44, 20), (bx, by, width, height), 1)

        title = self._small_font.render("OBJETIVOS", True, GOLD)
        surf.blit(title, (bx + 8, by + 4))
        for i, (text, complete) in enumerate(rows):
            col = (100, 220, 120) if complete else (220, 210, 180)
            ts = self._small_font.render(text, True, col)
            surf.blit(ts, (bx + 8, by + 23 + i * row_h))

    def _draw_scene_label(self, surf):
        if not self._scene_label: return
        label = self._small_font.render(self._scene_label, True, (180, 160, 120))
        lw = label.get_width()
        lh = label.get_height()
        bx = SCREEN_W - lw - 10
        by = 6
        bg = pygame.Surface((lw+8, lh+4), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        surf.blit(bg, (bx-4, by-2))
        label.set_alpha(200)
        surf.blit(label, (bx, by))

    def _draw_interaction(self, surf):
        if self.interaction_timer <= 0 or not self.interaction_text: return
        # Pulso senoidal suave
        pulse = int(abs(math.sin(self._tick * 0.08)) * 30) + 205
        col = (pulse, int(pulse * 0.82), 0)
        text = f"[X] {self.interaction_text}"
        ts = self._small_font.render(text, True, col)
        pw = ts.get_width() + 16
        ph = 14
        bx = (SCREEN_W - pw) // 2
        by = SCREEN_H - 148
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surf.blit(bg, (bx, by))
        pygame.draw.rect(surf, col, (bx, by, pw, ph), 1)
        surf.blit(ts, (bx+8, by+2))

    def _draw_death(self, surf):
        t = self._death_timer
        alpha = self._death_alpha

        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, alpha))
        surf.blit(ov, (0, 0))

        if t < 40: return

        if self._showing_controls:
            self._draw_controls_panel(surf)
            return

        text_alpha = min(255, (t - 40) * 8)
        col_main = (min(255, int(200*text_alpha/255)),
                    min(255, int(40*text_alpha/255)),
                    min(255, int(40*text_alpha/255)))
        col_sub  = (min(255, int(160*text_alpha/255)),
                    min(255, int(140*text_alpha/255)),
                    min(255, int(100*text_alpha/255)))

        t1 = self._big_font.render("Caio caiu.", True, col_main)
        surf.blit(t1, ((SCREEN_W-t1.get_width())//2, SCREEN_H//2-40))

        if t > 70:
            t2 = self._font.render("Mas a pedra espera.", True, col_sub)
            surf.blit(t2, ((SCREEN_W-t2.get_width())//2, SCREEN_H//2-10))

        if t > 110:
            pulse = int(abs(math.sin(self._tick * 0.12)) * 40) + 160
            col_btn = (pulse, int(pulse*0.82), 0)
            # Três botões em linhas separadas
            options = [
                "[ENTER]  Tentar de novo",
                "[ESC]    Sair ao Menu",
                "[C]      Ver Controles",
            ]
            line_h = self._small_font.get_height() + 8
            for i, opt in enumerate(options):
                ts = self._small_font.render(opt, True, col_btn)
                surf.blit(ts, ((SCREEN_W-ts.get_width())//2, SCREEN_H//2+26+i*line_h))

    def _draw_controls_panel(self, surf):
        """Painel de controles exibido dentro da tela de morte."""
        pw, ph = 440, 270
        px = (SCREEN_W - pw) // 2
        py = (SCREEN_H - ph) // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((8, 4, 18, 245))
        surf.blit(panel, (px, py))
        pygame.draw.rect(surf, (50, 40, 25), (px, py, pw, ph), 1)
        pygame.draw.rect(surf, GOLD,         (px+2, py+2, pw-4, ph-4), 1)

        self._init_fonts()
        title = self._big_font.render("CONTROLES", True, GOLD)
        surf.blit(title, ((SCREEN_W - title.get_width()) // 2, py + 10))

        pygame.draw.line(surf, (60, 48, 24), (px+20, py+46), (px+pw-20, py+46), 1)

        controles = [
            ("← →",          "Mover"),
            ("↑  /  W  /  Z", "Pular"),
            ("Z  /  K",       "Atacar"),
            ("X  /  J",       "Interagir"),
            ("ESC",           "Pausar / Menu"),
            ("ENTER",         "Confirmar / Avançar"),
        ]
        fs = self._small_font
        col_key = (220, 200, 120)
        col_val = (170, 155, 115)
        for i, (key, action) in enumerate(controles):
            k_surf = fs.render(key, True, col_key)
            a_surf = fs.render(action, True, col_val)
            y = py + 62 + i * 28
            surf.blit(k_surf, (px + 28, y))
            surf.blit(a_surf, (px + 235, y))

        pygame.draw.line(surf, (60, 48, 24), (px+20, py+ph-34), (px+pw-20, py+ph-34), 1)
        back = fs.render("[C] ou [ESC]  Voltar", True, (140, 120, 80))
        surf.blit(back, ((SCREEN_W - back.get_width()) // 2, py + ph - 26))

    def _draw_pause(self, surf):
        W, H = SCREEN_W, SCREEN_H

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        surf.blit(ov, (0, 0))

        pw, ph = 320, 170
        px = (W-pw)//2
        py = (H-ph)//2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((8, 4, 18, 240))
        surf.blit(panel, (px, py))
        pygame.draw.rect(surf, (50,40,25), (px,py,pw,ph), 1)
        pygame.draw.rect(surf, GOLD,       (px+2,py+2,pw-4,ph-4), 1)

        ft = self._big_font
        t = ft.render("PAUSADO", True, GOLD)
        surf.blit(t, ((W-t.get_width())//2, py+18))

        pygame.draw.line(surf, (60,48,24), (px+22,py+56), (px+pw-22,py+56), 1)

        fs = self._small_font
        items = [
            ("[ENTER]  Continuar",    (220, 210, 190)),
            ("[M]      Menu principal",(160, 140, 100)),
        ]
        for i, (text, col) in enumerate(items):
            ts = fs.render(text, True, col)
            surf.blit(ts, ((W-ts.get_width())//2, py+72+i*30))

        if self._scene_label:
            ta = fs.render(self._scene_label, True, (70,58,34))
            surf.blit(ta, ((W-ta.get_width())//2, py+ph-26))
