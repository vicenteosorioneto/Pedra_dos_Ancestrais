# art/sprites.py — sprites pixel art gerados via código

import pygame
from settings import PALETTE_SERTAO as P, PALETTE_CAVE as C

# Cache de sprites
_cache = {}

def _p(key):
    return P[key]

def _c(key):
    return C[key]

def _new(w, h, colorkey=(0, 0, 0)):
    s = pygame.Surface((w, h))
    s.fill(colorkey)
    s.set_colorkey(colorkey)
    return s

def _outline(surf, color=(0, 0, 0)):
    """Aplica outline 1px em volta de pixels não-transparentes."""
    w, h = surf.get_size()
    ck = surf.get_colorkey()
    result = surf.copy()
    for y in range(h):
        for x in range(w):
            if surf.get_at((x, y))[:3] != ck:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if surf.get_at((nx, ny))[:3] == ck:
                            result.set_at((nx, ny), color)
    return result


# ─────────────────────────────────────────────
#  CAIO — personagem principal 16x32
# ─────────────────────────────────────────────

def _draw_caio_base(surf, frame=0, direction=1):
    """Desenha Caio pixel a pixel em surface 16x32."""
    skin   = _p("caio_skin")
    shirt  = _p("caio_shirt")
    pants  = _p("caio_pants")
    hat    = _p("caio_hat")
    boots  = _p("caio_boots")
    black  = (0, 0, 0)
    white  = (255, 255, 255)
    dark_skin = (170, 120, 80)
    dark_shirt = (130, 25, 20)
    dark_pants = (35, 50, 110)

    # --- CHAPÉU (y=0..4) ---
    # aba do chapéu
    for x in range(2, 14):
        surf.set_at((x, 4), hat)
    # copa do chapéu
    for x in range(4, 12):
        for y in range(1, 4):
            surf.set_at((x, y), hat)
    surf.set_at((3, 3), hat)
    surf.set_at((12, 3), hat)
    # sombra no chapéu
    for x in range(4, 12):
        surf.set_at((x, 3), (70, 40, 10))

    # --- CABEÇA (y=5..10) ---
    for x in range(4, 12):
        for y in range(5, 11):
            surf.set_at((x, y), skin)
    # arredondar cabeça
    surf.set_at((4, 5), black)
    surf.set_at((11, 5), black)
    surf.set_at((4, 10), black)
    surf.set_at((11, 10), black)

    # --- OLHOS (y=7) ---
    eye_offset = 1 if direction == 1 else -1
    if direction == 1:
        # olho direito
        surf.set_at((7, 7), black)
        surf.set_at((8, 7), white)
        # olho esquerdo
        surf.set_at((9, 7), black)
        surf.set_at((10, 7), white)
    else:
        surf.set_at((5, 7), white)
        surf.set_at((6, 7), black)
        surf.set_at((7, 7), white)
        surf.set_at((8, 7), black)

    # --- SORRISO (y=9) ---
    surf.set_at((6, 9), dark_skin)
    surf.set_at((7, 9), dark_skin)
    surf.set_at((8, 9), dark_skin)
    surf.set_at((9, 9), dark_skin)

    # --- PESCOÇO + TRONCO (y=11..19) ---
    # pescoço
    surf.set_at((7, 11), skin)
    surf.set_at((8, 11), skin)
    # tronco: camisa vermelha
    for x in range(4, 12):
        for y in range(12, 20):
            surf.set_at((x, y), shirt)
    # sombra lateral camisa
    for y in range(12, 20):
        surf.set_at((4, y), dark_shirt)
    # highlight camisa
    for y in range(12, 20):
        surf.set_at((11, y), (220, 80, 70))

    # --- BRAÇOS (animação de walk) ---
    arm_offset_r = 0
    arm_offset_l = 0
    if frame == 1:
        arm_offset_r = -2
        arm_offset_l = 2
    elif frame == 2:
        arm_offset_r = 2
        arm_offset_l = -2

    # braço direito
    bx_r = 2 if direction == 1 else 12
    for y in range(13, 20):
        yo = y + arm_offset_r
        if 0 <= yo < 32:
            surf.set_at((bx_r, yo), shirt)
            surf.set_at((bx_r+1, yo), dark_skin)

    # braço esquerdo
    bx_l = 13 if direction == 1 else 2
    for y in range(13, 20):
        yo = y + arm_offset_l
        if 0 <= yo < 32:
            surf.set_at((bx_l, yo), shirt)

    # mãos
    surf.set_at((bx_r, 19 + arm_offset_r if 0 <= 19+arm_offset_r < 32 else 19), skin)
    surf.set_at((bx_l, 19 + arm_offset_l if 0 <= 19+arm_offset_l < 32 else 19), skin)

    # --- CALÇA (y=20..25) ---
    for x in range(4, 12):
        for y in range(20, 26):
            surf.set_at((x, y), pants)
    # divisão das pernas
    surf.set_at((7, 21), dark_pants)
    surf.set_at((8, 21), dark_pants)
    for y in range(21, 26):
        surf.set_at((7, y), dark_pants)
        surf.set_at((8, y), dark_pants)

    # --- PERNAS (animação) ---
    leg_r = 0
    leg_l = 0
    if frame == 1:
        leg_r = -2
        leg_l = 2
    elif frame == 2:
        leg_r = 2
        leg_l = -2

    # perna direita
    for y in range(26, 30):
        yo = y + leg_r
        if 0 <= yo < 32:
            surf.set_at((5, yo), pants)
            surf.set_at((6, yo), pants)

    # perna esquerda
    for y in range(26, 30):
        yo = y + leg_l
        if 0 <= yo < 32:
            surf.set_at((9, yo), pants)
            surf.set_at((10, yo), pants)

    # --- BOTAS (y=30..31) ---
    for x in range(4, 8):
        surf.set_at((x, 30), boots)
        surf.set_at((x, 31), boots)
    for x in range(8, 13):
        surf.set_at((x, 30), boots)
        surf.set_at((x, 31), boots)


