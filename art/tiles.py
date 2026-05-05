# art/tiles.py — geração procedural de tiles 16x16

import pygame
from settings import PALETTE_SERTAO as P, PALETTE_CAVE as C, TILE_SIZE

# Cache de tiles gerados
_tile_cache = {}

def _s(key):
    return P[key]

def _c(key):
    return C[key]

def _make_surface():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill((0, 0, 0))
    return surf

def _draw_noise(surf, base_color, variation=15, density=6):
    """Adiciona pixels de variação para textura."""
    import random
    rng = random.Random(hash(base_color))
    r, g, b = base_color
    for _ in range(density):
        x = rng.randint(0, TILE_SIZE - 1)
        y = rng.randint(0, TILE_SIZE - 1)
        v = rng.randint(-variation, variation)
        nc = (max(0, min(255, r+v)), max(0, min(255, g+v)), max(0, min(255, b+v)))
        surf.set_at((x, y), nc)

def tile_pedra_topo():
    surf = _make_surface()
    base = _s("rock_mid")
    top  = _s("platform_top")
    dark = _s("rock_dark")
    # corpo da pedra
    surf.fill(base)
    # topo mais claro (2 pixels)
    for x in range(TILE_SIZE):
        surf.set_at((x, 0), top)
        surf.set_at((x, 1), top)
    # linha de sombra na base
    for x in range(TILE_SIZE):
        surf.set_at((x, TILE_SIZE-1), dark)
    # borda esquerda escura
    for y in range(TILE_SIZE):
        surf.set_at((0, y), dark)
    # highlight direito
    light = _s("rock_light")
    for y in range(2, TILE_SIZE-1):
        surf.set_at((TILE_SIZE-1, y), light)
    _draw_noise(surf, base, 10, 8)
    return surf

def tile_pedra_meio():
    surf = _make_surface()
    base = _s("rock_mid")
    dark = _s("rock_dark")
    surf.fill(base)
    for y in range(TILE_SIZE):
        surf.set_at((0, y), dark)
    for x in range(TILE_SIZE):
        surf.set_at((x, TILE_SIZE-1), dark)
    _draw_noise(surf, base, 12, 6)
    return surf

def tile_pedra_base():
    surf = _make_surface()
    base = _s("rock_dark")
    surf.fill(base)
    _draw_noise(surf, base, 8, 6)
    return surf

def tile_terra():
    surf = _make_surface()
    base = _s("soil")
    surf.fill(base)
    # grãos de terra
    import random
    rng = random.Random(42)
    for _ in range(10):
        x = rng.randint(0, TILE_SIZE-1)
        y = rng.randint(0, TILE_SIZE-1)
        surf.set_at((x, y), _s("rock_dark"))
    _draw_noise(surf, base, 15, 8)
    return surf

def tile_cacto_base():
    surf = _make_surface()
    surf.fill((0, 0, 0))
    surf.set_colorkey((0, 0, 0))
    base = _s("cactus")
    dark = _s("cactus_dark")
    # tronco central (4px largura)
    for y in range(TILE_SIZE):
        for x in range(6, 10):
            surf.set_at((x, y), base)
    # sombra esquerda do tronco
    for y in range(TILE_SIZE):
        surf.set_at((6, y), dark)
    # braços do cacto
    for x in range(3, 6):
        surf.set_at((x, 6), base)
        surf.set_at((x, 7), base)
        surf.set_at((3, 4), base)
        surf.set_at((3, 5), base)
    for x in range(10, 13):
        surf.set_at((x, 9), base)
        surf.set_at((x, 10), base)
        surf.set_at((12, 7), base)
        surf.set_at((12, 8), base)
    return surf

def tile_cacto_topo():
    surf = _make_surface()
    surf.fill((0, 0, 0))
    surf.set_colorkey((0, 0, 0))
    base = _s("cactus")
    dark = _s("cactus_dark")
    light = (80, 150, 70)
    # tronco central
    for y in range(8, TILE_SIZE):
        for x in range(6, 10):
            surf.set_at((x, y), base)
    # topo arredondado
    for x in range(6, 10):
        for y in range(3, 8):
            surf.set_at((x, y), base)
    surf.set_at((7, 2), base)
    surf.set_at((8, 2), base)
    # espinhos
    surf.set_at((5, 4), dark)
    surf.set_at((10, 4), dark)
    surf.set_at((5, 6), dark)
    surf.set_at((10, 6), dark)
    surf.set_at((7, 1), dark)
    surf.set_at((8, 1), dark)
    # highlight
    for y in range(3, TILE_SIZE):
        surf.set_at((9, y), light)
    return surf

def tile_trepadeira():
    surf = _make_surface()
    surf.fill((0, 0, 0))
    surf.set_colorkey((0, 0, 0))
    vine = _s("vine")
    dark = (30, 70, 25)
    # hastes verticais sinuosas
    for y in range(TILE_SIZE):
        x = 4 + (y % 3)
        surf.set_at((x, y), vine)
        x2 = 10 + (y % 2)
        surf.set_at((x2, y), vine)
    # folhinhas
    positions = [(3, 3), (6, 7), (9, 2), (12, 10), (2, 12)]
    for px, py in positions:
        if 0 <= px < TILE_SIZE and 0 <= py < TILE_SIZE:
            surf.set_at((px, py), vine)
            if px+1 < TILE_SIZE:
                surf.set_at((px+1, py), dark)
    return surf

