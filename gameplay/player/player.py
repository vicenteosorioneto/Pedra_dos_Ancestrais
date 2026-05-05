# gameplay/player/player.py — Caio, personagem principal (refatorado)

from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from config.physics import (
    PLAYER_SPEED, PLAYER_JUMP_FORCE, PLAYER_GRAVITY,
    PLAYER_MAX_FALL, COYOTE_FRAMES, JUMP_BUFFER_FRAMES,
)
from shared.enums import PlayerState, GameEvent
from gameplay.player.states import VALID_TRANSITIONS
from art.sprites import get_caio_frame

if TYPE_CHECKING:
    from core.event_bus import EventBus
    from core.input_manager import InputState
    from systems.tilemap import Tilemap
    from art.fx import ParticleSystem


class Player:
    W  = 12
    H  = 28
    ATTACK_HITBOX_W = 20
    ATTACK_HITBOX_H = 16
    IFRAMES         = 60
    ANIM_SPEED      = 8

    def __init__(self, x: float, y: float, bus: EventBus) -> None:
        self.x   = float(x)
        self.y   = float(y)
        self.vx  = 0.0
        self.vy  = 0.0
        self._bus = bus

        # Stats
        self.hp     = 3
        self.max_hp = 3

        # Estado (enum — sem strings avulsas)
        self._state       = PlayerState.IDLE
        self.facing       = 1      # 1=direita, -1=esquerda
        self.iframe_timer = 0
        self.dead         = False

        # Coyote time e jump buffer
        self.coyote_timer      = 0
        self.jump_buffer_timer = 0
        self.on_ground         = False

        # Animação
        self.anim_frame  = 0
        self.anim_timer  = 0
        self.walk_frames = [1, 0, 2, 0]

        # Ataque
        self.attack_timer    = 0
        self.attack_cooldown = 0
        self.attack_active   = False

        # Partículas de poeira
        self._step_timer = 0

    # ── Estado (protegido contra transições inválidas) ────────────────────────

    @property
    def state(self) -> PlayerState:
        return self._state

    def _set_state(self, new: PlayerState) -> None:
        if new in VALID_TRANSITIONS.get(self._state, frozenset()):
            self._state = new

    # ── Rects ─────────────────────────────────────────────────────────────────

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def attack_rect(self) -> pygame.Rect:
        ax = int(self.x) + self.W if self.facing == 1 else int(self.x) - self.ATTACK_HITBOX_W
        return pygame.Rect(ax, int(self.y) + 8, self.ATTACK_HITBOX_W, self.ATTACK_HITBOX_H)

    # ── Input (recebe InputState — sem pygame.K_* aqui) ──────────────────────

    def handle_input(self, inp: InputState) -> bool:
        """Aplica intenções de movimento. Retorna True se está se movendo."""
        if self._state in (PlayerState.DEAD, PlayerState.HURT) and self.iframe_timer > 50:
            return False

        moving = False
        if inp.move_left:
            self.vx     = -PLAYER_SPEED
            self.facing = -1
            moving      = True
        elif inp.move_right:
            self.vx     = PLAYER_SPEED
            self.facing = 1
            moving      = True
        else:
            self.vx = 0.0

        if inp.jump:
            self.jump_buffer_timer = JUMP_BUFFER_FRAMES

        if inp.attack and self.attack_cooldown == 0:
            self._set_state(PlayerState.ATTACKING)
            self.attack_timer    = 16
            self.attack_cooldown = 24
            self.attack_active   = False

        return moving

    # ── Física ────────────────────────────────────────────────────────────────

    def _try_jump(self) -> None:
        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
            self.vy                = PLAYER_JUMP_FORCE
            self.jump_buffer_timer = 0
            self.coyote_timer      = 0
            self.on_ground         = False

    def _apply_gravity(self) -> None:
        self.vy = min(self.vy + PLAYER_GRAVITY, PLAYER_MAX_FALL)

    def collide_tilemap(self, tilemap: Tilemap) -> None:
        """Resolve colisão AABB com o tilemap (move X → Y)."""
        self.x += self.vx
        r = self.rect
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                self.x = tile_r.left - self.W if self.vx > 0 else float(tile_r.right)
                self.vx = 0.0
                r = self.rect

        self.y += self.vy
        r = self.rect
        self.on_ground = False
        for tile_r in tilemap.get_solid_rects_near(r):
            if r.colliderect(tile_r):
                if self.vy > 0:
                    self.y         = float(tile_r.top - self.H)
                    self.on_ground = True
                    self.vy        = 0.0
                else:
                    self.y  = float(tile_r.bottom)
                    self.vy = 0.0
                r = self.rect

    # ── Dano ──────────────────────────────────────────────────────────────────

    def take_damage(self, amount: int = 1) -> bool:
        """Aplica dano. Retorna True se dano foi aplicado. Publica eventos."""
        if self.iframe_timer > 0 or self.dead:
            return False
        self.hp          -= amount
        self.iframe_timer = self.IFRAMES
        self._set_state(PlayerState.HURT)
        self.vy           = -3.0

        self._bus.publish(
            GameEvent.PLAYER_DAMAGED,
            hp=self.hp, max_hp=self.max_hp,
            x=int(self.x) + self.W // 2,
            y=int(self.y) + self.H // 2,
        )

        if self.hp <= 0:
            self.hp   = 0
            self.dead = True
            self._set_state(PlayerState.DEAD)
            self._bus.publish(GameEvent.PLAYER_DIED)

        return True

    # ── Update ────────────────────────────────────────────────────────────────

    def update(
        self,
        inp: InputState,
        tilemap: Tilemap,
        particle_sys: ParticleSystem | None = None,
    ) -> None:
        if self.dead:
            self._apply_gravity()
            self.collide_tilemap(tilemap)
            return

        moving = self.handle_input(inp)
        self._try_jump()
        self._apply_gravity()
        self.collide_tilemap(tilemap)

        # Coyote time
        if self.on_ground:
            self.coyote_timer = COYOTE_FRAMES
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Timers
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
        if self.iframe_timer > 0:
            self.iframe_timer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
            self.attack_active = 4 <= self.attack_timer <= 12
        else:
            self.attack_active = False

        # Atualiza estado
        self._update_state(moving)

        # Animação
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            if self._state == PlayerState.WALKING:
                self.anim_frame = (self.anim_frame + 1) % len(self.walk_frames)
            else:
                self.anim_frame = 0

        # Poeira ao caminhar
        if particle_sys and self.on_ground and self._state == PlayerState.WALKING:
            self._step_timer += 1
            if self._step_timer >= 12:
                self._step_timer = 0
                particle_sys.emit_dust(int(self.x) + self.W // 2, int(self.y) + self.H)

    def _update_state(self, moving: bool) -> None:
        if self._state == PlayerState.HURT and self.iframe_timer < self.IFRAMES - 10:
            self._set_state(PlayerState.IDLE)
        if self._state != PlayerState.ATTACKING:
            if not self.on_ground:
                target = PlayerState.JUMPING if self.vy < 0 else PlayerState.FALLING
                self._set_state(target)
            elif moving:
                self._set_state(PlayerState.WALKING)
            else:
                self._set_state(PlayerState.IDLE)
        elif self.attack_timer == 0:
            self._set_state(PlayerState.IDLE)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.iframe_timer > 0 and (self.iframe_timer // 4) % 2 == 1:
            return  # pisca durante iframes

        if self._state == PlayerState.ATTACKING or self._state in (PlayerState.JUMPING, PlayerState.FALLING):
            frame_idx = 3
        elif self._state == PlayerState.WALKING:
            frame_idx = self.walk_frames[self.anim_frame % len(self.walk_frames)]
        else:
            frame_idx = 0

        sprite = get_caio_frame(frame_idx, self.facing)
        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        sx = int(self.x - cam_x) - 2
        sy = int(self.y - cam_y) - 4
        surf.blit(sprite, (sx, sy))
