# entities/player.py — Caio, personagem principal

import pygame
from settings import (
    PLAYER_SPEED, PLAYER_JUMP_FORCE, PLAYER_GRAVITY, PLAYER_MAX_FALL,
    COYOTE_FRAMES, JUMP_BUFFER_FRAMES, TILE_SIZE
)
from art.sprites import get_caio_frame


class Player:
    W = 12
    H = 28
    ATTACK_HITBOX_W = 20
    ATTACK_HITBOX_H = 16
    IFRAMES = 60       # frames de invencibilidade após dano
    ANIM_SPEED = 8     # ticks por frame de animação

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        # Stats
        self.hp     = 3
        self.max_hp = 3

        # Estados
        self.on_ground    = False
        self.facing       = 1      # 1=direita, -1=esquerda
        self.state        = "idle" # idle|walking|jumping|falling|attacking|hurt|dead
        self.iframe_timer = 0
        self.dead         = False

        # Coyote time e jump buffer
        self.coyote_timer      = 0
        self.jump_buffer_timer = 0

        # Animação
        self.anim_frame  = 0
        self.anim_timer  = 0
        self.walk_frames = [1, 0, 2, 0]  # ciclo de 4 frames

        # Breathing idle
        self.breath_timer  = 0
        self.breath_offset = 0

        # Ataque
        self.attack_timer    = 0
        self.attack_cooldown = 0
        self.attack_active   = False  # hitbox ativa

        # Partículas de poeira
        self._last_ground_x = x
        self._step_timer = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def attack_rect(self):
        if self.facing == 1:
            ax = int(self.x) + self.W
        else:
            ax = int(self.x) - self.ATTACK_HITBOX_W
        return pygame.Rect(ax, int(self.y) + 8, self.ATTACK_HITBOX_W, self.ATTACK_HITBOX_H)

    def handle_input(self, keys):
        if self.state in ("dead", "hurt") and self.iframe_timer > 50:
            return

        # Movimento horizontal
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing = -1
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing = 1
            moving = True
        else:
            self.vx = 0.0

        # Pulo
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump_buffer_timer = JUMP_BUFFER_FRAMES

        # Ataque
        if (keys[pygame.K_z] or keys[pygame.K_j]) and self.attack_cooldown == 0:
            self.state = "attacking"
            self.attack_timer    = 16
            self.attack_cooldown = 24
            self.attack_active   = False

        return moving

    def try_jump(self):
        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
            self.vy = PLAYER_JUMP_FORCE
            self.jump_buffer_timer = 0
            self.coyote_timer      = 0
            self.on_ground         = False

    def apply_gravity(self):
        self.vy += PLAYER_GRAVITY
        if self.vy > PLAYER_MAX_FALL:
            self.vy = PLAYER_MAX_FALL

    def collide_tilemap(self, tilemap):
        """Resolve colisão AABB com o tilemap."""
        ts = tilemap.tile_size
        r  = self.rect

        # Move X
        self.x += self.vx
        r = self.rect
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                if self.vx > 0:
                    self.x = tile_r.left - self.W
                elif self.vx < 0:
                    self.x = tile_r.right
                self.vx = 0
                r = self.rect

        # Move Y
        self.y += self.vy
        r = self.rect
        self.on_ground = False
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                if self.vy > 0:
                    self.y = tile_r.top - self.H
                    self.on_ground = True
                    self.vy = 0
                elif self.vy < 0:
                    self.y = tile_r.bottom
                    self.vy = 0
                r = self.rect

    def take_damage(self, amount=1, fx=None):
        if self.iframe_timer > 0 or self.dead:
            return False
        self.hp -= amount
        self.iframe_timer = self.IFRAMES
        self.state = "hurt"
        # Knockback leve
        self.vy = -3.0
        if fx:
            cx = int(self.x) + self.W // 2
            cy = int(self.y) + self.H // 2
            fx.emit_damage(cx, cy)
        if self.hp <= 0:
            self.hp   = 0
            self.dead = True
            self.state = "dead"
        return True

    def update(self, keys, tilemap, particle_sys=None):
        if self.dead:
            self.apply_gravity()
            self.collide_tilemap(tilemap)
            return

        moving = self.handle_input(keys)
        self.try_jump()
        self.apply_gravity()
        self.collide_tilemap(tilemap)

        # Coyote time
        if self.on_ground:
            self.coyote_timer = COYOTE_FRAMES
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Jump buffer
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        # iFrames
        if self.iframe_timer > 0:
            self.iframe_timer -= 1

        # Ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
            self.attack_active = 4 <= self.attack_timer <= 12
        else:
            self.attack_active = False

        # Estado
        if self.state == "hurt" and self.iframe_timer < self.IFRAMES - 10:
            self.state = "idle"
        if self.state != "attacking":
            if not self.on_ground:
                self.state = "jumping" if self.vy < 0 else "falling"
            elif moving:
                self.state = "walking"
            else:
                self.state = "idle"
        elif self.attack_timer == 0:
            self.state = "idle"

        # Animação de caminhada
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            if self.state == "walking":
                self.anim_frame = (self.anim_frame + 1) % len(self.walk_frames)
            else:
                self.anim_frame = 0

        # Breathing idle
        self.breath_timer += 1
        if self.state == "idle":
            self.breath_offset = 1 if (self.breath_timer // 30) % 2 == 0 else 0
        else:
            self.breath_offset = 0

        # Partículas de poeira ao caminhar
        if particle_sys and self.on_ground and self.state == "walking":
            self._step_timer += 1
            if self._step_timer >= 12:
                self._step_timer = 0
                particle_sys.emit_dust(
                    int(self.x) + self.W // 2,
                    int(self.y) + self.H
                )

    def draw(self, surf, cam_x, cam_y):
        # Seleciona frame
        if self.state == "attacking":
            frame_idx = 3
        elif self.state in ("jumping", "falling"):
            frame_idx = 3
        elif self.state == "walking":
            frame_idx = self.walk_frames[self.anim_frame % len(self.walk_frames)]
        else:
            frame_idx = 0

        sprite = get_caio_frame(frame_idx, self.facing)

        sx = int(self.x - cam_x) - 2  # centralizar sprite de 16 no hitbox de 12
        sy = int(self.y - cam_y) - 4 + self.breath_offset

        # Piscar quando em iframes
        if self.iframe_timer > 0 and (self.iframe_timer // 4) % 2 == 1:
            return  # pisca não renderizando

        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        surf.blit(sprite, (sx, sy))

        # Debug hitbox (desabilitar em produção)
        # pygame.draw.rect(surf, (255,0,0), (int(self.x-cam_x), int(self.y-cam_y), self.W, self.H), 1)
