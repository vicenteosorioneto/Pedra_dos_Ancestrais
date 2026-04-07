# config/palette.py — paletas de cores do jogo

from typing import Dict, Tuple

Color = Tuple[int, int, int]

PALETTE_SERTAO: Dict[str, Color] = {
    # céu e atmosfera
    "sky_dawn":    (255, 140,  60),
    "sky_mid":     (220,  80,  40),
    "sky_horizon": (255, 200,  80),
    "sun":         (255, 240, 160),
    "cloud_warm":  (255, 180, 120),
    # terreno
    "rock_light":  (180, 140,  90),
    "rock_mid":    (140, 100,  60),
    "rock_dark":   ( 90,  60,  35),
    "soil":        (160, 110,  55),
    "platform_top":(200, 160,  90),
    # vegetação
    "cactus":      ( 60, 120,  50),
    "cactus_dark": ( 40,  90,  35),
    "vine":        ( 50, 100,  40),
    # HUD
    "heart_red":   (220,  40,  40),
    "heart_empty": ( 80,  30,  30),
    "hud_bg":      ( 20,  15,  10),
    # personagens
    "caio_skin":   (210, 160, 110),
    "caio_shirt":  (180,  40,  30),
    "caio_pants":  ( 50,  70, 140),
    "caio_hat":    (100,  60,  20),
    "caio_boots":  ( 60,  35,  15),
    "enemy_skin":  (150, 100,  60),
    "enemy_vest":  ( 80,  55,  20),
    "enemy_hat":   (120,  80,  20),
}

PALETTE_CAVE: Dict[str, Color] = {
    "bg_deep":     ( 10,   5,  20),
    "bg_mid":      ( 25,  15,  45),
    "rock_cave":   ( 40,  30,  60),
    "rock_glow":   ( 80,  50, 120),
    "amber_glow":  (200, 130,  30),
    "spirit_blue": ( 80, 160, 220),
    "biolum":      ( 60, 200, 150),
}

BLACK: Color = (  0,   0,   0)
WHITE: Color = (255, 255, 255)
GOLD:  Color = (220, 180,  60)
