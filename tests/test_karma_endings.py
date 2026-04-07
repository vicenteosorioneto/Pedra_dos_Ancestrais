# tests/test_karma_endings.py — testes de integração dos cenários de final
# Executar com: pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.karma import KarmaSystem, KarmaSummary


# ── Finais por cenário completo de jogo ───────────────────────────────────────

class TestFinalVerdadeiro:
    """Cenários que devem produzir o final 'verdadeiro'."""

    def test_heroi_classico(self):
        """Matou inimigos, conversou com NPCs, aceitou trato da Iracema."""
        k = KarmaSystem()
        k.enfrentou_inimigo()   # trilha bat 1
        k.enfrentou_inimigo()   # trilha bat 2
        k.conversou_com_npc()   # aldeão 1
        k.conversou_com_npc()   # aldeão 2
        k.aceitou_trato_honrou()
        assert k.final_type == "verdadeiro"

    def test_verdadeiro_sem_iracema(self):
        """Coragem e sabedoria altas sem precisar do bônus de Iracema."""
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        k.conversou_com_npc()
        k.conversou_com_npc()
        k.conversou_com_npc()
        # ganancia == 0 → deve ser verdadeiro
        assert k.final_type == "verdadeiro"

    def test_verdadeiro_com_ganancia_limite(self):
        """Ganância máxima permitida no final verdadeiro é 1."""
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        k.conversou_com_npc()
        k.conversou_com_npc()
        k.pegou_item_armadilha()   # ganância = 1 — ainda dentro do limite
        assert k.final_type == "verdadeiro"

    def test_verdadeiro_ajudou_espirito(self):
        """ajudou_espirito conta como coragem (guardião derrotado na caverna)."""
        k = KarmaSystem()
        k.ajudou_espirito()        # +1 coragem via boss
        k.enfrentou_inimigo()      # +1 coragem via morcego
        k.conversou_com_npc()
        k.conversou_com_npc()
        assert k.final_type == "verdadeiro"


class TestFinalRuim:
    """Cenários que devem produzir o final 'ruim' (ganância ≥ 3)."""

    def test_ganancioso_puro(self):
        """Pegou 3 itens-armadilha sem nenhuma virtude."""
        k = KarmaSystem()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        assert k.final_type == "ruim"

    def test_ganancioso_mesmo_com_coragem(self):
        """Ganância domina mesmo com coragem alta."""
        k = KarmaSystem()
        for _ in range(5):
            k.enfrentou_inimigo()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        assert k.final_type == "ruim"

    def test_ganancioso_e_covarde(self):
        """Ignorou NPCs em perigo + pegou armadilhas → ruim."""
        k = KarmaSystem()
        k.ignorou_npc_em_perigo()
        k.ignorou_npc_em_perigo()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()
        assert k.final_type == "ruim"

    def test_potes_destroem_reputacao(self):
        """destruiu_pote_decorativo também incrementa ganância."""
        k = KarmaSystem()
        k.destruiu_pote_decorativo()
        k.destruiu_pote_decorativo()
        k.destruiu_pote_decorativo()
        assert k.final_type == "ruim"

    def test_ganancia_5_sempre_ruim(self):
        """Teto de ganância (5) → ruim independente de virtudes."""
        k = KarmaSystem()
        for _ in range(10):          # cap em 5
            k.pegou_item_armadilha()
        assert k.ganancia == 5
        assert k.final_type == "ruim"


class TestFinalNeutro:
    """Cenários que devem produzir o final 'neutro'."""

    def test_indiferente(self):
        """Jogador que não fez nada relevante."""
        k = KarmaSystem()
        assert k.final_type == "neutro"

    def test_coragem_sem_sabedoria(self):
        """Coragem alta mas sabedoria insuficiente → neutro."""
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        # sabedoria = 0 → não atinge limiar do verdadeiro
        assert k.final_type == "neutro"

    def test_sabedoria_sem_coragem(self):
        """Conversou com todos mas não lutou → neutro."""
        k = KarmaSystem()
        k.conversou_com_npc()
        k.conversou_com_npc()
        k.conversou_com_npc()
        # coragem = 0 → não atinge limiar do verdadeiro
        assert k.final_type == "neutro"

    def test_ganancia_2_bloqueia_verdadeiro(self):
        """ganância = 2 ainda está acima do limite para verdadeiro (≤ 1)."""
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        k.conversou_com_npc()
        k.conversou_com_npc()
        k.pegou_item_armadilha()
        k.pegou_item_armadilha()   # ganância = 2 → bloqueia verdadeiro
        assert k.final_type == "neutro"

    def test_recusar_iracema_nao_muda_final(self):
        """Recusar o trato não penaliza — apenas não adiciona bônus."""
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.enfrentou_inimigo()
        k.conversou_com_npc()
        k.conversou_com_npc()
        k.recusou_trato()          # divida_iracema = None
        # coragem≥2, sabedoria≥2, ganância=0 → verdadeiro (recusa é neutra)
        assert k.final_type == "verdadeiro"


