# gameplay/enemies/guardian_statue.py — guardião v4 (sem Parkinson)
from __future__ import annotations
import pygame
from gameplay.enemies.base_enemy import Enemy
from art.sprites import get_guardian_frame

class GuardianStatue(Enemy):
    SPEED_P1           = 0.6
    SPEED_P2           = 1.4
    SHOCKWAVE_INTERVAL = 100

    def __init__(self, x, y):
        super().__init__(x, y, w=26, h=44)
        self.hp = 8; self.max_hp = 8; self.damage = 0
        self.phase = 1; self.speed = self.SPEED_P1

        # Movimento suavizado
        self._vel_x = 0.0

        # Animação ligada à velocidade (não ao tick)
        self._anim_tick  = 0.0
        self.anim_frame  = 0
        self.anim_timer  = 0  # mantido p/ compatibilidade

        self.shockwave_timer = 0
        self.shockwaves: list[dict] = []
        self.defeated = False
        self._dialogue_shown = False

        # Despertar dramático
        self.awaken_timer = 80       # pisca por 80 frames
        self._awake = False
        self._wake_shake = 0.0

        self.phase_just_changed = False
        self._hurt_flash = 0

        # Rush (fase 2)
        self._rush_cd = 240
        self._rush_frames = 0

    def update(self, tilemap, player_rect=None):
        if self.defeated: return

        prev_phase = self.phase
        if self.hp <= 4:
            self.phase = 2
            self.speed = self.SPEED_P2
        self.phase_just_changed = (prev_phase == 1 and self.phase == 2)

        # Despertar
        if self.awaken_timer > 0:
            self.awaken_timer -= 1
            # Tremer levemente
            self._wake_shake = 0.8 if self.awaken_timer % 6 < 3 else -0.8
            self.x += self._wake_shake
            if self.awaken_timer == 0:
                self._awake = True
                self._vel_x = 0.0
            return
        self._wake_shake = 0.0

        if not self._awake or not player_rect: return

        # Rush na fase 2
        if self.phase == 2:
            self._rush_cd -= 1
            if self._rush_cd <= 0:
                self._rush_cd = 240
                self._rush_frames = 30
            if self._rush_frames > 0:
                self._rush_frames -= 1
                target_speed = 3.5
            else:
                target_speed = self.speed
        else:
            target_speed = self.speed

        # Movimento suavizado com lerp
        px = player_rect.centerx
        dir_x = 1 if px > self.x + self.w//2 else -1
        if abs(px - (self.x + self.w//2)) > 4:
            self._vel_x += (dir_x * target_speed - self._vel_x) * 0.12
            self.facing = dir_x
        else:
            self._vel_x *= 0.7

        self.x += self._vel_x

        # Animação de passo ligada à velocidade (FIM DO PARKINSON)
        self._anim_tick += abs(self._vel_x)
        if self._anim_tick >= 8:
            self._anim_tick = 0
            self.anim_frame = 1 - self.anim_frame

        # Ondas de choque (fase 2)
        if self.phase == 2:
            self.shockwave_timer += 1
            if self.shockwave_timer >= self.SHOCKWAVE_INTERVAL:
                self.shockwave_timer = 0
                self._create_shockwave()

        self.shockwaves = [sw for sw in self.shockwaves if sw["life"] > 0]
        for sw in self.shockwaves:
            sw["x"] += sw["vx"]; sw["life"] -= 1

        if self._hurt_flash > 0:
            self._hurt_flash -= 1

    def take_damage(self, amount):
        if self.defeated or not self._awake: return
        self.hp = max(0, self.hp - amount)
        self._hurt_flash = 10

    def _create_shockwave(self):
        cx = int(self.x + self.w//2); cy = int(self.y + self.h)
        base = {"y": float(cy), "life": 44, "w": 8, "h": 6}
        self.shockwaves.append({**base, "x": float(cx), "vx":  3.2})
        self.shockwaves.append({**base, "x": float(cx), "vx": -3.2})

    def check_shockwave_hit(self, player_rect):
        for sw in self.shockwaves:
            sr = pygame.Rect(int(sw["x"])-sw["w"]//2, int(sw["y"])-sw["h"], sw["w"], sw["h"])
            if sr.colliderect(player_rect): return True
        return False

    def knockback_player(self, player):
        player.vx = 4.0 if self.facing == 1 else -4.0
        player.vy = -3.0

    def defeat(self):
        self.defeated = True; self.alive = False; self._vel_x = 0.0

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x); sy = int(self.y - cam_y)

        # Despertar — pisca mais rápido quanto mais próximo de acordar
        if self.awaken_timer > 0:
            blink_speed = max(2, self.awaken_timer//10)
            if (self.awaken_timer // blink_speed) % 2 == 0:
                frame = 1   # olhos acesos
                sprite = get_guardian_frame(frame)
                tmp = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                tmp.blit(sprite, (0,0))
                tmp.set_alpha(180)
                surf.blit(tmp, (sx, sy))
            return

        frame = self.anim_frame
        sprite = get_guardian_frame(frame)
        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        # Flash de dano
        if self._hurt_flash > 0 and self._hurt_flash % 2 == 0:
            tmp = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            tmp.blit(sprite,(0,0))
            tmp.fill((255,255,255,80), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(tmp,(sx,sy))
        else:
            surf.blit(sprite,(sx,sy))

        # Ondas de choque
        for sw in self.shockwaves:
            wx = int(sw["x"]-cam_x)-sw["w"]//2; wy = int(sw["y"]-cam_y)-sw["h"]
            t = sw["life"]/44
            gsurf = pygame.Surface((sw["w"]+8,sw["h"]+6),pygame.SRCALPHA)
            pygame.draw.ellipse(gsurf,(220,140,30,int(180*t)),(0,0,sw["w"]+8,sw["h"]+6))
            surf.blit(gsurf,(wx-4,wy-3))
            pygame.draw.ellipse(surf,(240,180,60),(wx,wy,sw["w"],sw["h"]))

        # Barra de HP segmentada
        bar_w = max(self.w+12, 42); bx = sx+(self.w-bar_w)//2; by = sy-12; bh = 5
        segs  = self.max_hp; seg_w = (bar_w-segs-1)//segs
        pygame.draw.rect(surf,(15,10,25),(bx-1,by-1,bar_w+2,bh+2))
        for i in range(segs):
            filled = i < self.hp
            col    = ((220,130,30) if self.phase==2 else (220,40,40)) if filled else (30,22,8)
            sx2    = bx+1+i*(seg_w+1)
            pygame.draw.rect(surf,col,(sx2,by+1,seg_w,bh-2))
        pygame.draw.rect(surf,(160,120,40),(bx-1,by-1,bar_w+2,bh+2),1)

        if not hasattr(self,"_label_font"):
            try: self._label_font = pygame.font.SysFont("Courier New",9,bold=True)
            except: self._label_font = pygame.font.Font(None,12)
        label_txt = "GUARDIÃO ▸ FASE II" if self.phase==2 else "GUARDIÃO"
        label = self._label_font.render(label_txt,True,(220,180,60) if self.phase==2 else (180,160,140))
        surf.blit(label,(bx+(bar_w-label.get_width())//2,by-10))
