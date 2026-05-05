# core/game.py — loop principal do jogo (refatorado)

from __future__ import annotations
import pygame
import sys

from config.display import SCREEN_W, SCREEN_H, WINDOW_W, WINDOW_H, FPS, TITLE
from core.scene_manager import SceneManager
from core.event_bus import EventBus
from core.input_manager import InputManager
from systems.karma import KarmaSystem


class Game:
    """
    Inicializa pygame, gerencia o loop e injeta serviços nas cenas.

    Serviços disponíveis para todas as cenas via parâmetros do construtor:
        scene_manager : SceneManager  — pilha de cenas
        bus           : EventBus      — pub/sub desacoplado
        karma         : KarmaSystem   — rastreamento de karma global
        input_manager : InputManager  — mapeamento de ações de input
    """

    def __init__(self) -> None:
        pygame.init()
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        except pygame.error:
            pass

        self.window  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(TITLE)

        try:
            from art.sprites import get_window_icon
            icon = pygame.transform.scale(get_window_icon(), (32, 32))
            pygame.display.set_icon(icon)
        except Exception:
            pass

        self.screen  = pygame.Surface((SCREEN_W, SCREEN_H))
        self.clock   = pygame.time.Clock()
        self.running = True

        # ── Serviços compartilhados ───────────────────────────────────────────
        self.bus           = EventBus()
        self.karma         = KarmaSystem(self.bus)
        self.input_manager = InputManager()
        self.scene_manager = SceneManager()
        from systems.audio import AudioManager
        self.audio = AudioManager(self.bus)

    def start(self) -> None:
        """Carrega a cena inicial. Chamado por main.py após __init__."""
        from scenes.intro_scene import IntroScene
        intro = IntroScene(self.scene_manager, self.bus, self.karma, self.input_manager)
        self.scene_manager.push(intro)
        intro.on_enter()

    def run(self) -> None:
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and (pygame.key.get_mods() & pygame.KMOD_ALT):
                    self.running = False
            if scene := self.scene_manager.current:
                scene.handle_event(event)
        self.scene_manager.apply_pending()
        if self.scene_manager.is_empty:
            self.running = False

    def _update(self) -> None:
        if scene := self.scene_manager.current:
            scene.update()
            self.audio.update_for_scene(scene)
        self.scene_manager.apply_pending()

    def _draw(self) -> None:
        self.screen.fill((0, 0, 0))
        if scene := self.scene_manager.current:
            scene.draw(self.screen)
        scaled = pygame.transform.scale(self.screen, (WINDOW_W, WINDOW_H))
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()
