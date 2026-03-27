# core/camera.py — câmera com suavização e parallax

from settings import SCREEN_W, SCREEN_H

class Camera:
    def __init__(self, world_w, world_h):
        self.x = 0.0
        self.y = 0.0
        self.world_w = world_w
        self.world_h = world_h
        self.lerp_speed = 0.08  # suavização

        # Velocidades de parallax por camada
        self.parallax_speeds = [0.05, 0.15, 0.30, 0.55, 1.0]

    def update(self, target_x, target_y):
        """Segue o alvo com lerp e clampa nas bordas."""
        # Centro da câmera no alvo
        desired_x = target_x - SCREEN_W // 2
        desired_y = target_y - SCREEN_H // 2

        # Lerp suave
        self.x += (desired_x - self.x) * self.lerp_speed
        self.y += (desired_y - self.y) * self.lerp_speed

        # Clamp nas bordas do mundo
        self.x = max(0, min(self.x, self.world_w - SCREEN_W))
        self.y = max(0, min(self.y, self.world_h - SCREEN_H))

    def world_to_screen(self, wx, wy):
        """Converte coordenada de mundo para tela."""
        return int(wx - self.x), int(wy - self.y)

    def parallax_offset(self, layer_index):
        """Offset de parallax para camada."""
        speed = self.parallax_speeds[min(layer_index, len(self.parallax_speeds)-1)]
        return int(self.x * speed)

    def get_visible_rect(self, margin=16):
        """Retorno rect do mundo visível (para culling)."""
        import pygame
        return pygame.Rect(
            int(self.x) - margin, int(self.y) - margin,
            SCREEN_W + margin*2, SCREEN_H + margin*2
        )
