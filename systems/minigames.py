import pygame
import math
from settings import SCREEN_W, SCREEN_H, GOLD


KEY_SEQUENCE = [
    (pygame.K_z, "Z"),
    (pygame.K_x, "X"),
    (pygame.K_k, "K"),
]


class RuneMiniGame:
    def __init__(self, title="Jogo dos simbolos", on_win=None):
        self.title = title
        self.on_win = on_win
        self.active = False
        self.done = False
        self.index = 0
        self.timer = 0
        self.feedback = ""
        self._font = None
        self._big_font = None

    def open(self):
        if self.done:
            return
        self.active = True
        self.index = 0
        self.timer = 240
        self.feedback = ""

    def handle_event(self, event):
        if not self.active or event.type != pygame.KEYDOWN:
            return False
        expected, _ = KEY_SEQUENCE[self.index]
        if event.key == expected:
            self.index += 1
            self.feedback = "certo"
            if self.index >= len(KEY_SEQUENCE):
                self.active = False
                self.done = True
                if self.on_win:
                    self.on_win()
        else:
            self.index = 0
            self.feedback = "errou"
        return True

    def update(self):
        if not self.active:
            return
        self.timer -= 1
        if self.timer <= 0:
            self.index = 0
            self.active = False
            self.feedback = ""

    def draw(self, surf):
        if not self.active:
            return
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("Courier New", 11, bold=True)
                self._big_font = pygame.font.SysFont("Courier New", 16, bold=True)
            except Exception:
                self._font = pygame.font.Font(None, 14)
                self._big_font = pygame.font.Font(None, 20)

        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 165))
        surf.blit(ov, (0, 0))

        pw, ph = 250, 106
        px = (SCREEN_W - pw) // 2
        py = (SCREEN_H - ph) // 2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((10, 7, 20, 240))
        surf.blit(panel, (px, py))
        pygame.draw.rect(surf, GOLD, (px, py, pw, ph), 1)

        title = self._big_font.render(self.title, True, GOLD)
        surf.blit(title, ((SCREEN_W - title.get_width()) // 2, py + 10))

        for i, (_, label) in enumerate(KEY_SEQUENCE):
            bx = px + 58 + i * 48
            by = py + 42
            active = i == self.index
            col = (230, 205, 80) if active else (80, 70, 45)
            pygame.draw.rect(surf, col, (bx, by, 28, 24), 1)
            txt = self._big_font.render(label, True, col)
            surf.blit(txt, (bx + (28 - txt.get_width()) // 2, by + 3))

        remaining = max(0, self.timer / 240)
        pygame.draw.rect(surf, (45, 35, 20), (px + 30, py + 78, pw - 60, 6))
        pygame.draw.rect(surf, (180, 120, 45), (px + 30, py + 78, int((pw - 60) * remaining), 6))

        hint = self._font.render("Repita a sequencia antes do tempo acabar", True, (170, 150, 110))
        surf.blit(hint, ((SCREEN_W - hint.get_width()) // 2, py + 88))


class MiniGameTotem:
    W = 14
    H = 22

    def __init__(self, x, y, title, on_win):
        self.x = float(x)
        self.y = float(y)
        self.game = RuneMiniGame(title, on_win=on_win)
        self.time = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def done(self):
        return self.game.done

    def open(self):
        self.game.open()

    def handle_event(self, event):
        return self.game.handle_event(event)

    def update(self):
        self.time += 1
        self.game.update()

    def draw_world(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if not (-20 < sx < SCREEN_W + 20):
            return
        col = (70, 55, 35) if self.done else (130, 95, 45)
        glow_alpha = 30 + int(abs(math.sin(self.time * 0.07)) * 50)
        if not self.done:
            gsurf = pygame.Surface((34, 34), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (220, 170, 70, glow_alpha), (17, 17), 17)
            surf.blit(gsurf, (sx - 10, sy - 7))
        pygame.draw.rect(surf, col, (sx + 3, sy + 5, 8, 17))
        pygame.draw.rect(surf, (45, 30, 18), (sx + 3, sy + 5, 8, 17), 1)
        pygame.draw.rect(surf, (180, 130, 55), (sx, sy, 14, 7))
        pygame.draw.circle(surf, (30, 18, 10), (sx + 7, sy + 3), 2)

    def draw_overlay(self, surf):
        self.game.draw(surf)
