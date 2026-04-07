# shared/enums.py — enumerações globais do jogo

from enum import Enum, auto, IntEnum


class SceneID(str, Enum):
    INTRO   = "intro"
    VILLAGE = "village"
    TRAIL   = "trail"
    CAVE    = "cave"
    ENDING  = "ending"


class PlayerState(Enum):
    IDLE      = auto()
    WALKING   = auto()
    JUMPING   = auto()
    FALLING   = auto()
    ATTACKING = auto()
    HURT      = auto()
    DEAD      = auto()


class TileID(IntEnum):
    AIR            = 0
    PEDRA_TOPO     = 1
    PEDRA_MEIO     = 2
    PEDRA_BASE     = 3
    TERRA          = 4
    CACTO_BASE     = 5
    CACTO_TOPO     = 6
    TREPADEIRA     = 7
    PEDRA_CASTELO  = 8
    ROCHA_CAVE     = 9
    ROCHA_GLOW     = 10
    CRISTAL        = 11
    AGUA           = 12
    GRAMA_SECA     = 13
    POTE           = 14
    CAIXOTE        = 15


SOLID_TILE_IDS: frozenset[int] = frozenset({
    TileID.PEDRA_TOPO, TileID.PEDRA_MEIO, TileID.PEDRA_BASE,
    TileID.TERRA, TileID.PEDRA_CASTELO, TileID.ROCHA_CAVE,
    TileID.ROCHA_GLOW, TileID.CRISTAL, TileID.CAIXOTE,
})


class GameEvent(str, Enum):
    """Eventos publicados no EventBus."""
    PLAYER_DAMAGED   = "player_damaged"
    PLAYER_DIED      = "player_died"
    PLAYER_HEALED    = "player_healed"
    ENEMY_KILLED     = "enemy_killed"
    DIALOGUE_OPENED  = "dialogue_opened"
    DIALOGUE_CLOSED  = "dialogue_closed"
    DIALOGUE_ADVANCE = "dialogue_advance"
    POT_BROKEN       = "pot_broken"
    ITEM_COLLECTED   = "item_collected"
    SCENE_TRANSITION = "scene_transition"
    KARMA_CHANGED    = "karma_changed"
    BOSS_DEFEATED    = "boss_defeated"
