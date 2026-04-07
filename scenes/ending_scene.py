# scenes/ending_scene.py — Tela de final do jogo

import pygame
from settings import SCREEN_W, SCREEN_H
from systems.karma import KarmaSystem
from art.fx import ScreenEffects


class EndingScene:
    """
    Exibe o final do jogo baseado no karma acumulado.
    Aceita 3 tipos: 'verdadeiro', 'neutro', 'ruim'.
    Pressionar ENTER reinicia o jogo do início.
    """

    def __init__(self, scene_manager, bus, karma, input_manager, final_type: str):
        self.scene_manager = scene_manager
        self.bus           = bus
        self.karma         = karma
        self.input         = input_manager
        self.final_type    = final_type

        self.time        = 0
        self._blink      = True
        self._blink_timer = 0
        self._font_title = None
        self._font_body  = None
        self._ready      = False
        self.fx          = ScreenEffects(SCREEN_W, SCREEN_H)

    # ── Ciclo de vida ──────────────────────────────────────────────────────────

    def on_enter(self):
        self._init_fonts()
        self.fx.fade_in(frames=30)
        self._ready = True

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def _init_fonts(self):
        try:
            self._font_title = pygame.font.SysFont("Courier New", 18, bold=True)
            self._font_body  = pygame.font.SysFont("Courier New", 11)
        except Exception:
            self._font_title = pygame.font.Font(None, 22)
            self._font_body  = pygame.font.Font(None, 14)

    # ── Conteúdo por tipo de final ─────────────────────────────────────────────

    def _get_content(self):
        if self.final_type == "verdadeiro":
            return (
                "O LEGADO DOS ANCESTRAIS",
                [
                    "Caio descobriu que o verdadeiro tesouro",
                    "não eram as riquezas da pedra —",
                    "mas a história de seu povo,",
                    "e a força que carregava dentro de si.",
                    "",
                    "Ele voltou para a vila com a sabedoria",
                    "dos que vieram antes.",
                    "E a Pedra dos Ancestrais descansou em paz.",
                ],
                (220, 200, 80),
            )
        if self.final_type == "ruim":
            return (
                "CONSUMIDO PELA PEDRA",
                [
                    "A ganância de Caio o cegou.",
                    "Ele tocou o tesouro...",
                    "e a Pedra não o deixou partir.",
                    "",
                    "Dizem que à noite,",
                    "ainda é possível ouvir seus passos",
                    "ecoando nas câmaras de pedra.",
                ],
                (200, 60, 40),
            )
        # neutro
        return (
            "UM FARDO LEVADO",
            [
                "Caio saiu da pedra diferente.",
                "Não sábio, não condenado —",
                "apenas... mudado.",
                "",
                "A lenda continua.",
                "Como todas as lendas do sertão.",
            ],
            (160, 150, 200),
        )

    # ── Eventos ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                self._restart()

    def _restart(self):
        from scenes.intro_scene import IntroScene
        new_karma = KarmaSystem(self.bus)
        self.scene_manager.replace(
            IntroScene(self.scene_manager, self.bus, new_karma, self.input)
        )

    # ── Update ─────────────────────────────────────────────────────────────────

    def update(self):
        self.time += 1
        self._blink_timer += 1
        if self._blink_timer >= 40:
            self._blink_timer = 0
            self._blink = not self._blink
        self.fx.update()

    # ── Draw ───────────────────────────────────────────────────────────────────

    def draw(self, surf):
        title_text, body_lines, title_col = self._get_content()

        # Gradiente de fundo por tipo de final
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            if self.final_type == "verdadeiro":
                r = int(40  + t * 60)
                g = int(20  + t * 80)
                b = int(80  + t * 120)
            elif self.final_type == "ruim":
                r = int(60  + t * 40)
                g = int(10  + t * 10)
                b = int(10  + t * 20)
            else:
                r = int(30  + t * 50)
                g = int(25  + t * 50)
                b = int(50  + t * 80)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))

        # Título
        title  = self._font_title.render(title_text, True, title_col)
        shadow = self._font_title.render(title_text, True, (20, 10, 5))
        tx = (SCREEN_W - title.get_width()) // 2
        surf.blit(shadow, (tx + 2, 32))
        surf.blit(title,  (tx, 30))

        # Separador dourado
        pygame.draw.line(surf, title_col,
                         (SCREEN_W // 4, 52), (3 * SCREEN_W // 4, 52), 1)

        # Corpo do texto com fade-in linha a linha
        for i, line in enumerate(body_lines):
            if not line:
                continue
            delay = i * 5
            alpha = min(255, (self.time - delay) * 10) if self.time > delay else 0
            if alpha <= 0:
                continue
            ls = self._font_body.render(line, True, (200, 190, 170))
            ls.set_alpha(alpha)
            lx = (SCREEN_W - ls.get_width()) // 2
            surf.blit(ls, (lx, 68 + i * 16))

        # Resumo de karma (atributos do dataclass, não dict)
        summ = self.karma.get_summary()
        stats = [
            f"Coragem:  {'█' * summ.coragem}{'░' * (5 - summ.coragem)}",
            f"Sabedoria:{'█' * summ.sabedoria}{'░' * (5 - summ.sabedoria)}",
            f"Ganância: {'█' * summ.ganancia}{'░' * (5 - summ.ganancia)}",
        ]
        for i, stat in enumerate(stats):
            ss = self._font_body.render(stat, True, (160, 140, 100))
            surf.blit(ss, (20, SCREEN_H - 52 + i * 14))

        # Pressione ENTER (piscante)
        if self._blink:
            ps = self._font_body.render(
                "Pressione ENTER para jogar novamente", True, (180, 160, 120)
            )
            px = (SCREEN_W - ps.get_width()) // 2
            surf.blit(ps, (px, SCREEN_H - 18))

        self.fx.draw(surf)
