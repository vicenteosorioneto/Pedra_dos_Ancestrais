import math
import pygame

from settings import SCREEN_W, SCREEN_H


class RewardPickup:
    W = 12
    H = 12

    def __init__(self, x, y, kind="heart", label="Bencao recebida"):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.label = label
        self.collected = False
        self.time = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self):
        self.time += 1

    def collect(self, player, karma=None, bus=None):
        if self.collected:
            return False

        self.collected = True
        if self.kind == "heart":
            player.hp = min(player.max_hp, player.hp + 1)
        elif self.kind == "heart_max":
            player.max_hp = min(5, player.max_hp + 1)
            player.hp = min(player.max_hp, player.hp + 1)
        elif self.kind == "wisdom" and karma:
            karma.leu_registro()

        if bus:
            from shared.enums import GameEvent
            bus.publish(GameEvent.ITEM_COLLECTED, is_trap=False, kind=self.kind)
        return True

    def draw(self, surf, cam_x, cam_y):
        if self.collected:
            return
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y + math.sin(self.time * 0.08) * 2)
        if not (-20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H + 20):
            return

        if self.kind == "heart":
            col = (220, 45, 55)
            glow = (255, 130, 95, 70)
        elif self.kind == "heart_max":
            col = (255, 190, 60)
            glow = (255, 220, 100, 85)
        else:
            col = (80, 190, 220)
            glow = (80, 190, 220, 70)

        gsurf = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(gsurf, glow, (14, 14), 13)
        surf.blit(gsurf, (sx - 8, sy - 8))

        if self.kind in ("heart", "heart_max"):
            pts = [
                (sx + 6, sy + 11), (sx + 2, sy + 7), (sx + 1, sy + 4),
                (sx + 3, sy + 2), (sx + 6, sy + 4), (sx + 9, sy + 2),
                (sx + 11, sy + 4), (sx + 10, sy + 7),
            ]
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, (45, 20, 18), pts, 1)
        else:
            pygame.draw.rect(surf, col, (sx + 3, sy + 1, 6, 10))
            pygame.draw.rect(surf, (20, 55, 65), (sx + 3, sy + 1, 6, 10), 1)
            pygame.draw.line(surf, (210, 245, 255), (sx + 5, sy + 3), (sx + 7, sy + 8))


def update_rewards(rewards, player, particles, sys_msg, karma=None, bus=None):
    for reward in rewards:
        reward.update()
        if not reward.collected and reward.rect.colliderect(player.rect):
            if reward.collect(player, karma=karma, bus=bus):
                particles.emit_phase_burst(
                    int(reward.x + reward.W // 2),
                    int(reward.y + reward.H // 2),
                )
                sys_msg.show(reward.label, 100)


def draw_rewards(rewards, surf, cam_x, cam_y):
    for reward in rewards:
        reward.draw(surf, cam_x, cam_y)