# ── Testes de limite e caps ───────────────────────────────────────────────────

class TestKarmaLimites:
    def test_coragem_cap_5(self):
        k = KarmaSystem()
        for _ in range(10):
            k.enfrentou_inimigo()
        assert k.coragem == 5

    def test_sabedoria_cap_5(self):
        k = KarmaSystem()
        for _ in range(10):
            k.conversou_com_npc()
        assert k.sabedoria == 5

    def test_coragem_nao_negativa(self):
        k = KarmaSystem()
        for _ in range(10):
            k.ignorou_npc_em_perigo()
        assert k.coragem == 0

    def test_ganancia_nao_negativa(self):
        k = KarmaSystem()
        for _ in range(5):
            k.deixou_item_valioso()
        assert k.ganancia == 0

    def test_summary_e_dataclass(self):
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.conversou_com_npc()
        k.aceitou_trato_honrou()
        s = k.get_summary()
        assert isinstance(s, KarmaSummary)
        assert s.coragem == 1
        assert s.sabedoria == 1
        assert s.divida_iracema is True
        assert s.final == "neutro"   # só 1 de cada → neutro

    def test_summary_nao_e_dict(self):
        """Garante que KarmaSummary não aceita acesso por chave de dict."""
        k = KarmaSystem()
        s = k.get_summary()
        try:
            _ = s["coragem"]
            assert False, "KarmaSummary não deve aceitar acesso por chave"
        except TypeError:
            pass   # correto — é dataclass, não dict


# ── Fluxo completo de jogo (smoke test) ──────────────────────────────────────

class TestFluxoCompleto:
    def test_jogo_completo_verdadeiro(self):
        """
        Simula o fluxo completo de uma partida heroica:
        Village → Trail → Cave → Ending.
        """
        k = KarmaSystem()

        # ATO 1 — Vila
        k.conversou_com_npc()   # aldeão 1
        k.conversou_com_npc()   # aldeão 2
        k.conversou_com_npc()   # comerciante

        # ATO 2 — Trilha (3 altares + morcegos)
        k.enfrentou_inimigo()   # morcego 1
        k.enfrentou_inimigo()   # morcego 2

        # ATO 3 — Caverna (morcegos + guardião)
        k.enfrentou_inimigo()   # morcego cave
        k.ajudou_espirito()     # guardião derrotado
        k.aceitou_trato_honrou()  # aceitou proposta de Iracema
        k.conversou_com_npc()   # diálogo pós-aceitação

        summ = k.get_summary()
        assert summ.coragem >= 2
        assert summ.sabedoria >= 2
        assert summ.ganancia <= 1
        assert summ.divida_iracema is True
        assert k.final_type == "verdadeiro"

    def test_jogo_completo_ruim(self):
        """
        Simula partida gananciosa: quebrou potes, pegou armadilhas,
        ignorou NPCs.
        """
        k = KarmaSystem()

        # Ignorou aldeões
        k.ignorou_npc_em_perigo()
        k.ignorou_npc_em_perigo()

        # Quebrou potes decorativos
        k.destruiu_pote_decorativo()
        k.destruiu_pote_decorativo()

        # Pegou item armadilha
        k.pegou_item_armadilha()   # ganância = 3 → final ruim garantido

        assert k.final_type == "ruim"

    def test_jogo_completo_neutro(self):
        """
        Jogador casual: matou alguns inimigos, conversou pouco,
        não teve ganância excessiva.
        """
        k = KarmaSystem()
        k.enfrentou_inimigo()
        k.conversou_com_npc()   # só 1 conversa — sabedoria = 1
        k.recusou_trato()

        assert k.final_type == "neutro"
