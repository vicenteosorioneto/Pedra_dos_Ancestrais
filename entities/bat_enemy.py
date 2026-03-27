# entities/bat_enemy.py — morcego corrompido

import pygame
import math
from entities.enemy import Enemy
from art.sprites import get_bat_frame
from art.fx import ParticleSystem


class BatEnemy(Enemy):
    SPEED = 1.5
    PATROL_RANGE = 60

    def __init__(self, x, y, faster=False):
        super().__init__(x, y, w=14, h=10)
        self.hp = 2
        self.max_hp = 2
        self.damage = 1
        self.patrol_origin_x = float(x)
        self.patrol_dir = 1
        self.anim_frame = 0
        self.anim_timer = 0
        self.speed = self.SPEED * (1.5 if faster else 1.0)
        self.y_base = float(y)
        self.time = 0.0
        # Oscilação vertical
        self.osc_amp = 8.0
        self.osc_freq = 0.04

    def update(self, tilemap, player_rect=None):
        if not self.alive:
            return

        self.time += 1
        # Patrulha horizontal
        self.x += self.patrol_dir * self.speed
        # Oscilação vertical suave
        self.y = self.y_base + math.sin(self.time * self.osc_freq) * self.osc_amp

        # Inverte ao atingir limites
        if self.x > self.patrol_origin_x + self.PATROL_RANGE:
            self.patrol_dir = -1
            self.facing = -1
        elif self.x < self.patrol_origin_x - self.PATROL_RANGE:
            self.patrol_dir = 1
            self.facing = 1

        # Animação: troca asa a cada 8 frames
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = 1 - self.anim_frame

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        sprite = get_bat_frame(self.anim_frame)
        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        sx = int(self.x - cam_x) - 1
        sy = int(self.y - cam_y) - 3
        surf.blit(sprite, (sx, sy))

    def emit_death_particles(self, particle_sys):
        cx, cy = self.center
        particle_sys.emit_death(cx, cy, color=(100, 50, 150), count=6)
