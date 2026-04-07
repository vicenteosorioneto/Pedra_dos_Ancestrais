# settings.py — SHIM de compatibilidade
#
# Este arquivo existe para não quebrar imports legados.
# Toda configuração real mora em config/.
# Novos módulos devem importar diretamente de config/.

from config.display  import SCREEN_W, SCREEN_H, WINDOW_W, WINDOW_H, SCALE, FPS, TITLE
from config.physics  import (
    PLAYER_SPEED, PLAYER_JUMP_FORCE, PLAYER_GRAVITY,
    PLAYER_MAX_FALL, COYOTE_FRAMES, JUMP_BUFFER_FRAMES, TILE_SIZE,
)
from config.palette  import PALETTE_SERTAO, PALETTE_CAVE, BLACK, WHITE, GOLD
from config.scene_ids import (
    SCENE_INTRO, SCENE_VILLAGE, SCENE_TRAIL, SCENE_CAVE, SCENE_ENDING,
)
