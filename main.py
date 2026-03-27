#!/usr/bin/env python3
"""
A Pedra dos Ancestrais
======================
Um jogo 2D de plataforma com RPG leve ambientado no sertão nordestino.

Dependências:
  pip install pygame>=2.1.0

Como jogar:
  python main.py

Controles:
  WASD / Setas  — mover
  Espaço        — pular
  Z ou J        — atacar
  X ou K        — interagir
  ESC           — pausar
"""

import sys
import os

# Garante que o diretório do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pygame
except ImportError:
    print("ERRO: Pygame não encontrado.")
    print("Instale com: pip install pygame>=2.1.0")
    sys.exit(1)

from core.game import Game


if __name__ == "__main__":
    game = Game()
    game.run()
