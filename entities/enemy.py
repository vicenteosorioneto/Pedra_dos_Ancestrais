# entities/enemy.py — classe base de inimigo

import pygame


class Enemy:
    def __init__(self, x, y, w=12, h=28):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 2
        self.max_hp = 2
        self.facing = 1
        self.alive  = True
        self.on_ground = False
        self.damage = 1

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def center(self):
        return (int(self.x + self.w/2), int(self.y + self.h/2))

    def take_damage(self, amount=1):
        if not self.alive:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.hp    = 0
            self.alive = False
            return True
        return False  # ainda vivo

    def apply_gravity(self, gravity=0.4, max_fall=8.0):
        self.vy += gravity
        if self.vy > max_fall:
            self.vy = max_fall

    def collide_tilemap(self, tilemap):
        self.x += self.vx
        r = self.rect
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                if self.vx > 0:
                    self.x = tile_r.left - self.w
                elif self.vx < 0:
                    self.x = tile_r.right
                self.vx = 0
                r = self.rect

        self.y += self.vy
        r = self.rect
        self.on_ground = False
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                if self.vy > 0:
                    self.y = tile_r.top - self.h
                    self.on_ground = True
                    self.vy = 0
                elif self.vy < 0:
                    self.y = tile_r.bottom
                    self.vy = 0
                r = self.rect

    def update(self, tilemap, player_rect=None):
        raise NotImplementedError

    def draw(self, surf, cam_x, cam_y):
        raise NotImplementedError
