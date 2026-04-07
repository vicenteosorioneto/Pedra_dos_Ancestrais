# tests/test_dialogue_loader.py — testes do DialogueLoader
# Executar com: pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.dialogue_loader import DialogueLoader


class TestDialogueLoader:
    def test_carrega_aldeao_1(self):
        loader = DialogueLoader()
        lines = loader.get("aldeao_1")
        assert isinstance(lines, list)
        assert len(lines) > 0
        assert "Pedra" in lines[1] or "Pedra" in lines[0]

    def test_chave_inexistente_retorna_fallback(self):
        loader = DialogueLoader()
        lines = loader.get("npc_que_nao_existe_xyz")
        assert lines == ["..."]

    def test_has_retorna_true_para_chave_existente(self):
        loader = DialogueLoader()
        assert loader.has("zequinha") is True

    def test_has_retorna_false_para_chave_inexistente(self):
        loader = DialogueLoader()
        assert loader.has("personagem_fantasma") is False

    def test_arquivo_invalido_nao_quebra(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ isso nao e json valido")
        loader = DialogueLoader(path=bad_file)
        assert loader.get("qualquer") == ["..."]
