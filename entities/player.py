# entities/player.py — SHIM
# A implementação real está em gameplay/player/player.py
# Este arquivo existe para não quebrar imports legados.

from gameplay.player.player import Player

__all__ = ["Player"]
