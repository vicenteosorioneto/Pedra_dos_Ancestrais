# scenes/cave_scene.py — Ato 3: Cavernas da Pedra

import pygame
import math
import random
from settings import (
    SCREEN_W, SCREEN_H, TILE_SIZE, PALETTE_CAVE as C, BLACK, GOLD
)
from systems.tilemap import Tilemap
from systems.dialogue import DialogueBox, SystemMessage
from systems.hud import HUD
from entities.player import Player
from entities.bat_enemy import BatEnemy
from entities.guardian_statue import GuardianStatue
from core.camera import Camera
from art.fx import ParticleSystem, ScreenEffects


def _build_cave_map():
    COLS = 60
    ROWS = 22
    data = [[0] * COLS for _ in range(ROWS)]

    # Teto e chão
    for col in range(COLS):
        data[0][col]  = 9   # teto
        data[1][col]  = 9
        data[18][col] = 9   # chão
        data[19][col] = 9
        data[20][col] = 9
        data[21][col] = 9

    # Plataformas de pedra de caverna
    platforms = [
        (range(4, 12),   14),
        (range(14, 20),  12),
        (range(22, 28),  15),
        (range(30, 36),  13),
        (range(38, 44),  11),
        (range(46, 52),  14),
        (range(54, 60),  12),
    ]
    for cols, row in platforms:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 10  # rocha_glow
                if row + 1 < ROWS:
                    data[row+1][col] = 9

    # Cristais âmbar espalhados
    crystals = [(6, 17), (15, 11), (25, 14), (33, 12), (42, 10), (50, 13), (57, 11)]
    for col, row in crystals:
        if 0 <= col < COLS and 0 <= row < ROWS:
            data[row][col] = 11  # crystal

    # Pilares (paredes laterais dos grupos)
    for col in [0, 1, 58, 59]:
        for row in range(ROWS):
            data[row][col] = 9

    return data, COLS, ROWS


def _draw_cave_bg(surf, cam_x):
    """Fundo profundo da caverna."""
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        r = int(10  + t * 15)
        g = int(5   + t * 10)
        b = int(20  + t * 25)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W, y))


def _draw_cave_details(surf, cam_x, cam_y, time):
    """Estalactites e efeitos ambientes."""
    offset = cam_x * 0.8
    # Estalactites simplificadas
    for i in range(0, SCREEN_W + 40, 25):
        bx = int((i - offset) % (SCREEN_W + 40)) - 20
        h  = 10 + (i % 5) * 4
        color_idx = i % 3
        col = (C["rock_cave"] if color_idx == 0 else
               C["rock_glow"] if color_idx == 1 else
               C["bg_mid"])
        pts = [(bx - 4, -cam_y), (bx + 4, -cam_y), (bx, -cam_y + h)]
        if -cam_y < SCREEN_H:
            pygame.draw.polygon(surf, col, [(p[0], max(0, p[1])) for p in pts])

    # Pontos bioluminescentes pulsando
    biol = C["biolum"]
    for i in range(0, SCREEN_W + 40, 60):
        bx = int((i * 7 - cam_x * 0.6) % (SCREEN_W + 60)) - 30
        by = SCREEN_H - 20 + int(math.sin(time * 0.05 + i) * 5)
        alpha = 120 + int(math.sin(time * 0.08 + i * 0.3) * 80)
        gsurf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(gsurf, (*biol, alpha), (5, 5), 5)
        surf.blit(gsurf, (bx, by))


