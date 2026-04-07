# gameplay/player/states.py — máquina de estados do player

from shared.enums import PlayerState

# Transições válidas: de cada estado, quais estados pode ir
VALID_TRANSITIONS: dict[PlayerState, frozenset[PlayerState]] = {
    PlayerState.IDLE: frozenset({
        PlayerState.WALKING, PlayerState.JUMPING, PlayerState.FALLING,
        PlayerState.ATTACKING, PlayerState.HURT, PlayerState.DEAD,
    }),
    PlayerState.WALKING: frozenset({
        PlayerState.IDLE, PlayerState.JUMPING, PlayerState.FALLING,
        PlayerState.ATTACKING, PlayerState.HURT, PlayerState.DEAD,
    }),
    PlayerState.JUMPING: frozenset({
        PlayerState.FALLING, PlayerState.IDLE, PlayerState.WALKING,
        PlayerState.ATTACKING, PlayerState.HURT, PlayerState.DEAD,
    }),
    PlayerState.FALLING: frozenset({
        PlayerState.IDLE, PlayerState.WALKING,
        PlayerState.HURT, PlayerState.DEAD,
    }),
    PlayerState.ATTACKING: frozenset({
        PlayerState.IDLE, PlayerState.HURT, PlayerState.DEAD,
    }),
    PlayerState.HURT: frozenset({
        PlayerState.IDLE, PlayerState.DEAD,
    }),
    PlayerState.DEAD: frozenset(),  # estado terminal
}
