# shared/utils.py — utilitários genéricos sem dependência de pygame

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Limita value ao intervalo [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Interpolação linear entre a e b com fator t (0.0–1.0)."""
    return a + (b - a) * t


def load_json(path: str | Path) -> Any:
    """Carrega e retorna um arquivo JSON. Lança FileNotFoundError se ausente."""
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def get_logger(name: str) -> logging.Logger:
    """Retorna logger configurado para o módulo."""
    return logging.getLogger(name)


# Configura o logger raiz do projeto uma única vez
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