def get_caio_frame(frame=0, direction=1):
    key = ("caio", frame, direction)
    if key not in _cache:
        surf = _new(16, 32)
        _draw_caio_base(surf, frame, direction)
        _cache[key] = _outline(surf)
    return _cache[key]


# ─────────────────────────────────────────────
#  INIMIGO BANDIDO — 16x32
# ─────────────────────────────────────────────

def _draw_bandit_base(surf, frame=0, direction=1):
    skin  = _p("enemy_skin")
    vest  = _p("enemy_vest")
    hat   = _p("enemy_hat")
    pants = (50, 40, 20)
    boots = (50, 30, 10)
    knife = (180, 180, 200)
    dark_skin = (110, 70, 30)
    black = (0, 0, 0)
    white = (255, 255, 255)

    # chapéu de palha
    for x in range(2, 14):
        surf.set_at((x, 4), hat)
    for x in range(4, 12):
        for y in range(1, 4):
            surf.set_at((x, y), hat)
    surf.set_at((3, 3), hat)
    surf.set_at((12, 3), hat)
    for x in range(4, 12):
        surf.set_at((x, 2), (90, 60, 10))  # linha da palha

    # cabeça
    for x in range(4, 12):
        for y in range(5, 11):
            surf.set_at((x, y), skin)
    # expressão brava
    if direction == 1:
        surf.set_at((7, 7), black)
        surf.set_at((9, 7), black)
        surf.set_at((6, 9), dark_skin)
        surf.set_at((10, 9), dark_skin)
    else:
        surf.set_at((6, 7), black)
        surf.set_at((8, 7), black)
        surf.set_at((5, 9), dark_skin)
        surf.set_at((9, 9), dark_skin)
    # barba
    for x in range(5, 11):
        surf.set_at((x, 10), (80, 55, 30))

    # tronco: colete
    for x in range(4, 12):
        for y in range(12, 20):
            surf.set_at((x, y), vest)
    for y in range(12, 20):
        surf.set_at((4, y), (50, 35, 10))

    # braços
    arm_off = 2 if frame == 1 else (-2 if frame == 2 else 0)
    for y in range(13, 20):
        yo = y + arm_off
        if 0 <= yo < 32:
            surf.set_at((2, yo), vest)
            surf.set_at((3, yo), skin)
    for y in range(13, 20):
        surf.set_at((13, y), vest)
        surf.set_at((12, y), skin)

    # faca (frame de ataque ou sempre à direita)
    if direction == 1:
        surf.set_at((14, 14), knife)
        surf.set_at((15, 13), knife)
        surf.set_at((15, 14), (150, 150, 170))
    else:
        surf.set_at((1, 14), knife)
        surf.set_at((0, 13), knife)
        surf.set_at((0, 14), (150, 150, 170))

    # calça
    for x in range(4, 12):
        for y in range(20, 26):
            surf.set_at((x, y), pants)
    for y in range(21, 26):
        surf.set_at((7, y), (30, 25, 10))
        surf.set_at((8, y), (30, 25, 10))

    # pernas
    leg_off = 2 if frame == 1 else (-2 if frame == 2 else 0)
    for y in range(26, 30):
        yo = y + leg_off
        if 0 <= yo < 32:
            surf.set_at((5, yo), pants)
            surf.set_at((6, yo), pants)
    for y in range(26, 30):
        yo = y - leg_off
        if 0 <= yo < 32:
            surf.set_at((9, yo), pants)
            surf.set_at((10, yo), pants)

    # botas
    for x in range(4, 8):
        surf.set_at((x, 30), boots)
        surf.set_at((x, 31), boots)
    for x in range(8, 13):
        surf.set_at((x, 30), boots)
        surf.set_at((x, 31), boots)


