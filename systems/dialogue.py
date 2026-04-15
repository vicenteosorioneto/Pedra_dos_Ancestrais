# systems/dialogue.py — sistema de diálogo premium v4
# MELHORIAS:
# - Sem linha anterior visível (fantasma removido)
# - Slide-up ao abrir
# - Cursor piscante durante typewriter
# - Contador de progresso (2/6)
# - Indicador ▼ pulsa suavemente
# - Gradiente no fundo

import pygame
import math
from settings import SCREEN_W, SCREEN_H, BLACK, GOLD, PALETTE_SERTAO as P
from systems.dialogue_loader import DialogueLoader

_loader = DialogueLoader()
DIALOGUE_DATA: dict[str, list[str]] = _loader._data

_NPC_NAMES: dict[str, str] = {
    "aldeao_0":         "Aldeão",
    "aldeao_1":         "Aldeão",
    "aldeao_2":         "Aldeão",
    "zequinha":         "Seu Zequinha",
    "zequinha_sumiu":   "Seu Zequinha",
    "comerciante":      "Comerciante",
    "crianca":          "Criança",
    "crianca_2":        "Criança",
    "morador_medo":     "Morador",
    "guardiao":         "Guardião",
    "guardiao_intro":   "",
    "iracema":          "Iracema",
    "iracema_proposta": "Iracema",
    "iracema_aceita":   "Iracema",
    "iracema_recusa":   "Iracema",
    "velho_da_pedra":   "Velho da Pedra",
    "altar_0":          "[Visão]",
    "altar_1":          "[Visão]",
    "altar_2":          "[Visão]",
    "altar_3":          "[Visão]",
    "altar_4":          "[Visão]",
    "registro_0":       "[Inscrição]",
    "registro_1":       "[Inscrição]",
    "registro_2":       "[Inscrição]",
    "registro_3":       "[Inscrição]",
    "registro_4":       "[Inscrição]",
    "camara_0":              "[A Pedra]",
    "camara_1":              "[A Pedra]",
    "camara_2":              "[A Pedra]",
    # Floresta
    "peregrino_floresta":    "Peregrino",
    "registro_floresta_0":   "[Inscrição]",
    "registro_floresta_1":   "[Inscrição]",
    # Ruínas
    "altar_ruinas":          "[Visão]",
    "registro_ruinas_0":     "[Inscrição]",
    "registro_ruinas_1":     "[Inscrição]",
}


