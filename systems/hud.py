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
    HP_BOX_W = 62
    HP_BOX_H = 20

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
        self._scene_label = ""
        self._damage_timer = 0
        self._prev_hp = -1
        self._tick = 0

        # Morte premium
        self._death_timer = -1
        self._death_alpha = 0

        # Pausa premium
        self._paused   = False
        self._pause_cb_menu = None

    def _init_fonts(self):
        if self._font is None:
            try:
                self._font       = pygame.font.SysFont("Courier New", 11, bold=True)
                self._small_font = pygame.font.SysFont("Courier New", 10)
                self._big_font   = pygame.font.SysFont("Courier New", 18, bold=True)
            except Exception:
                self._font       = pygame.font.Font(None, 14)
                self._small_font = pygame.font.Font(None, 12)
                self._big_font   = pygame.font.Font(None, 24)

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
            _draw_heart(surf, bx+4+i*16, by+4, full=(i < hp))

    def _draw_altar_counter(self, surf):
        if self._altar_count < 0: return
        n, total = self._altar_count, self._altar_total
        done = (n >= total)
        bx = self.HP_BOX_X
        by = self.HP_BOX_Y + self.HP_BOX_H + 3
        bw = self.HP_BOX_W
        bh = 16

        bg = pygame.Surface((bw, bh))
        bg.set_alpha(175)
        bg.fill(P["hud_bg"])
        surf.blit(bg, (bx, by))

        border_col = (80, 200, 100) if done else GOLD
        pygame.draw.rect(surf, border_col, (bx, by, bw, bh), 1)

        # Triângulos (altares)
        for i in range(total):
            col = (220, 180, 60) if i < n else (40, 32, 15)
            tx = bx + 8 + i * 16
            ty = by + 3
            pygame.draw.polygon(surf, col, [(tx+6, ty), (tx+1, ty+9), (tx+11, ty+9)])
            pygame.draw.polygon(surf, (160, 130, 40) if i < n else (25,20,8),
                                [(tx+6, ty), (tx+1, ty+9), (tx+11, ty+9)], 1)

        label = self._small_font.render(f"{n}/{total}", True,
                                        (100,220,120) if done else (180,160,100))
        surf.blit(label, (bx+bw-label.get_width()-4, by+3))

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
        by = SCREEN_H - 108
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

        text_alpha = min(255, (t - 40) * 8)
        col_main = (min(255, int(200*text_alpha/255)),
                    min(255, int(40*text_alpha/255)),
                    min(255, int(40*text_alpha/255)))
        col_sub  = (min(255, int(160*text_alpha/255)),
                    min(255, int(140*text_alpha/255)),
                    min(255, int(100*text_alpha/255)))

        t1 = self._big_font.render("Caio caiu.", True, col_main)
        surf.blit(t1, ((SCREEN_W-t1.get_width())//2, SCREEN_H//2-28))

        if t > 70:
            t2 = self._font.render("Mas a pedra espera.", True, col_sub)
            surf.blit(t2, ((SCREEN_W-t2.get_width())//2, SCREEN_H//2+4))

        if t > 110:
            pulse = int(abs(math.sin(self._tick * 0.12)) * 40) + 160
            col_btn = (pulse, int(pulse*0.82), 0)
            t3 = self._small_font.render(
                "[ENTER] Tentar de novo     [ESC] Menu", True, col_btn)
            surf.blit(t3, ((SCREEN_W-t3.get_width())//2, SCREEN_H//2+28))

    def _draw_pause(self, surf):
        W, H = SCREEN_W, SCREEN_H

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        surf.blit(ov, (0, 0))

        pw, ph = 200, 108
        px = (W-pw)//2
        py = (H-ph)//2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((8, 4, 18, 240))
        surf.blit(panel, (px, py))
        pygame.draw.rect(surf, (50,40,25), (px,py,pw,ph), 1)
        pygame.draw.rect(surf, GOLD,       (px+2,py+2,pw-4,ph-4), 1)

        ft = self._big_font
        t = ft.render("PAUSADO", True, GOLD)
        surf.blit(t, ((W-t.get_width())//2, py+12))

        pygame.draw.line(surf, (60,48,24), (px+16,py+34), (px+pw-16,py+34), 1)

        fs = self._small_font
        items = [
            ("[ENTER]  Continuar",    (220, 210, 190)),
            ("[M]      Menu principal",(160, 140, 100)),
        ]
        for i, (text, col) in enumerate(items):
            ts = fs.render(text, True, col)
            surf.blit(ts, ((W-ts.get_width())//2, py+44+i*22))

        if self._scene_label:
            ta = fs.render(self._scene_label, True, (70,58,34))
            surf.blit(ta, ((W-ta.get_width())//2, py+ph-16))