def get_bandit_frame(frame=0, direction=1):
    key = ("bandit", frame, direction)
    if key not in _cache:
        surf = _new(16, 32)
        _draw_bandit_base(surf, frame, direction)
        _cache[key] = _outline(surf)
    return _cache[key]


# ─────────────────────────────────────────────
#  MORCEGO — 16x16
# ─────────────────────────────────────────────

def get_bat_frame(frame=0):
    key = ("bat", frame)
    if key not in _cache:
        surf = _new(16, 16)
        body  = (60, 30, 80)
        wing  = (100, 50, 120)
        dark  = (40, 15, 55)
        eye   = (200, 50, 50)
        # corpo central
        for x in range(6, 10):
            for y in range(6, 12):
                surf.set_at((x, y), body)
        surf.set_at((6, 6), dark)
        surf.set_at((9, 6), dark)
        # olhos
        surf.set_at((6, 7), eye)
        surf.set_at((9, 7), eye)
        # orelhas
        surf.set_at((6, 5), body)
        surf.set_at((5, 4), body)
        surf.set_at((9, 5), body)
        surf.set_at((10, 4), body)
        # asas
        if frame == 0:
            # asa aberta
            for x in range(1, 6):
                surf.set_at((x, 7), wing)
                surf.set_at((x, 8), wing)
            for x in range(10, 15):
                surf.set_at((x, 7), wing)
                surf.set_at((x, 8), wing)
            surf.set_at((1, 6), dark)
            surf.set_at((14, 6), dark)
            surf.set_at((2, 5), dark)
            surf.set_at((13, 5), dark)
        else:
            # asa dobrada
            for x in range(3, 6):
                surf.set_at((x, 8), wing)
                surf.set_at((x, 9), wing)
            for x in range(10, 13):
                surf.set_at((x, 8), wing)
                surf.set_at((x, 9), wing)
        # focinho
        surf.set_at((7, 11), dark)
        surf.set_at((8, 11), dark)
        _cache[key] = _outline(surf)
    return _cache[key]


# ─────────────────────────────────────────────
#  GUARDIÃO ESTÁTUA — 32x48
# ─────────────────────────────────────────────

