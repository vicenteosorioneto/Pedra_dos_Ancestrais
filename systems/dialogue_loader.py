# systems/dialogue_loader.py — carrega diálogos de JSON

from __future__ import annotations
import json
from pathlib import Path

_DEFAULT_PATH = Path(__file__).parent.parent / "content" / "dialogue" / "npcs.json"


class DialogueLoader:
    """
    Carrega diálogos de um arquivo JSON.
    Formato esperado: { "npc_key": ["linha 1", "linha 2", ...] }
    """

    def __init__(self, path: str | Path = _DEFAULT_PATH) -> None:
        self._data: dict[str, list[str]] = {}
        self._load(path)

    def _load(self, path: str | Path) -> None:
        p = Path(path)
        if not p.exists():
            return
        try:
            with p.open(encoding="utf-8") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._data = {}

    def get(self, npc_key: str) -> list[str]:
        """Retorna as linhas de diálogo para a chave dada, ou ['...'] se não encontrar."""
        return self._data.get(npc_key, ["..."])

    def has(self, npc_key: str) -> bool:
        return npc_key in self._data