class CaveScene:
    WORLD_COLS = 60
    WORLD_ROWS = 22
    WORLD_W    = WORLD_COLS * TILE_SIZE
    WORLD_H    = WORLD_ROWS * TILE_SIZE

    def __init__(self, scene_manager, bus, karma, input_manager, player=None):
        self.scene_manager = scene_manager
        self.bus           = bus
        self.karma         = karma
        self.input         = input_manager
        self._prev_player  = player
        self._ready        = False
        self._guardian_defeated = False
        self._ending_triggered  = False
        self._iracema_shown     = False

    def on_enter(self):
        self._setup()

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def _setup(self):
        map_data, cols, rows = _build_cave_map()
        self.tilemap   = Tilemap(map_data)
        self.camera    = Camera(self.WORLD_W, self.WORLD_H)
        self.particles = ParticleSystem()
        self.fx        = ScreenEffects(SCREEN_W, SCREEN_H)
        self.dialogue  = DialogueBox()
        self.sys_msg   = SystemMessage()
        self.hud       = HUD(self.karma)
        self.time      = 0
        self._paused   = False
        self._transitioning = False
        self._transition_timer = 0

        # Player
        start_y = 17 * TILE_SIZE - Player.H
        self.player = Player(30, start_y, self.bus)
        if self._prev_player:
            self.player.hp = max(1, self._prev_player.hp)

        # Inimigos: morcegos mais rápidos + guardião
        bat_y = 8 * TILE_SIZE
        self.enemies = [
            BatEnemy(180, bat_y, faster=True),
            BatEnemy(300, bat_y - 10, faster=True),
            BatEnemy(440, bat_y + 10, faster=True),
        ]

        # Guardião estátua (mini-boss)
        guardian_y = 17 * TILE_SIZE - 44
        self.guardian = GuardianStatue(500, guardian_y)
        self._guardian_fight_started = False

        # Fontes de luz ambiente
        self._light_sources = [
            (col * TILE_SIZE, 14 * TILE_SIZE, 40, C["amber_glow"])
            for col in range(8, self.WORLD_COLS, 15)
        ]

        # Vinheta de caverna mais intensa
        self._vignette_intensity = 100

        self.fx.fade_in(frames=25)
        self._ready = True

    def handle_event(self, event):
        if not self._ready:
            return
        if self.dialogue.active:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_x, pygame.K_k, pygame.K_RETURN, pygame.K_SPACE):
                self.dialogue.advance()
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._paused = not self._paused

    def update(self):
        if not self._ready or self._paused:
            return

        self.time += 1

        if not self.dialogue.active:
            self.player.update(self.input.poll(), self.tilemap, self.particles)

        # Morcegos
        for enemy in self.enemies:
            enemy.update(self.tilemap, self.player.rect)
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(1):
                    self.fx.camera_shake(4, 12)

        # Ataque contra morcegos
        if self.player.attack_active:
            ar = self.player.attack_rect
            for enemy in self.enemies:
                if enemy.alive and ar.colliderect(enemy.rect):
                    if enemy.take_damage(1):
                        enemy.emit_death_particles(self.particles)

        self.enemies = [e for e in self.enemies if e.alive]

        # Guardião — inicia luta quando player se aproxima
        if not self._guardian_fight_started and self.player.x > 400:
            self._guardian_fight_started = True
            self.sys_msg.show("Um guardião bloqueia o caminho!", 120)

        if self._guardian_fight_started and not self.guardian.defeated:
            self.guardian.update(self.tilemap, self.player.rect)

            # Colisão corpo a corpo
            if self.guardian.rect.colliderect(self.player.rect):
                self.guardian.knockback_player(self.player)

            # Ondas de choque fase 2
            if self.guardian.check_shockwave_hit(self.player.rect):
                if self.player.take_damage(1):
                    self.fx.camera_shake(5, 15)

            # Ataque do player contra guardião
            if self.player.attack_active:
                ar = self.player.attack_rect
                if ar.colliderect(self.guardian.rect):
                    self.guardian.take_damage(1)

            # Guardião derrotado
            if self.guardian.hp <= 0 and not self.guardian.defeated:
                self.guardian.defeat()
                self._guardian_defeated = True
                self.karma.ajudou_espirito()
                # Diálogo do guardião
                self.dialogue.open("guardiao", on_close=self._on_guardian_dialogue_close)

        # Iracema encontro (quando avança muito)
        if not self._iracema_shown and self.player.x > 700:
            self._iracema_shown = True
            self.dialogue.open("iracema", on_close=self._on_iracema_close)

        self.dialogue.update()
        self.sys_msg.update()
        self.particles.update()
        self.fx.update()
        self.hud.update()

        self.camera.update(
            self.player.x + Player.W // 2,
            self.player.y + Player.H // 2
        )

        # Transição para final
        if self._ending_triggered and not self._transitioning:
            self._transitioning = True
            self._transition_timer = 60
            self.fx.fade_out(40)

        if self._transitioning:
            self._transition_timer -= 1
            if self._transition_timer <= 0:
                self._transitioning = False
                self._show_ending()

        if self.player.x < 0:
            self.player.x = 0

    def _on_guardian_dialogue_close(self):
        self.sys_msg.show("O guardião se dissipou em luz...", 150)

    def _on_iracema_close(self):
        self.sys_msg.show("Câmara do Tesouro à frente...", 120)
        # Após algum tempo, trigger de final
        self._ending_triggered = True

    def _show_ending(self):
        """Mostra tela de final baseada no karma."""
        final = self.karma.final_type
        self.scene_manager.replace(
            EndingScene(self.scene_manager, self.karma, final)
        )

    def draw(self, surf):
        if not self._ready:
            surf.fill((0, 0, 0))
            return

        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)

        # Fundo caverna
        _draw_cave_bg(surf, cam_x)
        _draw_cave_details(surf, cam_x, cam_y, self.time)

        # Tilemap
        self.tilemap.draw(surf, cam_x, cam_y, SCREEN_W, SCREEN_H)

        # Inimigos
        for enemy in self.enemies:
            enemy.draw(surf, cam_x, cam_y)

        # Guardião
        if self._guardian_fight_started and not self.guardian.defeated:
            self.guardian.draw(surf, cam_x, cam_y)
        elif self.guardian.defeated:
            # Partículas residuais de luz
            if self.time % 3 == 0 and self.time < self.time + 120:
                gx = self.guardian.x + self.guardian.w // 2
                gy = self.guardian.y + self.guardian.h // 2
                self.particles.emit_altar(gx, gy)

        # Partículas
        self.particles.draw(surf, cam_x, cam_y)

        # Player
        self.player.draw(surf, cam_x, cam_y)

        # HUD
        self.hud.draw(surf, self.player.hp, self.player.max_hp)
        self.dialogue.draw(surf)
        self.sys_msg.draw(surf)

        # Vinheta de caverna
        vsurf = pygame.Surface((SCREEN_W, SCREEN_H))
        vsurf.fill((0, 0, 0))
        vsurf.set_alpha(self._vignette_intensity)
        # Recorte oval no centro
        center_surf = pygame.Surface((SCREEN_W // 2, SCREEN_H // 2))
        center_surf.fill((0, 0, 0))
        pygame.draw.ellipse(center_surf, (0, 0, 0), center_surf.get_rect())
        surf.blit(vsurf, (0, 0))

        self.fx.draw(surf)


# ── Tela de Final ─────────────────────────────────────────────────────────────

class EndingScene:
    def __init__(self, scene_manager, karma, final_type):
        self.scene_manager = scene_manager
        self.karma         = karma
        self.final_type    = final_type
        self.time          = 0
        self._font_title   = None
        self._font_body    = None
        self._blink        = True
        self._blink_timer  = 0

    def on_enter(self):
        try:
            self._font_title = pygame.font.SysFont("Courier New", 18, bold=True)
            self._font_body  = pygame.font.SysFont("Courier New", 11)
        except Exception:
            self._font_title = pygame.font.Font(None, 22)
            self._font_body  = pygame.font.Font(None, 14)

    def on_exit(self): pass
    def on_resume(self): pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                # Volta ao início
                from scenes.intro_scene import IntroScene
                from systems.karma import KarmaSystem
                new_karma = KarmaSystem(self.bus)
                self.scene_manager.replace(IntroScene(self.scene_manager, self.bus, new_karma, self.input))

    def update(self):
        self.time += 1
        self._blink_timer += 1
        if self._blink_timer >= 40:
            self._blink_timer = 0
            self._blink = not self._blink

    def draw(self, surf):
        # Fundo
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

        # Títulos por final
        if self.final_type == "verdadeiro":
            title_text = "O LEGADO DOS ANCESTRAIS"
            body_lines = [
                "Caio descobriu que o verdadeiro tesouro",
                "não eram as riquezas da pedra —",
                "mas a história de seu povo,",
                "e a força que carregava dentro de si.",
                "",
                "Ele voltou para a vila com a sabedoria",
                "dos que vieram antes.",
                "E a Pedra dos Ancestrais descansou em paz.",
            ]
            title_col = (220, 200, 80)
        elif self.final_type == "ruim":
            title_text = "CONSUMIDO PELA PEDRA"
            body_lines = [
                "A ganância de Caio o cegou.",
                "Ele tocou o tesouro...",
                "e a Pedra não o deixou partir.",
                "",
                "Dizem que à noite,",
                "ainda é possível ouvir seus passos",
                "ecoando nas câmaras de pedra.",
            ]
            title_col = (200, 60, 40)
        else:
            title_text = "UM FARDO LEVADO"
            body_lines = [
                "Caio saiu da pedra diferente.",
                "Não sábio, não condenado —",
                "apenas... mudado.",
                "",
                "A lenda continua.",
                "Como todas as lendas do sertão.",
            ]
            title_col = (160, 150, 200)

        # Título
        title = self._font_title.render(title_text, True, title_col)
        shadow = self._font_title.render(title_text, True, (20, 10, 5))
        tx = (SCREEN_W - title.get_width()) // 2
        surf.blit(shadow, (tx + 2, 32))
        surf.blit(title,  (tx, 30))

        # Separador
        pygame.draw.line(surf, title_col, (SCREEN_W//4, 52), (3*SCREEN_W//4, 52), 1)

        # Corpo do texto
        for i, line in enumerate(body_lines):
            if not line:
                continue
            alpha = min(255, (self.time - i * 5) * 10) if self.time > i * 5 else 0
            if alpha <= 0:
                continue
            ls = self._font_body.render(line, True, (200, 190, 170))
            ls.set_alpha(alpha)
            lx = (SCREEN_W - ls.get_width()) // 2
            surf.blit(ls, (lx, 68 + i * 16))

        # Karma resumo
        summ = self.karma.get_summary()
        stats = [
            f"Coragem: {'█' * summ['coragem']}{'░' * (5 - summ['coragem'])}",
            f"Sabedoria: {'█' * summ['sabedoria']}{'░' * (5 - summ['sabedoria'])}",
            f"Ganância: {'█' * summ['ganancia']}{'░' * (5 - summ['ganancia'])}",
        ]
        for i, stat in enumerate(stats):
            ss = self._font_body.render(stat, True, (160, 140, 100))
            surf.blit(ss, (20, SCREEN_H - 50 + i * 13))

        # Pressione ENTER
        if self._blink:
            ps = self._font_body.render("Pressione ENTER para jogar novamente", True, (180, 160, 120))
            px = (SCREEN_W - ps.get_width()) // 2
            surf.blit(ps, (px, SCREEN_H - 18))
