# systems/tilemap.py — renderização e colisão do tilemap

import pygame
from settings import TILE_SIZE
from art.tiles import get_tile_surface, is_solid


class Tilemap:
    def __init__(self, data, tile_size=TILE_SIZE):
        """
        data: lista de listas de int (linhas x colunas)
        """
        self.data      = data
        self.tile_size = tile_size
        self.rows      = len(data)
        self.cols      = len(data[0]) if data else 0
        self.width_px  = self.cols * tile_size
        self.height_px = self.rows * tile_size

    def get_tile(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.data[row][col]
        return 0

    def is_solid_at(self, col, row):
        return is_solid(self.get_tile(col, row))

    def get_solid_rects_near(self, rect, margin=2):
        """Retorna rects sólidos próximos a um rect (para colisão)."""
        ts = self.tile_size
        col_start = max(0, rect.left  // ts - margin)
        col_end   = min(self.cols, rect.right  // ts + margin + 1)
        row_start = max(0, rect.top   // ts - margin)
        row_end   = min(self.rows, rect.bottom // ts + margin + 1)

        rects = []
        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                if self.is_solid_at(col, row):
                    rects.append(pygame.Rect(
                        col * ts, row * ts, ts, ts
                    ))
        return rects

    def draw(self, surf, cam_x, cam_y, screen_w, screen_h):
        ts = self.tile_size
        col_start = max(0, int(cam_x) // ts)
        col_end   = min(self.cols, col_start + screen_w // ts + 2)
        row_start = max(0, int(cam_y) // ts)
        row_end   = min(self.rows, row_start + screen_h // ts + 2)

        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                tile_id = self.data[row][col]
                if tile_id == 0:
                    continue
                tile_surf = get_tile_surface(tile_id)
                if tile_surf is None:
                    continue
                sx = col * ts - int(cam_x)
                sy = row * ts - int(cam_y)
                surf.blit(tile_surf, (sx, sy))
