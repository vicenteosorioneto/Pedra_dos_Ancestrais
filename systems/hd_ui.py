import math
import pygame

from settings import GOLD


WHITE = (226, 218, 198)
MUTED = (174, 154, 112)
GREEN = (105, 225, 130)
RED = (210, 52, 48)
PANEL = (18, 7, 6, 212)
BORDER = (70, 52, 24)


class HDUIRenderer:
    def __init__(self):
        self._fonts = {}

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self._fonts:
            try:
                self._fonts[key] = pygame.font.SysFont("Courier New", size, bold=bold)
            except Exception:
                self._fonts[key] = pygame.font.Font(None, size + 6)
        return self._fonts[key]

    def draw(self, surf, scene):
        if scene.__class__.__name__ == "IntroScene":
            self._draw_intro(surf, scene)
            return

        hud = getattr(scene, "hud", None)
        if hud:
            self._draw_hud(surf, scene, hud)
            if getattr(hud, "_paused", False):
                self._draw_pause(surf, hud)
            if getattr(hud, "death_active", False):
                self._draw_death(surf, hud)

        dialogue = getattr(scene, "dialogue", None)
        if dialogue and getattr(dialogue, "active", False):
            self._draw_dialogue(surf, dialogue)

        choice = getattr(scene, "choice_box", None)
        if choice and getattr(choice, "active", False):
            self._draw_choice(surf, choice)

        sys_msg = getattr(scene, "sys_msg", None)
        if sys_msg and getattr(sys_msg, "timer", 0) > 0:
            self._draw_system_message(surf, sys_msg)

    def _panel(self, surf, rect, border=GOLD, alpha=212):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((18, 7, 6, alpha))
        surf.blit(panel, rect.topleft)
        pygame.draw.rect(surf, BORDER, rect, 2)
        pygame.draw.rect(surf, border, rect.inflate(-4, -4), 2)

    def _fit(self, font, text, max_w):
        if font.size(text)[0] <= max_w:
            return text
        suffix = "..."
        while text and font.size(text + suffix)[0] > max_w:
            text = text[:-1]
        return text + suffix if text else suffix

    def _wrap(self, font, text, max_w):
        words = text.split(" ")
        lines = []
        cur = ""
        for word in words:
            test = (cur + " " + word).strip()
            if cur and font.size(test)[0] > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = test
        if cur:
            lines.append(cur)
        return lines

    def _draw_heart(self, surf, x, y, full=True):
        color = (225, 48, 58) if full else (76, 38, 34)
        outline = (38, 14, 12)
        pts = [
            (x + 12, y + 30), (x + 4, y + 20), (x + 2, y + 10),
            (x + 8, y + 4), (x + 14, y + 8), (x + 20, y + 4),
            (x + 28, y + 10), (x + 26, y + 20),
        ]
        pygame.draw.polygon(surf, outline, pts)
        inner = [(px, py - 2) for px, py in pts]
        pygame.draw.polygon(surf, color, inner)
        if full:
            pygame.draw.circle(surf, (255, 122, 112), (x + 10, y + 11), 3)

    def _draw_hud(self, surf, scene, hud):
        w, h = surf.get_size()
        safe_x, safe_y = 48, 42

        player = getattr(scene, "player", None)
        hp = getattr(player, "hp", 0)
        max_hp = getattr(player, "max_hp", 3)
        hp_rect = pygame.Rect(safe_x, safe_y, 190, 58)
        self._panel(surf, hp_rect, alpha=196)
        for i in range(max_hp):
            self._draw_heart(surf, safe_x + 18 + i * 34, safe_y + 15, i < hp)

        objectives = list(getattr(hud, "_objectives", []) or [])
        if objectives:
            title_font = self.font(26, True)
            row_font = self.font(23)
            rows = []
            for item in objectives:
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

            panel_w = min(520, max(360, max(row_font.size(t)[0] for t, _ in rows) + 44))
            panel_h = 54 + len(rows) * 34
            rect = pygame.Rect(safe_x, safe_y + 72, panel_w, panel_h)
            self._panel(surf, rect, alpha=204)
            surf.blit(title_font.render("OBJETIVOS", True, GOLD), (rect.x + 20, rect.y + 15))
            for i, (text, complete) in enumerate(rows):
                color = GREEN if complete else WHITE
                fitted = self._fit(row_font, text, rect.width - 40)
                surf.blit(row_font.render(fitted, True, color), (rect.x + 20, rect.y + 52 + i * 34))

        label = getattr(hud, "_scene_label", "")
        if label:
            font = self.font(22)
            text = font.render(label, True, MUTED)
            rect = pygame.Rect(w - text.get_width() - 58, 38, text.get_width() + 28, 42)
            self._panel(surf, rect, border=BORDER, alpha=130)
            surf.blit(text, (rect.x + 14, rect.y + 10))

        if getattr(hud, "interaction_timer", 0) > 0 and getattr(hud, "interaction_text", ""):
            font = self.font(24, True)
            pulse = int(abs(math.sin(getattr(hud, "_tick", 0) * 0.08)) * 35) + 200
            color = (pulse, int(pulse * 0.82), 35)
            text = font.render(f"[X] {hud.interaction_text}", True, color)
            rect = pygame.Rect((w - text.get_width()) // 2 - 18, h - 265, text.get_width() + 36, 44)
            self._panel(surf, rect, border=color, alpha=178)
            surf.blit(text, (rect.x + 18, rect.y + 9))

    def _draw_system_message(self, surf, sys_msg):
        w, _ = surf.get_size()
        font = self.font(24, True)
        alpha = min(255, sys_msg.timer * 8, (sys_msg.max_time - sys_msg.timer) * 8)
        text = font.render(sys_msg.text, True, GOLD)
        text.set_alpha(alpha)
        rect = pygame.Rect((w - text.get_width()) // 2 - 20, 36, text.get_width() + 40, 44)
        bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, int(alpha * 0.62)))
        surf.blit(bg, rect.topleft)
        surf.blit(text, (rect.x + 20, rect.y + 9))

    def _draw_dialogue(self, surf, dialogue):
        w, h = surf.get_size()
        rect = pygame.Rect(72, h - 300, w - 144, 224)
        self._panel(surf, rect, alpha=232)

        name_font = self.font(30, True)
        body_font = self.font(28)
        small_font = self.font(22)

        x = rect.x + 34
        if getattr(dialogue, "avatar_surf", None):
            avatar = pygame.transform.scale(dialogue.avatar_surf, (112, 112))
            pygame.draw.rect(surf, (42, 30, 12), (x - 3, rect.y + 48, 118, 118))
            surf.blit(avatar, (x, rect.y + 51))
            pygame.draw.rect(surf, GOLD, (x, rect.y + 51, 112, 112), 2)
            x += 144

        if getattr(dialogue, "npc_name", ""):
            surf.blit(name_font.render(dialogue.npc_name, True, GOLD), (x, rect.y + 28))
            text_y = rect.y + 78
        else:
            text_y = rect.y + 48

        line = dialogue.lines[dialogue.current_line]
        visible = line[:int(dialogue.char_index)]
        for i, wrapped in enumerate(self._wrap(body_font, visible, rect.right - x - 70)[:3]):
            surf.blit(body_font.render(wrapped, True, WHITE), (x, text_y + i * 42))

        if int(dialogue.char_index) >= len(line):
            hint = small_font.render("[X] continuar", True, MUTED)
            surf.blit(hint, (rect.right - hint.get_width() - 34, rect.bottom - 42))

        if len(dialogue.lines) > 1:
            progress = small_font.render(f"{dialogue.current_line + 1}/{len(dialogue.lines)}", True, MUTED)
            surf.blit(progress, (rect.right - progress.get_width() - 34, rect.y + 24))

    def _draw_choice(self, surf, choice):
        w, h = surf.get_size()
        rect_h = 76 + len(choice.options) * 36
        rect = pygame.Rect(72, h - 332 - rect_h, w - 144, rect_h)
        self._panel(surf, rect, alpha=232)
        font = self.font(26)
        prompt = self.font(24, True).render("O que voce decide?", True, MUTED)
        surf.blit(prompt, (rect.x + 26, rect.y + 16))
        for i, (label, _) in enumerate(choice.options):
            prefix = "> " if i == choice.selected else "  "
            color = GOLD if i == choice.selected else WHITE
            surf.blit(font.render(prefix + label, True, color), (rect.x + 42, rect.y + 54 + i * 36))

    def _draw_pause(self, surf, hud):
        w, h = surf.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surf.blit(overlay, (0, 0))
        rect = pygame.Rect((w - 520) // 2, (h - 260) // 2, 520, 260)
        self._panel(surf, rect, alpha=238)
        title = self.font(46, True).render("PAUSADO", True, GOLD)
        surf.blit(title, ((w - title.get_width()) // 2, rect.y + 34))
        font = self.font(28)
        for i, text in enumerate(("[ENTER] Continuar", "[M] Menu principal")):
            item = font.render(text, True, WHITE if i == 0 else MUTED)
            surf.blit(item, ((w - item.get_width()) // 2, rect.y + 112 + i * 48))

    def _draw_death(self, surf, hud):
        w, h = surf.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(210, getattr(hud, "_death_alpha", 0))))
        surf.blit(overlay, (0, 0))
        if getattr(hud, "_death_timer", 0) < 40:
            return
        title = self.font(54, True).render("Caio caiu.", True, RED)
        surf.blit(title, ((w - title.get_width()) // 2, h // 2 - 105))
        subtitle = self.font(30).render("Mas a pedra espera.", True, MUTED)
        surf.blit(subtitle, ((w - subtitle.get_width()) // 2, h // 2 - 38))
        if getattr(hud, "_death_timer", 0) > 110:
            font = self.font(28, True)
            options = ["[ENTER] Tentar de novo", "[ESC] Menu principal", "[C] Ver controles"]
            for i, option in enumerate(options):
                text = font.render(option, True, GOLD)
                surf.blit(text, ((w - text.get_width()) // 2, h // 2 + 35 + i * 42))

    def _draw_intro(self, surf, scene):
        screen = getattr(scene, "_screen", "main")
        if screen == "main":
            self._draw_intro_main(surf, scene)
        elif screen == "credits":
            self._draw_intro_credits(surf)
        elif screen == "controls":
            self._draw_intro_controls(surf)
        elif screen == "options":
            self._draw_intro_options(surf, scene)

    def _draw_intro_main(self, surf, scene):
        w, h = surf.get_size()
        title_font = self.font(56, True)
        sub_font = self.font(26)
        item_font = self.font(32)
        title = title_font.render("A PEDRA DOS ANCESTRAIS", True, GOLD)
        shadow = title_font.render("A PEDRA DOS ANCESTRAIS", True, (38, 17, 0))
        surf.blit(shadow, ((w - title.get_width()) // 2 + 4, 74))
        surf.blit(title, ((w - title.get_width()) // 2, 70))
        subtitle = sub_font.render("Uma lenda do Piaui", True, (222, 186, 128))
        surf.blit(subtitle, ((w - subtitle.get_width()) // 2, 142))

        items = ["Jogar", "Creditos", "Controles", "Opcoes", "Sair"]
        selected = getattr(scene, "_sel", 0)
        panel_w = 430
        panel_h = 72 + len(items) * 58
        rect = pygame.Rect((w - panel_w) // 2, h // 2 - 12, panel_w, panel_h)
        self._panel(surf, rect, alpha=224)
        for i, item in enumerate(items):
            y = rect.y + 38 + i * 58
            is_selected = i == selected
            if is_selected:
                high = pygame.Surface((panel_w - 42, 44), pygame.SRCALPHA)
                high.fill((222, 176, 52, 42))
                surf.blit(high, (rect.x + 21, y - 6))
                color = GOLD
                cursor = self.font(32, True).render(">", True, GOLD)
                surf.blit(cursor, (rect.x + 48, y))
            else:
                color = (184, 164, 104)
            text = item_font.render(item, True, color)
            surf.blit(text, (rect.x + 102, y))

        version = self.font(20).render("v4", True, (80, 68, 42))
        surf.blit(version, (w - version.get_width() - 42, h - 48))

    def _draw_intro_panel(self, surf, title):
        w, h = surf.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 154))
        surf.blit(overlay, (0, 0))
        rect = pygame.Rect((w - 860) // 2, (h - 520) // 2, 860, 520)
        self._panel(surf, rect, alpha=238)
        title_text = self.font(42, True).render(title, True, GOLD)
        surf.blit(title_text, ((w - title_text.get_width()) // 2, rect.y + 42))
        pygame.draw.line(surf, BORDER, (rect.x + 56, rect.y + 108), (rect.right - 56, rect.y + 108), 2)
        return rect

    def _draw_intro_credits(self, surf):
        w, _ = surf.get_size()
        rect = self._draw_intro_panel(surf, "CREDITOS")
        title_font = self.font(30, True)
        body_font = self.font(27)
        lines = [
            ("A Pedra dos Ancestrais", title_font, GOLD),
            ("Codigo e mecanicas: projeto autoral em Python/Pygame", body_font, WHITE),
            ("Arte, audio e efeitos: pixel art/procedural em codigo", body_font, WHITE),
            ("Tema: plataforma narrativo no sertao brasileiro", body_font, WHITE),
            ("Build: executavel Windows fechado com PyInstaller", body_font, WHITE),
        ]
        y = rect.y + 150
        for text, font, color in lines:
            rendered = font.render(text, True, color)
            surf.blit(rendered, ((w - rendered.get_width()) // 2, y))
            y += 48
        back = self.font(24).render("[ESC / X] Voltar", True, MUTED)
        surf.blit(back, ((w - back.get_width()) // 2, rect.bottom - 70))

    def _draw_intro_controls(self, surf):
        rect = self._draw_intro_panel(surf, "CONTROLES")
        w, _ = surf.get_size()
        rows = [
            ("MOVER", "A / Setas"),
            ("PULAR", "W / Espaco"),
            ("ATACAR", "Z ou J"),
            ("INTERAGIR", "X ou K"),
            ("PAUSAR", "ESC"),
            ("CONFIRMAR", "ENTER"),
        ]
        key_font = self.font(28, True)
        val_font = self.font(28)
        y = rect.y + 138
        for action, key in rows:
            surf.blit(key_font.render(action, True, GOLD), (rect.x + 180, y))
            surf.blit(val_font.render(key, True, WHITE), (rect.x + 460, y))
            y += 48
        back = self.font(24).render("[ESC / X] Voltar", True, MUTED)
        surf.blit(back, ((w - back.get_width()) // 2, rect.bottom - 60))

    def _draw_intro_options(self, surf, scene):
        from systems.audio import get_music_volume, get_sfx_volume

        rect = self._draw_intro_panel(surf, "OPCOES")
        w, _ = surf.get_size()
        rows = [("Musica", get_music_volume()), ("Efeitos", get_sfx_volume())]
        selected = getattr(scene, "_opt_sel", 0)
        font = self.font(30)
        y = rect.y + 170
        for i, (label, value) in enumerate(rows):
            color = GOLD if i == selected else WHITE
            filled = int(round(value * 10))
            bar = "#" * filled + "-" * (10 - filled)
            text = font.render(f"{label}: [{bar}] {int(round(value * 100)):3d}%", True, color)
            surf.blit(text, ((w - text.get_width()) // 2, y))
            if i == selected:
                cursor = self.font(30, True).render(">", True, GOLD)
                surf.blit(cursor, ((w - text.get_width()) // 2 - 42, y))
            y += 64
        help_text = self.font(24).render("A/D ou setas ajusta", True, MUTED)
        surf.blit(help_text, ((w - help_text.get_width()) // 2, rect.y + 330))
        back = self.font(24).render("[ESC / X] Voltar", True, MUTED)
        surf.blit(back, ((w - back.get_width()) // 2, rect.bottom - 60))


_renderer = HDUIRenderer()


def draw_hd_ui(surf, scene):
    _renderer.draw(surf, scene)
