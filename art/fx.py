# art/fx.py — efeitos visuais: partículas, luz, câmera

import pygame
import random
import math


class Particle:
    def __init__(self, x, y, color, vx=0.0, vy=0.0, life=30, size=2):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravidade leve
        self.life -= 1

    def draw(self, surf, offset_x=0, offset_y=0):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        r, g, b = self.color
        rx = int(self.x - offset_x)
        ry = int(self.y - offset_y)
        if self.size == 1:
            surf.set_at((rx, ry), (r, g, b)) if 0 <= rx < surf.get_width() and 0 <= ry < surf.get_height() else None
        else:
            pygame.draw.rect(surf, (r, g, b), (rx, ry, self.size, self.size))

    @property
    def alive(self):
        return self.life > 0


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_death(self, x, y, color=(150, 50, 200), count=6):
        """Partículas de morte de inimigo."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 3.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 1.5
            size = random.randint(1, 3)
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, vx, vy, life, size))

    def emit_dust(self, x, y):
        """Poeira dos passos."""
        for _ in range(2):
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.8, -0.2)
            c = (160, 120, 80)
            self.particles.append(Particle(x, y, c, vx, vy, life=15, size=1))

    def emit_altar(self, x, y):
        """Partículas âmbar dos altares."""
        vx = random.uniform(-0.3, 0.3)
        vy = random.uniform(-1.5, -0.5)
        c = (200 + random.randint(-20, 20), 130 + random.randint(-20, 20), 30)
        self.particles.append(Particle(x, y, c, vx, vy, life=40, size=1))

    def emit_damage(self, x, y):
        """Partículas de dano."""
        for _ in range(5):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(1.0, 2.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            c = (220 + random.randint(-20, 0), 30, 30)
            self.particles.append(Particle(x, y, c, vx, vy, life=25, size=2))

    def update(self):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

    def draw(self, surf, cam_x=0, cam_y=0):
        for p in self.particles:
            p.draw(surf, cam_x, cam_y)


class ScreenEffects:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.shake_frames = 0
        self.shake_intensity = 0
        self.shake_offset = (0, 0)
        self.flash_frames = 0
        self.flash_color = (255, 255, 255)
        self.fade_frames = 0
        self.fade_target = 0  # 0=transparente, 255=negro
        self.fade_surface = pygame.Surface((w, h))
        self.fade_surface.fill((0, 0, 0))

    def camera_shake(self, intensity=4, frames=12):
        self.shake_frames = frames
        self.shake_intensity = intensity

    def flash(self, color=(255, 255, 255), frames=8):
        self.flash_frames = frames
        self.flash_color = color

    def fade_out(self, frames=30):
        self.fade_frames = -frames  # negativo = fade out

    def fade_in(self, frames=30):
        self.fade_frames = frames  # positivo = fade in

    def update(self):
        if self.shake_frames > 0:
            self.shake_frames -= 1
            i = self.shake_intensity
            self.shake_offset = (
                random.randint(-i, i),
                random.randint(-i, i)
            )
        else:
            self.shake_offset = (0, 0)
            self.shake_intensity = 0

        if self.flash_frames > 0:
            self.flash_frames -= 1

        if self.fade_frames != 0:
            if self.fade_frames > 0:
                self.fade_frames -= 1
            else:
                self.fade_frames += 1

    def draw(self, dest_surf):
        """Aplica efeitos na superfície de destino."""
        if self.flash_frames > 0:
            fs = pygame.Surface((self.w, self.h))
            fs.fill(self.flash_color)
            alpha = int(180 * (self.flash_frames / 8))
            fs.set_alpha(alpha)
            dest_surf.blit(fs, (0, 0))

        if self.fade_frames != 0:
            alpha = abs(self.fade_frames)
            self.fade_surface.set_alpha(alpha * 8)
            dest_surf.blit(self.fade_surface, (0, 0))

    def apply_vignette(self, dest_surf, intensity=80):
        """Vinheta nas bordas."""
        vsurf = pygame.Surface((self.w, self.h))
        vsurf.fill((0, 0, 0))
        vsurf.set_alpha(intensity)
        # centro transparente — aproximação com rect
        inner = pygame.Rect(self.w//4, self.h//4, self.w//2, self.h//2)
        pygame.draw.rect(vsurf, (0, 0, 0, 0), inner)
        dest_surf.blit(vsurf, (0, 0))

    @property
    def is_fading(self):
        return self.fade_frames != 0

    @property
    def fade_done(self):
        return self.fade_frames == 0


def draw_stars(surface, count=150, seed=42):
    """Estrelas com seed fixa para cena noturna."""
    rng = random.Random(seed)
    w, h = surface.get_size()
    for _ in range(count):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h//2)
        size_roll = rng.random()
        if size_roll < 0.6:
            surface.set_at((x, y), (220, 220, 200))
        elif size_roll < 0.9:
            pygame.draw.rect(surface, (240, 240, 220), (x, y, 2, 2))
        else:
            # estrela com cruz
            c = (255, 255, 240)
            surface.set_at((x, y), c)
            if x > 0: surface.set_at((x-1, y), (180, 180, 160))
            if x < w-1: surface.set_at((x+1, y), (180, 180, 160))
            if y > 0: surface.set_at((x, y-1), (180, 180, 160))
            if y < h-1: surface.set_at((x, y+1), (180, 180, 160))


def draw_ambient_light(surface, sources, w, h):
    """
    Iluminação ambiente simples.
    sources: lista de (x, y, raio, (r,g,b))
    """
    light_surf = pygame.Surface((w, h))
    light_surf.fill((0, 0, 0))

    for lx, ly, radius, color in sources:
        # Desenha círculo de luz gradual
        for r in range(radius, 0, -2):
            alpha = int(60 * (1.0 - r / radius))
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (r, r), r)
            light_surf.blit(s, (int(lx) - r, int(ly) - r),
                            special_flags=pygame.BLEND_ADD)

    surface.blit(light_surf, (0, 0), special_flags=pygame.BLEND_ADD)
