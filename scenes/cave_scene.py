# scenes/cave_scene.py — Ato 3: Cavernas da Pedra

import pygame
import math
import random
from settings import (
    SCREEN_W, SCREEN_H, TILE_SIZE, PALETTE_CAVE as C, BLACK, GOLD
)
from systems.tilemap import Tilemap
from systems.dialogue import DialogueBox, ChoiceBox, SystemMessage
from systems.hud import HUD
from entities.player import Player
from entities.bat_enemy import BatEnemy
from entities.guardian_statue import GuardianStatue
from core.camera import Camera
from art.fx import ParticleSystem, ScreenEffects


def _build_cave_map():
    COLS = 82
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

    # Plataformas de pedra de caverna (câmara da memória + área do guardião)
    platforms = [
        (range(4,  12),  14),
        (range(14, 20),  12),
        (range(22, 28),  15),
        (range(30, 36),  13),
        (range(38, 44),  11),
        (range(46, 52),  14),
        (range(54, 60),  12),
        (range(62, 68),  15),   # área do guardião
        (range(70, 76),  13),
        (range(76, 82),  11),   # câmara final / Iracema
    ]
    for cols, row in platforms:
        for col in cols:
            if 0 <= col < COLS:
                data[row][col] = 10  # rocha_glow
                if row + 1 < ROWS:
                    data[row+1][col] = 9

    # Cristais âmbar espalhados
    crystals = [
        (6, 17), (15, 11), (25, 14), (33, 12),
        (42, 10), (50, 13), (57, 11), (65, 12),
        (73, 10), (79, 13),
    ]
    for col, row in crystals:
        if 0 <= col < COLS and 0 <= row < ROWS:
            data[row][col] = 11  # crystal

    # Pilares (paredes laterais)
    for col in [0, 1, 80, 81]:
        for row in range(ROWS):
            data[row][col] = 9

    # Posições dos registros na câmara da memória (cols 6-45)
    registro_positions = [(8, 17), (22, 14), (38, 12)]

    return data, COLS, ROWS, registro_positions


