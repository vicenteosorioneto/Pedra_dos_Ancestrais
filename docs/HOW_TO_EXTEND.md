# Como estender o jogo

Guia prático para adicionar conteúdo novo sem quebrar o que já existe.

---

## Sumário

1. [Adicionar uma nova cena (ato)](#1-adicionar-uma-nova-cena-ato)
2. [Adicionar um novo inimigo](#2-adicionar-um-novo-inimigo)
3. [Adicionar um novo NPC](#3-adicionar-um-novo-npc)
4. [Adicionar diálogo](#4-adicionar-diálogo)
5. [Adicionar um novo tile](#5-adicionar-um-novo-tile)
6. [Adicionar um evento de karma](#6-adicionar-um-evento-de-karma)
7. [Ajustar física e constantes](#7-ajustar-física-e-constantes)

---

## 1. Adicionar uma nova cena (ato)

### Passo 1 — Registrar o ID em `settings.py`

```python
# settings.py
SCENE_INTRO   = "intro"
SCENE_VILLAGE = "village"
SCENE_TRAIL   = "trail"
SCENE_CAVE    = "cave"
SCENE_ENDING  = "ending"   # ← novo
```

### Passo 2 — Criar o arquivo em `scenes/`

```python
# scenes/ending_scene.py

import pygame
from settings import SCREEN_W, SCREEN_H, GOLD

class EndingScene:
    def __init__(self, scene_manager, karma):
        self.scene_manager = scene_manager
        self.karma = karma

    # ── Ciclo de vida ──────────────────────────────
    def on_enter(self):
        pass          # inicializar recursos aqui

    def on_exit(self):
        pass          # liberar recursos aqui

    def on_resume(self):
        pass          # chamado ao voltar do topo (pop de outra cena)

    # ── Loop ──────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.scene_manager.pop()

    def update(self):
        pass

    def draw(self, surf):
        surf.fill((0, 0, 0))
        # desenhar o ending aqui
```

### Passo 3 — Disparar a transição na cena anterior

```python
# dentro de cave_scene.py, quando o boss for derrotado:
from scenes.ending_scene import EndingScene

ending = EndingScene(self.scene_manager, self.karma)
self.scene_manager.replace(ending)
```

---

## 2. Adicionar um novo inimigo

### Passo 1 — Criar a classe em `entities/`

Herdar de `Enemy` (já tem física, colisão e `take_damage`):

```python
# entities/rock_golem.py

import pygame
from entities.enemy import Enemy
from art.sprites import get_golem_frame   # criar esta função em art/sprites.py

class RockGolem(Enemy):
    SPEED = 0.8

    def __init__(self, x, y):
        super().__init__(x, y, w=20, h=32)
        self.hp     = 5
        self.max_hp = 5
        self.damage = 2
        self.anim_frame = 0
        self.anim_timer = 0

    def update(self, tilemap, player_rect=None):
        if not self.alive:
            return

        # IA: persegue o player
        if player_rect:
            dx = player_rect.centerx - (self.x + self.w / 2)
            self.vx = self.SPEED if dx > 0 else -self.SPEED
            self.facing = 1 if dx > 0 else -1

        self.apply_gravity()
        self.collide_tilemap(tilemap)

        self.anim_timer += 1
        if self.anim_timer >= 16:
            self.anim_timer = 0
            self.anim_frame = 1 - self.anim_frame

    def draw(self, surf, cam_x, cam_y):
        if not self.alive:
            return
        sprite = get_golem_frame(self.anim_frame)
        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)
        surf.blit(sprite, (int(self.x - cam_x), int(self.y - cam_y)))
```

### Passo 2 — Instanciar na cena

```python
# dentro de cave_scene.py (ou qualquer cena)
from entities.rock_golem import RockGolem

self.enemies = [RockGolem(400, 200)]
```

### Passo 3 — Incluir no loop de update e colisão com o player

```python
# no update() da cena
for enemy in self.enemies:
    enemy.update(self.tilemap, self.player.rect)
    # colisão com ataque do player
    if self.player.attack_active and enemy.rect.colliderect(self.player.attack_rect):
        killed = enemy.take_damage(1)
        if killed:
            self.fx.emit_death(enemy.center[0], enemy.center[1])
    # colisão do inimigo com o player
    if enemy.rect.colliderect(self.player.rect):
        self.player.take_damage(enemy.damage, fx=self.fx)

self.enemies = [e for e in self.enemies if e.alive]
```

---

## 3. Adicionar um novo NPC

### Opção A — Herdar de `NPC` (simples)

```python
# entities/npc.py (adicionar ao final)

class MerchantNPC(NPC):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            npc_key="comerciante",
            sprite_fn=lambda direction: get_npc_villager(1, direction),
            patrol_range=0   # parado
        )
```

### Opção B — NPC com lógica própria

Criar arquivo separado em `entities/` e implementar `update()` / `draw()` / `get_avatar()`.

### Instanciar na cena

```python
# village_scene.py
from entities.npc import MerchantNPC

self.npcs.append(MerchantNPC(320, ground_y))
```

---

## 4. Adicionar diálogo

### Passo 1 — Registrar o texto em `systems/dialogue.py`

```python
# systems/dialogue.py  →  DIALOGUE_DATA
DIALOGUE_DATA = {
    # ... entradas existentes ...
    "ferreiro": [
        "Essa pedra existe antes dos nossos avós.",
        "Dizem que falar o nome dela em voz alta",
        "já é um convite."
    ],
}
```

A chave deve ser única e corresponder ao `npc_key` do NPC.

### Passo 2 — Abrir o diálogo na cena

```python
# no handle_event() da cena, quando o player pressiona X perto do NPC:
self.dialogue.open(
    npc.npc_key,
    avatar_surf=npc.get_avatar(),
    on_close=lambda: self.karma.conversou_com_npc()   # opcional
)
```

### Passo 3 — Repassar eventos para o diálogo

```python
# handle_event()
if self.dialogue.active:
    if event.type == pygame.KEYDOWN and event.key in (pygame.K_x, pygame.K_k, pygame.K_RETURN):
        self.dialogue.advance()
    return   # bloqueia input do player enquanto o diálogo está ativo

# update()
self.dialogue.update()

# draw()
self.dialogue.draw(surf)
```

---

## 5. Adicionar um novo tile

### Passo 1 — Criar a função geradora em `art/tiles.py`

```python
# art/tiles.py

def tile_lava():
    surf = _make_surface()
    surf.fill((180, 40, 10))
    # detalhes de lava
    for x in range(0, TILE_SIZE, 4):
        surf.set_at((x, 3), (220, 100, 20))
    _draw_noise(surf, (180, 40, 10), variation=20, density=6)
    return surf
```

### Passo 2 — Registrar o ID em `TILE_GENERATORS` e `SOLID_TILES`

```python
# art/tiles.py

TILE_GENERATORS = {
    # ... ids existentes ...
    16: tile_lava,   # ← novo ID
}

SOLID_TILES = {1, 2, 3, 4, 8, 9, 10, 11, 15, 16}  # adicionar 16 se for sólido
```

### Passo 3 — Usar na construção do mapa da cena

```python
# scenes/cave_scene.py  →  _build_cave_map()
data[18][30] = 16   # coloca lava na posição col=30, row=18
```

### Passo 4 — (Opcional) Lógica de dano por tile

Verificar no `update()` da cena se o player está sobre um tile de lava:

```python
col = int(self.player.x + self.player.W / 2) // TILE_SIZE
row = int(self.player.y + self.player.H)     // TILE_SIZE
if self.tilemap.get_tile(col, row) == 16:   # ID da lava
    self.player.take_damage(1, fx=self.fx)
```

---

## 6. Adicionar um evento de karma

### Passo 1 — Criar o método em `systems/karma.py`

```python
# systems/karma.py

# ── Coragem ───────────────────────────────────
def salvou_aliado(self):
    self.coragem = min(5, self.coragem + 1)
```

Use prefixos de categoria (`coragem`, `ganancia`, `sabedoria`) para manter
o agrupamento claro.

### Passo 2 — Chamar no momento certo na cena

```python
# exemplo: player ajuda um NPC que estava em perigo
self.karma.salvou_aliado()
```

### Passo 3 — (Opcional) Ajustar o cálculo do final

```python
# systems/karma.py  →  final_type
@property
def final_type(self):
    if self.ganancia >= 3:
        return "ruim"
    if self.coragem >= 2 and self.sabedoria >= 2 and self.ganancia <= 1:
        return "verdadeiro"
    return "neutro"
```

---

## 7. Ajustar física e constantes

Todas as constantes de gameplay estão em `settings.py`. Nenhum outro arquivo
precisa ser modificado para alterar física, resolução ou velocidades.

```python
# settings.py — valores que você pode querer tunar

PLAYER_SPEED       = 2.5    # px/frame
PLAYER_JUMP_FORCE  = -8.0   # negativo = sobe
PLAYER_GRAVITY     = 0.4    # aplicado por frame
PLAYER_MAX_FALL    = 10.0   # velocidade máxima de queda
COYOTE_FRAMES      = 8      # frames de graça após sair da borda
JUMP_BUFFER_FRAMES = 6      # antecipação de pulo
FPS                = 60
TILE_SIZE          = 16     # alterar requer rever todos os mapas
```

> **Atenção:** `TILE_SIZE` afeta diretamente o layout de todos os tilemaps.
> Altere apenas se estiver reconstruindo os mapas junto.

---

## Convenções de código

| Item                  | Convenção                                              |
|-----------------------|--------------------------------------------------------|
| Nomes de arquivos     | `snake_case.py`                                        |
| Classes               | `PascalCase`                                           |
| Funções / variáveis   | `snake_case`                                           |
| Constantes            | `UPPER_SNAKE_CASE` (em `settings.py`)                  |
| Funções internas      | prefixo `_` (ex: `_build_map`, `_draw_bg`)             |
| IDs de NPC (diálogo)  | `snake_case` correspondendo à chave em `DIALOGUE_DATA` |
| IDs de tile           | inteiros sequenciais registrados em `TILE_GENERATORS`  |
| Coordenadas           | `(x, y)` em pixels no espaço de mundo; câmera converte |
| Superfícies de render | sempre na resolução interna 640×360                    |

---

## Checklist para novo conteúdo

- [ ] Nova cena: registrar ID em `settings.py`, criar arquivo em `scenes/`, disparar transição
- [ ] Novo inimigo: herdar de `Enemy`, implementar `update()` e `draw()`, adicionar à cena
- [ ] Novo NPC: herdar de `NPC` ou implementar interface mínima, registrar diálogo
- [ ] Novo diálogo: adicionar entrada em `DIALOGUE_DATA`, chamar `dialogue.open()`
- [ ] Novo tile: criar função geradora, registrar ID, marcar como sólido se necessário
- [ ] Novo karma: adicionar método em `KarmaSystem`, chamar na cena, revisar `final_type`