def get_guardian_frame(frame=0):
    key = ("guardian", frame)
    if key not in _cache:
        surf = _new(32, 48)
        stone  = (100, 90, 120)
        dark   = (60, 50, 75)
        light  = (140, 130, 160)
        amber  = (200, 130, 30)
        crack  = (40, 30, 50)

        # pés / base
        for x in range(4, 28):
            for y in range(42, 48):
                surf.set_at((x, y), dark)
        # pernas
        for x in range(7, 15):
            for y in range(30, 43):
                surf.set_at((x, y), stone)
        for x in range(17, 25):
            for y in range(30, 43):
                surf.set_at((x, y), stone)
        # saia / saiote
        for x in range(5, 27):
            for y in range(28, 32):
                surf.set_at((x, y), stone)
        # tronco
        for x in range(8, 24):
            for y in range(14, 29):
                surf.set_at((x, y), stone)
        # highlight tronco
        for y in range(14, 29):
            surf.set_at((23, y), light)
        # rachaduras
        surf.set_at((12, 18), crack)
        surf.set_at((13, 19), crack)
        surf.set_at((12, 20), crack)
        surf.set_at((18, 22), crack)
        surf.set_at((19, 21), crack)
        # ombros
        for x in range(4, 8):
            for y in range(14, 20):
                surf.set_at((x, y), stone)
        for x in range(24, 28):
            for y in range(14, 20):
                surf.set_at((x, y), stone)
        # braços
        for x in range(3, 7):
            for y in range(20, 30):
                surf.set_at((x, y), stone)
        for x in range(25, 29):
            for y in range(20, 30):
                surf.set_at((x, y), stone)
        # punhos
        for x in range(2, 8):
            for y in range(30, 36):
                surf.set_at((x, y), dark)
        for x in range(24, 30):
            for y in range(30, 36):
                surf.set_at((x, y), dark)

        # cabeça
        for x in range(10, 22):
            for y in range(4, 14):
                surf.set_at((x, y), stone)
        # arredondar
        surf.set_at((10, 4), (0, 0, 0))
        surf.set_at((21, 4), (0, 0, 0))
        surf.set_at((10, 13), (0, 0, 0))
        surf.set_at((21, 13), (0, 0, 0))
        # olhos âmbar brilhantes
        eye_state = amber if frame == 1 else (40, 30, 15)
        for ox, oy in [(12, 7), (13, 7), (18, 7), (19, 7)]:
            surf.set_at((ox, oy), eye_state)
        if frame == 1:  # acordando
            surf.set_at((12, 6), (240, 200, 80))
            surf.set_at((13, 6), (240, 200, 80))
            surf.set_at((18, 6), (240, 200, 80))
            surf.set_at((19, 6), (240, 200, 80))
        # boca
        for x in range(13, 19):
            surf.set_at((x, 11), dark)
        surf.set_at((14, 10), dark)
        surf.set_at((17, 10), dark)

        # nariz
        surf.set_at((15, 9), dark)
        surf.set_at((16, 9), dark)

        _cache[key] = _outline(surf, (0, 0, 0))
    return _cache[key]


# ─────────────────────────────────────────────
#  NPC VOVÔ ZEQUINHA — 16x32
# ─────────────────────────────────────────────

def get_npc_elder(direction=1):
    key = ("elder", direction)
    if key not in _cache:
        surf = _new(16, 32)
        skin   = (190, 140, 90)
        shirt  = (200, 200, 180)
        pants  = (100, 80, 50)
        hat    = (150, 120, 60)
        hair   = (220, 220, 220)
        dark_skin = (140, 100, 60)
        black  = (0, 0, 0)
        cane   = (120, 80, 30)

        # chapéu de palha largo
        for x in range(1, 15):
            surf.set_at((x, 4), hat)
        for x in range(3, 13):
            for y in range(1, 4):
                surf.set_at((x, y), hat)

        # cabelo branco saindo do chapéu
        surf.set_at((3, 5), hair)
        surf.set_at((12, 5), hair)

        # cabeça
        for x in range(4, 12):
            for y in range(5, 11):
                surf.set_at((x, y), skin)
        # bigode branco
        for x in range(5, 11):
            surf.set_at((x, 9), hair)
        # olhos com rugas
        if direction == 1:
            surf.set_at((7, 7), black)
            surf.set_at((9, 7), black)
            surf.set_at((6, 6), dark_skin)
            surf.set_at((10, 6), dark_skin)
        else:
            surf.set_at((6, 7), black)
            surf.set_at((8, 7), black)

        # tronco: camisa creme
        for x in range(4, 12):
            for y in range(12, 21):
                surf.set_at((x, y), shirt)
        for y in range(12, 21):
            surf.set_at((4, y), (150, 150, 120))

        # bengala
        cx = 14 if direction == 1 else 1
        for y in range(13, 32):
            surf.set_at((cx, y), cane)
        surf.set_at((cx-1, 13), cane)
        surf.set_at((cx-2, 13), cane)

        # braços
        for y in range(13, 21):
            surf.set_at((2, y), shirt)
            surf.set_at((3, y), skin)
            surf.set_at((13, y), shirt)

        # calça
        for x in range(4, 12):
            for y in range(21, 27):
                surf.set_at((x, y), pants)

        # sapatos
        for x in range(3, 9):
            surf.set_at((x, 27), black)
            surf.set_at((x, 28), black)
        for x in range(8, 13):
            surf.set_at((x, 27), black)
            surf.set_at((x, 28), black)

        _cache[key] = _outline(surf)
    return _cache[key]