class RegistroCaverna:
    """Inscrição de pedra na câmara da memória — idêntica à da trilha."""
    W = 12
    H = 16

    def __init__(self, x, y, key):
        self.x    = float(x)
        self.y    = float(y)
        self.key  = key
        self.read = False
        self.time = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self):
        self.time += 1

    def draw(self, surf, cam_x, cam_y):
        from settings import PALETTE_CAVE as C
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if not (-20 < sx < SCREEN_W + 20):
            return
        col     = (80, 120, 100) if not self.read else (50, 75, 60)
        col_top = (60, 90,  75)  if not self.read else (40, 60, 48)
        pygame.draw.rect(surf, col,     (sx,   sy + 4, self.W, self.H - 4))
        pygame.draw.rect(surf, col_top, (sx+2, sy,     self.W - 4, 6))
        glyph = (80, 200, 160) if not self.read else (40, 100, 80)
        for row in range(3):
            pygame.draw.line(surf, glyph,
                             (sx + 2, sy + 7 + row * 3),
                             (sx + self.W - 2, sy + 7 + row * 3))
        if not self.read:
            pulse = int(abs(math.sin(self.time * 0.07)) * 55) + 30
            gsurf = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (80, 200, 160, pulse), (11, 11), 11)
            surf.blit(gsurf, (sx - 5, sy - 5))


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
    WORLD_COLS = 82
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
        self._camara_hint_shown = False

    def on_enter(self):
        self._setup()

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def _setup(self):
        map_data, cols, rows, registro_positions = _build_cave_map()
        self.tilemap   = Tilemap(map_data)
        self.camera    = Camera(self.WORLD_W, self.WORLD_H)
        self.particles = ParticleSystem()
        self.fx        = ScreenEffects(SCREEN_W, SCREEN_H)
        self.dialogue    = DialogueBox()
        self.choice_box  = ChoiceBox()
        self.sys_msg     = SystemMessage()
        self.hud       = HUD(self.karma)
        self.hud.set_scene_label("ATO 3 — CAVERNA")
        self.time      = 0
        self._paused   = False
        self._transitioning = False
        self._transition_timer = 0
        self._camara_hint_shown = False

        # Player
        start_y = 17 * TILE_SIZE - Player.H
        self.player = Player(30, start_y, self.bus)
        if self._prev_player:
            self.player.hp = max(1, self._prev_player.hp)

        # Inimigos: morcegos espalhados pela caverna maior
        bat_y = 8 * TILE_SIZE
        self.enemies = [
            BatEnemy(160, bat_y, faster=True),
            BatEnemy(280, bat_y - 10, faster=True),
            BatEnemy(420, bat_y + 10, faster=True),
            BatEnemy(580, bat_y - 15, faster=True),
            BatEnemy(720, bat_y + 5, faster=True),
        ]

        # Registros na câmara da memória
        self.registros = [
            RegistroCaverna(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE - 16, f"camara_{i}")
            for i, pos in enumerate(registro_positions)
        ]
        self._registros_read = 0

        # Guardião estátua (mini-boss) — mais afastado na caverna expandida
        guardian_y = 17 * TILE_SIZE - 44
        self.guardian = GuardianStatue(660, guardian_y)
        self._guardian_fight_started = False
        self._guardian_death_time    = -1

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
        if self.hud.death_active:
            if event.type == pygame.KEYDOWN:
                if self.hud._showing_controls:
                    if event.key in (pygame.K_c, pygame.K_ESCAPE):
                        self.hud.hide_controls()
                elif self.hud.death_ready_for_input:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.hud.hide_death()
                        self._setup()
                    elif event.key == pygame.K_ESCAPE:
                        self.hud.hide_death()
                        self._go_to_menu()
                    elif event.key == pygame.K_c:
                        self.hud.show_controls()
            return
        if self.dialogue.active:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_x, pygame.K_k, pygame.K_RETURN, pygame.K_SPACE):
                self.dialogue.advance()
            return
        # ChoiceBox tem prioridade sobre input de movimento
        if self.choice_box.active:
            self.choice_box.handle_event(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._paused = not self._paused
                self.hud.set_pause(self._paused)
            if event.key == pygame.K_m and self._paused:
                self._paused = False
                self.hud.set_pause(False)
                self._go_to_menu()
            if event.key == pygame.K_RETURN and self._paused:
                self._paused = False
                self.hud.set_pause(False)
            if event.key in (pygame.K_x, pygame.K_k) and not self._paused:
                self._try_interact_registro()

    def update(self):
        if not self._ready or self._paused:
            return
        if self.hud.death_active:
            self.hud.update()
            return

        self.time += 1

        if not self.dialogue.active and not self.choice_box.active:
            self.player.update(self.input.poll(), self.tilemap, self.particles)

        # Morcegos
        for enemy in self.enemies:
            enemy.update(self.tilemap, self.player.rect)
            if enemy.alive and enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(1):
                    self.fx.camera_shake(4, 12)
                    self.hud.notify_damage()

        # Ataque contra morcegos
        if self.player.attack_active:
            ar = self.player.attack_rect
            for enemy in self.enemies:
                if enemy.alive and ar.colliderect(enemy.rect):
                    if enemy.take_damage(1):
                        enemy.emit_death_particles(self.particles)

        self.enemies = [e for e in self.enemies if e.alive]

        # Hint da câmara da memória ao entrar na zona dos registros
        if not self._camara_hint_shown and self.player.x > 80:
            self._camara_hint_shown = True
            self.sys_msg.show("Câmara da Memória — [X] para ler as inscrições", 200)

        # Guardião — diálogo de intro antes de acordar (posição ajustada)
        if not self._guardian_fight_started and self.player.x > 560:
            self._guardian_fight_started = True
            self.dialogue.open("guardiao_intro", on_close=self._on_guardian_intro_close)

        if not hasattr(self, '_guardian_intro_done'):
            self._guardian_intro_done = False

        if self._guardian_fight_started and not self.guardian.defeated and getattr(self, "_guardian_intro_done", False):
            self.guardian.update(self.tilemap, self.player.rect)

            # Transição para fase 2 — feedback visual imediato
            if self.guardian.phase_just_changed:
                self.fx.camera_shake(6, 20)
                cx = int(self.guardian.x + self.guardian.w // 2)
                cy = int(self.guardian.y + self.guardian.h // 2)
                self.particles.emit_phase_burst(cx, cy)
                self.sys_msg.show("O Guardião entrou em fúria!", 100)

            # Colisão corpo a corpo — knockback só quando dano aceito (respeita iframes)
            if self.guardian.rect.colliderect(self.player.rect):
                if self.player.take_damage(1):
                    self.guardian.knockback_player(self.player)
                    self.fx.camera_shake(3, 8)
                    self.hud.notify_damage()

            # Ondas de choque fase 2
            if self.guardian.check_shockwave_hit(self.player.rect):
                if self.player.take_damage(1):
                    self.fx.camera_shake(5, 15)
                    self.hud.notify_damage()

            # Ataque do player contra guardião
            if self.player.attack_active:
                ar = self.player.attack_rect
                if ar.colliderect(self.guardian.rect):
                    self.guardian.take_damage(1)

            # Guardião derrotado
            if self.guardian.hp <= 0 and not self.guardian.defeated:
                self.guardian.defeat()
                self._guardian_defeated = True
                self._guardian_death_time = self.time
                self.karma.ajudou_espirito()
                # Explosão de partículas na derrota
                cx = int(self.guardian.x + self.guardian.w // 2)
                cy = int(self.guardian.y + self.guardian.h // 2)
                self.particles.emit_boss_death(cx, cy)
                self.fx.camera_shake(8, 25)
                self.dialogue.open("guardiao", on_close=self._on_guardian_dialogue_close)

        # Iracema encontro — só abre DEPOIS que o guardião foi derrotado
        if not self._iracema_shown and self.guardian.defeated and self.player.x > 900:
            self._iracema_shown = True
            self.dialogue.open("iracema_proposta", on_close=self._on_iracema_proposta_close)

        # Registros da câmara da memória
        for registro in self.registros:
            registro.update()

        # Indicador de interação com registros
        if not self.dialogue.active and not self.choice_box.active:
            pr = self.player.rect
            for registro in self.registros:
                if abs(pr.centerx - registro.rect.centerx) < 35 and abs(pr.centery - registro.rect.centery) < 45:
                    if not registro.read:
                        self.hud.show_interaction("ler inscrição")
                    break

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

        if self.player.dead and not self.hud.death_active:
            self.hud.show_death()

        if self.player.x < 0:
            self.player.x = 0

    def _try_interact_registro(self):
        if self.dialogue.active or self.choice_box.active:
            return
        pr = self.player.rect
        for registro in self.registros:
            if abs(pr.centerx - registro.rect.centerx) < 35 and abs(pr.centery - registro.rect.centery) < 45:
                if not registro.read:
                    registro.read = True
                    self._registros_read += 1
                    self.karma.leu_registro()
                    self.dialogue.open(registro.key)
                    self.sys_msg.show("Câmara da Memória — inscrição lida.", 90)
                return

    def _on_guardian_intro_close(self):
        self._guardian_intro_done = True
        self.sys_msg.show("[Z] atacar — pule as ondas de choque!", 160)

    def _on_guardian_dialogue_close(self):
        self.sys_msg.show("O guardião se dissipou em luz...", 150)

    # ── Fluxo do encontro com Iracema ─────────────────────────────────────────

    def _on_iracema_proposta_close(self):
        """Após o diálogo da proposta, abre a ChoiceBox."""
        self.choice_box.open([
            ("Aceitar o trato",  self._iracema_aceitar),
            ("Recusar o trato",  self._iracema_recusar),
        ])

    def _iracema_aceitar(self):
        """Player honrou o trato: +sabedoria, abre resposta da Iracema."""
        self.karma.aceitou_trato_honrou()
        self.karma.conversou_com_npc()   # sapiência por escutar e aceitar
        self.dialogue.open("iracema_aceita", on_close=self._on_iracema_close)

    def _iracema_recusar(self):
        """Player recusou: karma neutro para dívida, abre resposta de recusa."""
        self.karma.recusou_trato()
        self.dialogue.open("iracema_recusa", on_close=self._on_iracema_close)

    def _on_iracema_close(self):
        """Após qualquer resposta de Iracema, encaminha para o final."""
        self.sys_msg.show("Câmara do Tesouro à frente...", 120)
        self._ending_triggered = True

    def _show_ending(self):
        """Mostra tela de final baseada no karma."""
        from scenes.ending_scene import EndingScene
        final = self.karma.final_type
        self.scene_manager.replace(
            EndingScene(self.scene_manager, self.bus, self.karma, self.input, final)
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

        # Registros da câmara da memória
        for registro in self.registros:
            registro.draw(surf, cam_x, cam_y)

        # Guardião
        if self._guardian_fight_started and not self.guardian.defeated and getattr(self, "_guardian_intro_done", False):
            self.guardian.draw(surf, cam_x, cam_y)
        elif self.guardian.defeated:
            # Partículas residuais de luz nos primeiros 120 frames após derrota
            elapsed = self.time - self._guardian_death_time
            if self._guardian_death_time >= 0 and elapsed < 120 and self.time % 3 == 0:
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
        self.choice_box.draw(surf)   # renderiza acima do dialogue quando ativo
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