class DialogueBox:
    BOX_H     = 76
    BOX_Y_BASE = SCREEN_H - BOX_H - 4
    BOX_PAD   = 8
    AVATAR_W  = 44
    CHAR_SPEED = 2

    def __init__(self):
        self.active       = False
        self.lines        = []
        self.npc_name     = ""
        self.avatar_surf  = None
        self.current_line = 0
        self.char_index   = 0.0
        self.frame_count  = 0
        self._font        = None
        self._name_font   = None
        self._small_font  = None
        self._on_close_cb = None
        self._slide_y     = 0.0   # 0=dentro, 1=fora
        self._tick        = 0

    def _init_fonts(self):
        if self._font is None:
            try:
                self._font      = pygame.font.SysFont("Courier New", 11)
                self._name_font = pygame.font.SysFont("Courier New", 12, bold=True)
                self._small_font= pygame.font.SysFont("Courier New", 9)
            except Exception:
                self._font      = pygame.font.Font(None, 14)
                self._name_font = pygame.font.Font(None, 16)
                self._small_font= pygame.font.Font(None, 12)

    def open(self, npc_key, avatar_surf=None, on_close=None):
        self._init_fonts()
        self.active       = True
        self.lines        = _loader.get(npc_key)
        self.npc_name     = _NPC_NAMES.get(npc_key, npc_key.replace("_"," ").title())
        self.avatar_surf  = avatar_surf
        self.current_line = 0
        self.char_index   = 0.0
        self.frame_count  = 0
        self._on_close_cb = on_close
        self._slide_y     = 1.0   # começa fora, slide para dentro
        self._tick        = 0

    def close(self):
        self.active = False
        self._slide_y = 0.0
        if self._on_close_cb:
            self._on_close_cb()
            self._on_close_cb = None

    def advance(self):
        if not self.active: return
        line = self.lines[self.current_line]
        if int(self.char_index) < len(line):
            self.char_index = float(len(line))
            return
        self.current_line += 1
        self._tick = 0
        if self.current_line >= len(self.lines):
            self.close()
        else:
            self.char_index = 0.0

    def update(self):
        if not self.active: return
        self._tick += 1
        self.frame_count += 1

        # Slide up (entra da base)
        if self._slide_y > 0:
            self._slide_y = max(0.0, self._slide_y - 0.12)

        line = self.lines[self.current_line]
        if self.char_index < len(line):
            self.char_index += self.CHAR_SPEED

    def draw(self, surf):
        if not self.active: return
        self._init_fonts()

        slide_offset = int(self._slide_y * (self.BOX_H + 10))
        by = self.BOX_Y_BASE + slide_offset
        bx = 4
        bw = SCREEN_W - 8
        bh = self.BOX_H

        # Fundo com gradiente manual
        box = pygame.Surface((bw, bh), pygame.SRCALPHA)
        for row in range(bh):
            t = row / bh
            r = int(P["hud_bg"][0] * (1 + t * 0.5))
            g = int(P["hud_bg"][1] * (1 + t * 0.4))
            b = int(P["hud_bg"][2] * (1 + t * 0.6))
            alpha = int(230 * (0.88 + t * 0.12))
            pygame.draw.line(box, (min(255,r), min(255,g), min(255,b), alpha),
                             (0, row), (bw, row))
        surf.blit(box, (bx, by))

        # Bordas
        pygame.draw.rect(surf, BLACK,       (bx,   by,   bw,   bh),   2)
        pygame.draw.rect(surf, (55, 44, 20),(bx+2, by+2, bw-4, bh-4), 1)
        pygame.draw.rect(surf, GOLD,        (bx+3, by+3, bw-6, bh-6), 1)

        # Linha accent topo
        pygame.draw.rect(surf, (80, 60, 20), (bx+4, by+4, bw-8, 2))

        # Avatar
        tx = bx + self.BOX_PAD
        if self.avatar_surf:
            av = pygame.transform.scale(self.avatar_surf, (self.AVATAR_W, self.AVATAR_W))
            pygame.draw.rect(surf, (40,32,12), (tx-1, by+14, self.AVATAR_W+2, self.AVATAR_W+2))
            surf.blit(av, (tx, by+15))
            pygame.draw.rect(surf, GOLD, (tx, by+15, self.AVATAR_W, self.AVATAR_W), 1)
            tx = tx + self.AVATAR_W + self.BOX_PAD

        # Nome
        if self.npc_name:
            is_iracema = "iracema" in self.npc_name.lower()
            name_col = (80, 160, 220) if is_iracema else GOLD
            ns = self._name_font.render(self.npc_name, True, name_col)
            surf.blit(ns, (tx, by + 8))
            pygame.draw.line(surf, (45,36,15),
                             (tx, by+22), (tx + ns.get_width() + 20, by+22), 1)
            text_y = by + 26
        else:
            text_y = by + 14

        # Texto atual — SEM linha anterior
        line = self.lines[self.current_line]
        visible = line[:int(self.char_index)]
        full    = self.char_index >= len(line)

        # Quebra de linha por palavras
        max_ch = 54
        words = visible.split(' ')
        lines_out = []
        cur = ""
        for w in words:
            cand = (cur + " " + w).strip()
            if len(cand) > max_ch:
                if cur: lines_out.append(cur)
                cur = w
            else:
                cur = cand
        if cur: lines_out.append(cur)

        for i, ln in enumerate(lines_out[:2]):
            ts = self._font.render(ln, True, (220, 210, 190))
            surf.blit(ts, (tx, text_y + i * 14))

        # Cursor piscante
        if not full:
            cursor_on = (self._tick // 8) % 2 == 0
            if cursor_on and lines_out:
                last_w = self._font.render(lines_out[-1], True, (220, 210, 190))
                cx = tx + last_w.get_width() + 2
                cy = text_y + (len(lines_out)-1) * 14
                pygame.draw.rect(surf, (200, 160, 40), (cx, cy+2, 2, 9))

        # Indicador ▼ pulsante
        if full:
            pulse = int(abs(math.sin(self._tick * 0.12)) * 180) + 60
            pa = max(0, min(255, pulse))
            col = (int(GOLD[0]*pa//240), int(GOLD[1]*pa//240), int(GOLD[2]*pa//240))
            arr = self._small_font.render("▼", True, col)
            surf.blit(arr, (bx + bw - 20, by + bh - 14))
            hint = self._small_font.render("[X]", True,
                                           (int(col[0]*0.6), int(col[1]*0.6), 0))
            surf.blit(hint, (bx + bw - 38, by + bh - 14))

        # Contador de progresso
        n = len(self.lines)
        if n > 1:
            prog = self._small_font.render(f"{self.current_line+1}/{n}",
                                           True, (55, 44, 20))
            surf.blit(prog, (bx + bw - prog.get_width() - 6, by + 5))


class ChoiceBox:
    BOX_H = 56
    BOX_Y = SCREEN_H - DialogueBox.BOX_H - 6 - 56

    def __init__(self):
        self.active   = False
        self.options: list[tuple[str, object]] = []
        self.selected = 0
        self._font    = None

    def _init_font(self):
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("Courier New", 11)
            except Exception:
                self._font = pygame.font.Font(None, 14)

    def open(self, options):
        self._init_font()
        self.options  = list(options)
        self.selected = 0
        self.active   = True

    def close(self):
        self.active  = False
        self.options = []

    def handle_event(self, event):
        if not self.active: return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = max(0, self.selected - 1); return True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = min(len(self.options)-1, self.selected+1); return True
            if event.key in (pygame.K_x, pygame.K_k, pygame.K_RETURN, pygame.K_SPACE):
                self._confirm(); return True
        return False

    def _confirm(self):
        if not self.options: return
        _, cb = self.options[self.selected]
        self.close()
        if callable(cb): cb()

    def draw(self, surf):
        if not self.active: return
        self._init_font()
        bx, by, bw, bh = 4, self.BOX_Y, SCREEN_W-8, self.BOX_H

        box = pygame.Surface((bw, bh))
        box.set_alpha(220)
        box.fill(P["hud_bg"])
        surf.blit(box, (bx, by))
        pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 2)
        pygame.draw.rect(surf, GOLD,  (bx+2, by+2, bw-4, bh-4), 1)

        prompt = self._font.render("O que você decide?", True, (180,160,100))
        surf.blit(prompt, (bx+10, by+6))

        for i, (label, _) in enumerate(self.options):
            cursor = "▶ " if i == self.selected else "  "
            color  = GOLD if i == self.selected else (160,150,130)
            text   = self._font.render(f"{cursor}{label}", True, color)
            surf.blit(text, (bx+16, by+22+i*14))

        hint = self._font.render("↑↓ navegar   X confirmar", True, (100,90,70))
        surf.blit(hint, (bx+bw-hint.get_width()-8, by+bh-12))


class SystemMessage:
    def __init__(self):
        self.text     = ""
        self.timer    = 0
        self.max_time = 120
        self._font    = None

    def _init_font(self):
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("Courier New", 11, bold=True)
            except Exception:
                self._font = pygame.font.Font(None, 14)

    def show(self, text, duration=120):
        self._init_font()
        # Deduplicar — não empilha mesma mensagem
        if text == self.text and self.timer > 0:
            self.timer = max(self.timer, duration // 2)
            return
        self.text     = text
        self.timer    = duration
        self.max_time = duration

    def update(self):
        if self.timer > 0: self.timer -= 1

    def draw(self, surf):
        if self.timer <= 0: return
        self._init_font()
        alpha = min(255, self.timer * 8, (self.max_time - self.timer) * 8)
        ts = self._font.render(self.text, True, GOLD)
        bg = pygame.Surface((ts.get_width()+12, ts.get_height()+6))
        bg.fill((0,0,0))
        bg.set_alpha(int(alpha*0.7))
        bx = (SCREEN_W - bg.get_width()) // 2
        by = 14
        surf.blit(bg, (bx, by))
        ts.set_alpha(alpha)
        surf.blit(ts, (bx+6, by+3))
