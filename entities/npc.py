# entities/npc.py — NPCs com diálogos e patrulha simples

import pygame
from art.sprites import get_npc_villager, get_npc_elder


class NPC:
    W = 12
    H = 28
    WALK_SPEED = 0.5

    def __init__(self, x, y, npc_key, sprite_fn=None, patrol_range=0):
        self.x = float(x)
        self.y = float(y)
        self.npc_key = npc_key
        self.sprite_fn = sprite_fn
        self.patrol_origin = float(x)
        self.patrol_range  = float(patrol_range)
        self.facing = 1
        self.walk_dir = 1
        self.walk_timer = 0
        self.pause_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self):
        if self.patrol_range <= 0:
            return  # NPC parado

        # Lógica de patrulha simples
        if self.pause_timer > 0:
            self.pause_timer -= 1
            return

        self.x += self.walk_dir * self.WALK_SPEED
        self.facing = self.walk_dir

        if self.x > self.patrol_origin + self.patrol_range:
            self.walk_dir = -1
            self.pause_timer = 60
        elif self.x < self.patrol_origin - self.patrol_range:
            self.walk_dir = 1
            self.pause_timer = 60

        # Animação
        self.anim_timer += 1
        if self.anim_timer >= 12:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

    def draw(self, surf, cam_x, cam_y):
        if self.sprite_fn:
            sprite = self.sprite_fn(direction=self.facing)
        else:
            sprite = get_npc_villager(0, direction=self.facing)

        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        sx = int(self.x - cam_x) - 2
        sy = int(self.y - cam_y) - 4
        surf.blit(sprite, (sx, sy))

    def get_avatar(self):
        """Surface 16x32 para avatar na caixa de diálogo."""
        if self.sprite_fn:
            return self.sprite_fn(direction=1)
        return get_npc_villager(0, direction=1)


class VillagerNPC(NPC):
    def __init__(self, x, y, variant=0, patrol_range=40):
        super().__init__(x, y, f"aldeao_{variant+1}",
                         sprite_fn=lambda direction: get_npc_villager(variant, direction),
                         patrol_range=patrol_range)
        self.variant = variant
        if variant >= 2:
            self.patrol_range = 0  # parado


class ElderNPC(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "zequinha",
                         sprite_fn=lambda direction: get_npc_elder(direction),
                         patrol_range=0)
