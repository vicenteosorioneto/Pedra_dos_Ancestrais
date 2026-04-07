# systems/hud.py — HUD: corações, altares, label de cena, interação

import pygame
import math
from settings import PALETTE_SERTAO as P, BLACK, GOLD, SCREEN_W, SCREEN_H
from art.fx import Particle


def _draw_heart(surf, x, y, full=True):
    """Desenha coração 12x12 pixel art."""
    filled = P["heart_red"] if full else P["heart_empty"]
    light  = (255, 100, 100) if full else (100, 50, 50)

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
        surf.set_at((x + hx, y + hy), filled)
    for hx, hy in [(3,2),(4,2),(3,3)]:
        surf.set_at((x + hx, y + hy), light)
    outline_pts = [
        (1,1),(5,0),(6,0),(10,1),(11,2),(11,3),(11,4),(10,5),
        (9,6),(8,7),(7,8),(6,9),(5,9),(4,8),(3,7),(2,6),(1,5),(0,4),(0,3),(0,2),
    ]
    for hx, hy in outline_pts:
        if 0 <= x+hx < surf.get_width() and 0 <= y+hy < surf.get_height():
            surf.set_at((x+hx, y+hy), BLACK)


class HUD:
    # ── Constantes de layout ───────────────────────────────────────────────────
    HP_BOX_X  = 4
    HP_BOX_Y  = 4
    HP_BOX_W  = 60
    HP_BOX_H  = 20

    def __init__(self, karma_system=None):
        self.karma = karma_system
        self._font       = None
        self._small_font = None

        # Partículas de coração quebrado
        self.particles: list[Particle] = []

        # Indicador de interação
        self.interaction_text  = ""
        self.interaction_timer = 0

        # Progresso de altares (TrailScene)
        self._altar_count = -1    # -1 = não exibir
        self._altar_total = 3

        # Label de cena (top-right)
        self._scene_label = ""

        # Animação de dano — pulse no HUD
        self._damage_timer  = 0   # decrementado em update()
        self._prev_hp       = -1  # para detectar mudança de HP

    # ── Inicialização ──────────────────────────────────────────────────────────

    def _init_fonts(self):
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("Courier New", 11, bold=True)
            except Exception:
                self._font = pygame.font.Font(None, 14)
        if self._small_font is None:
            try:
                self._small_font = pygame.font.SysFont("Courier New", 10)
            except Exception:
                self._small_font = pygame.font.Font(None, 12)

    # ── API pública ────────────────────────────────────────────────────────────

    def notify_damage(self) -> None:
        """Cenas chamam isso quando player toma dano — ativa pulse no HUD."""
        self._damage_timer = 22
        # Emite partículas de coração no hp atual (calculado externamente)
        for i in range(3):
            self.emit_heart_break(i)

    def set_scene_label(self, text: str) -> None:
        """Define o label de ato/cena exibido no topo-direito."""
        self._scene_label = text

    def set_altar_progress(self, count: int, total: int = 3) -> None:
        """TrailScene atualiza isso todo frame para exibir o contador de altares."""
        self._altar_count = count
        self._altar_total = total

    def clear_altar_progress(self) -> None:
        """Remove o contador de altares do HUD."""
        self._altar_count = -1

    def show_interaction(self, text: str) -> None:
        self.interaction_text  = text
        self.interaction_timer = 5

    def emit_heart_break(self, heart_index: int) -> None:
        """Partículas quando um coração quebra."""
        import random
        hx = self.HP_BOX_X + 8 + heart_index * 16
        hy = self.HP_BOX_Y + 6
        for _ in range(4):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            p = Particle(
                hx, hy, P["heart_red"],
                math.cos(angle) * speed,
                math.sin(angle) * speed - 1.0,
                life=25, size=2,
            )
            self.particles.append(p)

    # ── Update ─────────────────────────────────────────────────────────────────

    def update(self) -> None:
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()
        if self.interaction_timer > 0:
            self.interaction_timer -= 1
        if self._damage_timer > 0:
            self._damage_timer -= 1

    # ── Draw ───────────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface, player_hp: int, player_max_hp: int = 3) -> None:
        self._init_fonts()
        self._draw_hp_area(surf, player_hp, player_max_hp)
        self._draw_altar_counter(surf)
        self._draw_scene_label(surf)
        self._draw_interaction(surf)
        # Partículas de coração (renderizadas sem offset de câmera)
        for p in self.particles:
            p.draw(surf)

    def _draw_hp_area(self, surf: pygame.Surface, hp: int, max_hp: int) -> None:
        """Caixa de HP com corações e efeito de shake ao tomar dano."""
        # Shake horizontal senoidal quando damage_timer ativo
        shake = 0
        if self._damage_timer > 0:
            shake = int(math.sin(self._damage_timer * 1.9) * 2)

        bx = self.HP_BOX_X + shake
        by = self.HP_BOX_Y

        # Fundo
        hud_bg = pygame.Surface((self.HP_BOX_W, self.HP_BOX_H))
        hud_bg.set_alpha(180)
        hud_bg.fill(P["hud_bg"])
        surf.blit(hud_bg, (bx, by))

        # Flash vermelho sobre o fundo quando damage ativo
        if self._damage_timer > 0:
            intensity = min(120, self._damage_timer * 8)
            flash = pygame.Surface((self.HP_BOX_W, self.HP_BOX_H), pygame.SRCALPHA)
            flash.fill((200, 30, 30, intensity))
            surf.blit(flash, (bx, by))

        # Borda: dourada normal, vermelha pulsante quando dano
        border_col = (220, 60, 60) if self._damage_timer > 0 else GOLD
        pygame.draw.rect(surf, border_col, (bx, by, self.HP_BOX_W, self.HP_BOX_H), 1)

        # Corações
        for i in range(max_hp):
            _draw_heart(surf, bx + 4 + i * 16, by + 4, full=(i < hp))

    def _draw_altar_counter(self, surf: pygame.Surface) -> None:
        """Exibe progresso dos altares apenas quando set_altar_progress foi chamado."""
        if self._altar_count < 0:
            return

        n     = self._altar_count
        total = self._altar_total
        done  = (n >= total)

        # Badge abaixo da caixa de HP
        bx = self.HP_BOX_X
        by = self.HP_BOX_Y + self.HP_BOX_H + 3
        bw = self.HP_BOX_W
        bh = 14

        bg = pygame.Surface((bw, bh))
        bg.set_alpha(170)
        bg.fill(P["hud_bg"])
        surf.blit(bg, (bx, by))

        border_col = (80, 200, 100) if done else GOLD
        pygame.draw.rect(surf, border_col, (bx, by, bw, bh), 1)

        # Ícones: círculos cheios/vazios para cada altar
        dot_r  = 3
        dot_y  = by + bh // 2
        dot_spacing = 10
        total_dots_w = total * dot_spacing - (dot_spacing - dot_r * 2)
        start_x = bx + (bw - total_dots_w) // 2 + dot_r

        for i in range(total):
            cx = start_x + i * dot_spacing
            if i < n:
                pygame.draw.circle(surf, (220, 180, 60), (cx, dot_y), dot_r)
            else:
                pygame.draw.circle(surf, (80, 70, 50), (cx, dot_y), dot_r)
                pygame.draw.circle(surf, (140, 120, 80), (cx, dot_y), dot_r, 1)

        # Contador numérico à direita
        label = self._small_font.render(f"{n}/{total}", True,
                                        (100, 220, 120) if done else (180, 160, 100))
        surf.blit(label, (bx + bw - label.get_width() - 4, by + 2))

    def _draw_scene_label(self, surf: pygame.Surface) -> None:
        """Label de ato no topo-direito — sutil, semi-transparente."""
        if not self._scene_label:
            return
        label = self._small_font.render(self._scene_label, True, (180, 160, 120))
        lw = label.get_width()
        lh = label.get_height()
        bx = SCREEN_W - lw - 10
        by = 6
        bg = pygame.Surface((lw + 6, lh + 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 100))
        surf.blit(bg, (bx - 3, by - 1))
        label.set_alpha(160)
        surf.blit(label, (bx, by))

    def _draw_interaction(self, surf: pygame.Surface) -> None:
        """Prompt de interação centralizado acima do diálogo."""
        if self.interaction_timer <= 0 or not self.interaction_text:
            return
        text = f"[X] {self.interaction_text}"
        ts = self._small_font.render(text, True, GOLD)
        bg = pygame.Surface((ts.get_width() + 8, ts.get_height() + 4))
        bg.fill(P["hud_bg"])
        bg.set_alpha(200)
        bx = (SCREEN_W - bg.get_width()) // 2
        by = SCREEN_H - 110
        surf.blit(bg, (bx, by))
        pygame.draw.rect(surf, GOLD, (bx, by, bg.get_width(), bg.get_height()), 1)
        surf.blit(ts, (bx + 4, by + 2))
