# core/game.py — loop principal do jogo

import pygame
import sys
from settings import (
    SCREEN_W, SCREEN_H, WINDOW_W, WINDOW_H, SCALE, FPS, TITLE
)
from core.scene_manager import SceneManager
from systems.karma import KarmaSystem


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Janela upscaled
        self.window  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(TITLE)

        # Tenta colocar ícone da janela
        try:
            from art.sprites import get_window_icon
            icon = get_window_icon()
            icon_scaled = pygame.transform.scale(icon, (32, 32))
            pygame.display.set_icon(icon_scaled)
        except Exception:
            pass

        # Surface interna de render
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()
        self.running = True

        # Gerenciadores
        self.scene_manager = SceneManager()
        self.karma         = KarmaSystem()

        # Carrega cena inicial
        from scenes.intro_scene import IntroScene
        intro = IntroScene(self.scene_manager, self.karma)
        self.scene_manager.push(intro)
        intro.on_enter()

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and (
                    pygame.key.get_mods() & pygame.KMOD_ALT
                ):
                    self.running = False

            # Repassa o evento para a cena atual
            scene = self.scene_manager.current
            if scene:
                scene.handle_event(event)

        # Aplica mudanças de cena pendentes
        self.scene_manager.apply_pending()

        if self.scene_manager.is_empty:
            self.running = False

    def _update(self):
        scene = self.scene_manager.current
        if scene:
            scene.update()
        self.scene_manager.apply_pending()

    def _draw(self):
        # Render na superfície interna 640x360
        self.screen.fill((0, 0, 0))
        scene = self.scene_manager.current
        if scene:
            scene.draw(self.screen)

        # Upscale 2x para a janela 1280x720
        scaled = pygame.transform.scale(self.screen, (WINDOW_W, WINDOW_H))
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()
