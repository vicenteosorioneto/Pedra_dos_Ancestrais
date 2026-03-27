# art/palette.py — utilitários de paleta
from settings import PALETTE_SERTAO, PALETTE_CAVE

def get(key, cave=False):
    """Retorna cor da paleta ativa."""
    pal = PALETTE_CAVE if cave else PALETTE_SERTAO
    return pal.get(key, (255, 0, 255))  # magenta = cor faltando

def darken(color, amount=30):
    r, g, b = color
    return (max(0, r - amount), max(0, g - amount), max(0, b - amount))

def lighten(color, amount=30):
    r, g, b = color
    return (min(255, r + amount), min(255, g + amount), min(255, b + amount))
