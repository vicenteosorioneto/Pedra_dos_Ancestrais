# systems/karma.py — sistema de karma silencioso

class KarmaSystem:
    def __init__(self):
        self.coragem   = 0  # 0-5
        self.ganancia  = 0  # 0-5
        self.sabedoria = 0  # 0-5
        self.divida_iracema = None  # True/False/None

    # ── Coragem ───────────────────────────────────
    def ajudou_espirito(self):
        self.coragem = min(5, self.coragem + 1)

    def enfrentou_inimigo(self):
        self.coragem = min(5, self.coragem + 1)

    def ignorou_npc_em_perigo(self):
        self.coragem = max(0, self.coragem - 1)

    # ── Ganância ──────────────────────────────────
    def pegou_item_armadilha(self):
        self.ganancia = min(5, self.ganancia + 1)

    def destruiu_pote_decorativo(self):
        self.ganancia = min(5, self.ganancia + 1)

    def deixou_item_valioso(self):
        self.ganancia = max(0, self.ganancia - 1)

    # ── Sabedoria ─────────────────────────────────
    def leu_registro(self):
        self.sabedoria = min(5, self.sabedoria + 1)

    def resolveu_puzzle_perfeito(self):
        self.sabedoria = min(5, self.sabedoria + 1)

    def conversou_com_npc(self):
        self.sabedoria = min(5, self.sabedoria + 1)

    # ── Iracema ───────────────────────────────────
    def aceitou_trato_honrou(self):
        self.divida_iracema = True

    def aceitou_trato_traiu(self):
        self.divida_iracema = False

    def recusou_trato(self):
        self.divida_iracema = None

    # ── Final computado ───────────────────────────
    @property
    def final_type(self):
        if self.ganancia >= 3:
            return "ruim"
        if self.coragem >= 2 and self.sabedoria >= 2 and self.ganancia <= 1:
            return "verdadeiro"
        return "neutro"

    def get_summary(self):
        return {
            "coragem":   self.coragem,
            "ganancia":  self.ganancia,
            "sabedoria": self.sabedoria,
            "divida":    self.divida_iracema,
            "final":     self.final_type,
        }