# ─────────────────────────────────────────────
#  NPC ALDEÃO GENÉRICO — 16x32
# ─────────────────────────────────────────────

def get_npc_villager(variant=0, direction=1):
    key = ("villager", variant, direction)
    if key not in _cache:
        surf = _new(16, 32)
        # variações de cor por variant
        shirt_colors = [
            (180, 160, 100), (100, 160, 80), (80, 100, 180), (160, 80, 80)
        ]
        pants_colors = [
            (80, 60, 30), (60, 80, 40), (40, 60, 100), (100, 50, 50)
        ]
        shirt = shirt_colors[variant % len(shirt_colors)]
        pants = pants_colors[variant % len(pants_colors)]
        skin  = (210 - variant*10, 160 - variant*5, 110 - variant*5)
        hat   = (120 - variant*10, 80 - variant*5, 20)
        black = (0, 0, 0)
        dark_skin = (skin[0]-40, skin[1]-40, skin[2]-40)

        # chapéu simples
        for x in range(3, 13):
            surf.set_at((x, 4), hat)
        for x in range(5, 11):
            for y in range(1, 4):
                surf.set_at((x, y), hat)

        # cabeça
        for x in range(4, 12):
            for y in range(5, 11):
                surf.set_at((x, y), skin)
        # olhos
        if direction == 1:
            surf.set_at((7, 7), black)
            surf.set_at((9, 7), black)
        else:
            surf.set_at((6, 7), black)
            surf.set_at((8, 7), black)

        # tronco
        for x in range(4, 12):
            for y in range(12, 21):
                surf.set_at((x, y), shirt)
        for y in range(12, 21):
            surf.set_at((4, y), (shirt[0]-30, shirt[1]-30, shirt[2]-30))

        # braços
        for y in range(13, 21):
            surf.set_at((2, y), shirt)
            surf.set_at((3, y), skin)
            surf.set_at((13, y), shirt)
            surf.set_at((12, y), skin)

        # calça
        for x in range(4, 12):
            for y in range(21, 27):
                surf.set_at((x, y), pants)
        for y in range(21, 27):
            surf.set_at((7, y), (pants[0]-20, pants[1]-20, pants[2]-20))
            surf.set_at((8, y), (pants[0]-20, pants[1]-20, pants[2]-20))

        # sapatos/pés
        for x in range(3, 9):
            surf.set_at((x, 27), (50, 35, 15))
            surf.set_at((x, 28), (50, 35, 15))
        for x in range(8, 13):
            surf.set_at((x, 27), (50, 35, 15))
            surf.set_at((x, 28), (50, 35, 15))

        _cache[key] = _outline(surf)
    return _cache[key]


# ─────────────────────────────────────────────
#  ÍCONE DA JANELA — pedra âmbar 16x16
# ─────────────────────────────────────────────

def get_window_icon():
    surf = pygame.Surface((16, 16))
    surf.fill((0, 0, 0))
    surf.set_colorkey((0, 0, 0))
    amber  = (200, 130, 30)
    light  = (240, 200, 80)
    dark   = (120, 70, 10)
    glow   = (255, 220, 100)
    # forma de pedra irregular
    points = [(8,1),(13,4),(14,10),(11,15),(5,15),(2,10),(3,4)]
    pygame.draw.polygon(surf, amber, points)
    # brilho central
    pygame.draw.line(surf, light, (8,3), (11,9), 1)
    pygame.draw.line(surf, light, (7,4), (9,10), 1)
    # sombra
    pygame.draw.line(surf, dark, (3,5), (5,14), 1)
    # glow ponto
    surf.set_at((9, 6), glow)
    surf.set_at((10, 6), glow)
    return surf
