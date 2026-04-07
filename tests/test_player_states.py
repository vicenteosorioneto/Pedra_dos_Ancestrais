# tests/test_player_states.py — testes da máquina de estados do player
# Executar com: pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.enums import PlayerState
from gameplay.player.states import VALID_TRANSITIONS


class TestPlayerStateTransitions:
    def test_idle_pode_ir_para_walking(self):
        assert PlayerState.WALKING in VALID_TRANSITIONS[PlayerState.IDLE]

    def test_idle_pode_ir_para_jumping(self):
        assert PlayerState.JUMPING in VALID_TRANSITIONS[PlayerState.IDLE]

    def test_dead_nao_tem_transicoes(self):
        assert len(VALID_TRANSITIONS[PlayerState.DEAD]) == 0

    def test_hurt_pode_ir_para_dead(self):
        assert PlayerState.DEAD in VALID_TRANSITIONS[PlayerState.HURT]

    def test_hurt_pode_ir_para_idle(self):
        assert PlayerState.IDLE in VALID_TRANSITIONS[PlayerState.HURT]

    def test_attacking_nao_pode_ir_para_jumping(self):
        assert PlayerState.JUMPING not in VALID_TRANSITIONS[PlayerState.ATTACKING]

    def test_todos_estados_tem_entrada_na_tabela(self):
        for state in PlayerState:
            assert state in VALID_TRANSITIONS, f"Estado {state} sem entrada em VALID_TRANSITIONS"