def tile_pedra_castelo():
    surf = _make_surface()
    base = _s("rock_mid")
    dark = _s("rock_dark")
    light = _s("rock_light")
    surf.fill(base)
    # padrão de pedra lavrada
    for y in range(0, TILE_SIZE, 4):
        for x in range(TILE_SIZE):
            surf.set_at((x, y), dark)
    for x in range(0, TILE_SIZE, 8):
        for y in range(TILE_SIZE):
            surf.set_at((x, y), dark)
    # "janelas" escuras
    surf.set_at((3, 5), (10, 5, 15))
    surf.set_at((4, 5), (10, 5, 15))
    surf.set_at((3, 6), (10, 5, 15))
    surf.set_at((4, 6), (10, 5, 15))
    surf.set_at((11, 2), (10, 5, 15))
    surf.set_at((12, 2), (10, 5, 15))
    surf.set_at((11, 3), (10, 5, 15))
    surf.set_at((12, 3), (10, 5, 15))
    _draw_noise(surf, base, 8, 4)
    return surf

def tile_rocha_cave():
    surf = _make_surface()
    base = _c("rock_cave")
    surf.fill(base)
    dark = _c("bg_deep")
    for y in range(0, TILE_SIZE, 5):
        for x in range(TILE_SIZE):
            surf.set_at((x, y), dark)
    _draw_noise(surf, base, 10, 6)
    return surf

def tile_rocha_glow():
    surf = _make_surface()
    base = _c("rock_glow")
    surf.fill(base)
    glow = _c("biolum")
    # pontos bioluminescentes
    spots = [(2,3),(5,8),(9,2),(12,11),(7,6),(14,5)]
    for px, py in spots:
        surf.set_at((px, py), glow)
        if px+1 < TILE_SIZE:
            surf.set_at((px+1, py), (glow[0]//2, glow[1]//2, glow[2]//2))
    _draw_noise(surf, base, 8, 4)
    return surf

def tile_crystal():
    surf = _make_surface()
    surf.fill((0, 0, 0))
    surf.set_colorkey((0, 0, 0))
    amber = _c("amber_glow")
    light = (240, 200, 80)
    dark  = (120, 70, 10)
    # forma de cristal
    points = [(8,1),(12,5),(13,11),(10,15),(6,15),(3,11),(4,5)]
    pygame.draw.polygon(surf, amber, points)
    # highlight
    pygame.draw.line(surf, light, (8,2), (11,8), 1)
    # sombra
    pygame.draw.line(surf, dark, (4,6), (6,14), 1)
    return surf

def tile_water():
    surf = _make_surface()
    surf.fill((30, 80, 160))
    # ondas
    for x in range(0, TILE_SIZE, 3):
        surf.set_at((x, 4), (60, 120, 200))
        surf.set_at((x+1, 4), (80, 140, 220))
    for x in range(0, TILE_SIZE, 4):
        surf.set_at((x, 10), (40, 100, 180))
    return surf

def tile_grass_dry():
    surf = _make_surface()
    soil = _s("soil")
    grass = (100, 130, 40)
    dark_grass = (70, 100, 25)
    surf.fill(soil)
    # tufos de grama
    for x in range(0, TILE_SIZE, 3):
        h = 2 + (x % 3)
        for y in range(h):
            surf.set_at((x, y), grass if y < h-1 else dark_grass)
    return surf

def tile_pot():
    surf = _make_surface()
    surf.fill((0, 0, 0))
    surf.set_colorkey((0, 0, 0))
    base = (160, 100, 60)
    dark = (100, 60, 30)
    light = (200, 140, 90)
    # corpo do pote
    pygame.draw.ellipse(surf, base, (3, 6, 10, 9))
    pygame.draw.rect(surf, base, (5, 3, 6, 6))
    # boca do pote
    pygame.draw.ellipse(surf, dark, (4, 2, 8, 3))
    # highlight
    surf.set_at((5, 7), light)
    surf.set_at((5, 8), light)
    surf.set_at((5, 9), light)
    return surf

def tile_crate():
    surf = _make_surface()
    base = (140, 100, 50)
    dark = (80, 55, 20)
    light = (180, 140, 80)
    surf.fill(base)
    # bordas do caixote
    pygame.draw.rect(surf, dark, (0, 0, TILE_SIZE, TILE_SIZE), 1)
    # tábuas verticais
    surf.set_at((5, 1), dark)
    for y in range(1, TILE_SIZE-1):
        surf.set_at((5, y), dark)
        surf.set_at((10, y), dark)
    # tábua horizontal do meio
    for x in range(1, TILE_SIZE-1):
        surf.set_at((x, 7), dark)
    # highlight
    for y in range(1, 7):
        surf.set_at((1, y), light)
    return surf


# Mapa: id → função geradora
TILE_GENERATORS = {
    0:  None,
    1:  tile_pedra_topo,
    2:  tile_pedra_meio,
    3:  tile_pedra_base,
    4:  tile_terra,
    5:  tile_cacto_base,
    6:  tile_cacto_topo,
    7:  tile_trepadeira,
    8:  tile_pedra_castelo,
    9:  tile_rocha_cave,
    10: tile_rocha_glow,
    11: tile_crystal,
    12: tile_water,
    13: tile_grass_dry,
    14: tile_pot,
    15: tile_crate,
}

SOLID_TILES = {1, 2, 3, 4, 8, 9, 10, 15}

def get_tile_surface(tile_id):
    """Retorna Surface cacheada para o tile_id."""
    if tile_id not in _tile_cache:
        gen = TILE_GENERATORS.get(tile_id)
        if gen is None:
            _tile_cache[tile_id] = None
        else:
            _tile_cache[tile_id] = gen()
    return _tile_cache[tile_id]

def is_solid(tile_id):
    return tile_id in SOLID_TILES
