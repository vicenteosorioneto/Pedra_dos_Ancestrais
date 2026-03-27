# systems/dialogue.py — sistema de diálogo com efeito typewriter

import pygame
from settings import SCREEN_W, SCREEN_H, BLACK, GOLD, PALETTE_SERTAO as P

# Textos dos NPCs
DIALOGUE_DATA = {
    "aldeao_1": [
        "Esse vento tá esquisito hoje...",
        "parece que a Pedra tá chamando."
    ],
    "aldeao_2": [
        "Seu Zequinha foi lá pra cima ontem à noite.",
        "Eu vi com meus próprios olhos.",
        "Nunca é boa ideia."
    ],
    "comerciante": [
        "Três homens foram nessa pedra no século passado.",
        "Nenhum voltou do mesmo jeito, menino."
    ],
    "zequinha": [
        "A pedra chama... mas só entra quem está destinado.",
        "Se um dia você encontrar o símbolo,",
        "saiba: o tesouro não alimenta o corpo.",
        "Ele alimenta o que você mais deseja —",
        "e cobra o preço mais alto."
    ],
    "guardiao": [
        "Você... tem o sinal.",
        "Pode passar.",
        "Mas devia voltar."
    ],
    "iracema": [
        "Você não é o primeiro a procurar",
        "alguém aqui dentro.",
        "E não será o último a se perder."
    ],
}


class DialogueBox:
    # Altura e posição da caixa
    BOX_H     = 80
    BOX_Y     = SCREEN_H - BOX_H - 4
    BOX_PAD   = 8
    AVATAR_W  = 40
    CHAR_SPEED = 2  # caracteres por frame

    def __init__(self):
        self.active      = False
        self.lines       = []
        self.npc_name    = ""
        self.avatar_surf = None
        self.current_line = 0
        self.char_index  = 0.0
        self.frame_count = 0
        self.blink_timer = 0
        self.blink_state = True
        self._font = None
        self._name_font = None
        self._on_close_cb = None

    def _init_fonts(self):
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("Courier New", 11)
            except Exception:
                self._font = pygame.font.Font(None, 14)
        if self._name_font is None:
            try:
                self._name_font = pygame.font.SysFont("Courier New", 12, bold=True)
            except Exception:
                self._name_font = pygame.font.Font(None, 16)

    def open(self, npc_key, avatar_surf=None, on_close=None):
        self._init_fonts()
        self.active       = True
        self.lines        = DIALOGUE_DATA.get(npc_key, ["..."])
        self.npc_name     = npc_key.replace("_", " ").title()
        self.avatar_surf  = avatar_surf
        self.current_line = 0
        self.char_index   = 0.0
        self.frame_count  = 0
        self._on_close_cb = on_close

    def close(self):
        self.active = False
        if self._on_close_cb:
            self._on_close_cb()
            self._on_close_cb = None

    def advance(self):
        """Avança linha ou fecha o diálogo."""
        if not self.active:
            return
        # Se texto não terminou, completa de uma vez
        line = self.lines[self.current_line]
        if int(self.char_index) < len(line):
            self.char_index = float(len(line))
            return
        # Próxima linha
        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.close()
        else:
            self.char_index = 0.0

    def update(self):
        if not self.active:
            return
        self.frame_count += 1
        # Typewriter: avança caracteres
        line = self.lines[self.current_line]
        if self.char_index < len(line):
            self.char_index += self.CHAR_SPEED
        # Piscar triângulo
        if self.frame_count % 20 == 0:
            self.blink_state = not self.blink_state

    def draw(self, surf):
        if not self.active:
            return
        self._init_fonts()
        bx = 4
        by = self.BOX_Y
        bw = SCREEN_W - 8
        bh = self.BOX_H

        # Fundo com alpha
        box = pygame.Surface((bw, bh))
        box.set_alpha(220)
        box.fill(P["hud_bg"])
        surf.blit(box, (bx, by))

        # Borda dupla
        pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 2)
        pygame.draw.rect(surf, GOLD,  (bx+2, by+2, bw-4, bh-4), 1)

        # Avatar
        ax = bx + self.BOX_PAD
        ay = by + self.BOX_PAD
        if self.avatar_surf:
            scaled = pygame.transform.scale(self.avatar_surf, (self.AVATAR_W, self.AVATAR_W))
            surf.blit(scaled, (ax, ay))
            pygame.draw.rect(surf, GOLD, (ax, ay, self.AVATAR_W, self.AVATAR_W), 1)
        tx = ax + self.AVATAR_W + self.BOX_PAD

        # Nome do NPC
        name_surf = self._name_font.render(self.npc_name, True, GOLD)
        surf.blit(name_surf, (tx, by + 6))

        # Texto typewriter
        line = self.lines[self.current_line]
        visible = line[:int(self.char_index)]
        text_surf = self._font.render(visible, True, (220, 210, 190))
        surf.blit(text_surf, (tx, by + 22))

        # Linhas anteriores (acima, se houver espaço)
        if self.current_line > 0:
            prev = self.lines[self.current_line - 1]
            prev_surf = self._font.render(prev, True, (140, 130, 110))
            surf.blit(prev_surf, (tx, by + 12))

        # Triângulo piscante
        if self.blink_state and int(self.char_index) >= len(line):
            arr = self._font.render("▼", True, GOLD)
            surf.blit(arr, (bx + bw - 16, by + bh - 14))


class SystemMessage:
    """Mensagens temporárias que surgem no topo-centro da tela."""
    def __init__(self):
        self.text     = ""
        self.timer    = 0
        self.max_time = 120
        self._font    = None

    def _init_font(self):
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("Courier New", 12, bold=True)
            except Exception:
                self._font = pygame.font.Font(None, 16)

    def show(self, text, duration=120):
        self._init_font()
        self.text     = text
        self.timer    = duration
        self.max_time = duration

    def update(self):
        if self.timer > 0:
            self.timer -= 1

    def draw(self, surf):
        if self.timer <= 0:
            return
        self._init_font()
        alpha = min(255, self.timer * 8, (self.max_time - self.timer) * 8)
        ts = self._font.render(self.text, True, GOLD)
        bg = pygame.Surface((ts.get_width() + 12, ts.get_height() + 6))
        bg.fill((0, 0, 0))
        bg.set_alpha(int(alpha * 0.7))
        bx = (SCREEN_W - bg.get_width()) // 2
        by = 12
        surf.blit(bg, (bx, by))
        ts.set_alpha(alpha)
        surf.blit(ts, (bx + 6, by + 3))
