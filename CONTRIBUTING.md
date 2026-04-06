# Guia de contribuição

## Ambiente de desenvolvimento

```bash
# Clonar e instalar
pip install pygame>=2.1.0

# Rodar
python main.py
```

Não há dependências de desenvolvimento além do Pygame. Sem linters ou
formatadores obrigatórios por enquanto — siga as convenções abaixo manualmente.

---

## Convenções de código

### Nomenclatura

| Elemento              | Estilo            | Exemplo                        |
|-----------------------|-------------------|--------------------------------|
| Módulos / arquivos    | `snake_case`      | `bat_enemy.py`                 |
| Classes               | `PascalCase`      | `BatEnemy`, `SceneManager`     |
| Funções e métodos     | `snake_case`      | `apply_gravity()`, `on_enter()`|
| Variáveis             | `snake_case`      | `player_hp`, `tile_id`         |
| Constantes globais    | `UPPER_SNAKE_CASE`| `PLAYER_SPEED`, `TILE_SIZE`    |
| Funções privadas      | `_snake_case`     | `_build_map()`, `_draw_bg()`   |
| Chaves de diálogo     | `snake_case`      | `"zequinha"`, `"aldeao_1"`     |

### Organização de imports

```python
# 1. Stdlib
import math
import random

# 2. Pygame
import pygame

# 3. Projeto (settings primeiro, depois por camada)
from settings import SCREEN_W, TILE_SIZE
from core.camera import Camera
from systems.tilemap import Tilemap
from entities.player import Player
from art.fx import ParticleSystem
```

### Comentários

- Cabeçalho de arquivo: `# caminho/arquivo.py — descrição curta`
- Seções dentro do arquivo: `# ── Nome da seção ──────────────────────`
- Inline apenas onde a lógica não é óbvia
- Sem docstrings em funções simples; use docstring apenas em métodos públicos
  não triviais

---

## Estrutura de uma cena

Toda cena deve implementar a interface mínima:

```python
class MinhaScene:
    def __init__(self, scene_manager, karma):
        ...

    def on_enter(self):   ...   # inicializar / carregar
    def on_exit(self):    ...   # liberar recursos
    def on_resume(self):  ...   # ao voltar ao topo

    def handle_event(self, event): ...
    def update(self):             ...
    def draw(self, surf):         ...
```

Não use `super().__init__()` de uma classe base de cena — o protocolo é
por duck typing (interface implícita), não herança.

---

## Estrutura de um inimigo

Herdar sempre de `Enemy` (`entities/enemy.py`):

```python
class MeuInimigo(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, w=12, h=28)
        self.hp = 3
        self.damage = 1

    def update(self, tilemap, player_rect=None): ...
    def draw(self, surf, cam_x, cam_y):          ...
```

`Enemy` já fornece: `rect`, `center`, `take_damage()`, `apply_gravity()`,
`collide_tilemap()`, flag `alive`.

---

## Onde cada tipo de mudança vai

| Mudança                        | Arquivo(s) a modificar                         |
|--------------------------------|------------------------------------------------|
| Nova cena                      | `settings.py` + novo arquivo em `scenes/`      |
| Novo inimigo                   | Novo arquivo em `entities/` + cena que usa     |
| Novo NPC                       | `entities/npc.py` + `systems/dialogue.py`      |
| Novo diálogo                   | `systems/dialogue.py` → `DIALOGUE_DATA`        |
| Novo tile                      | `art/tiles.py` → `TILE_GENERATORS` + mapa      |
| Ajuste de física               | `settings.py`                                  |
| Nova paleta de cores           | `settings.py` + `art/palette.py`               |
| Novo efeito de partícula       | `art/fx.py` → `ParticleSystem`                 |
| Novo efeito de tela            | `art/fx.py` → `ScreenEffects`                  |
| Novo evento de karma           | `systems/karma.py`                             |

---

## O que não fazer

- **Não colocar constantes numéricas literais nas cenas.** Use ou crie
  constantes em `settings.py`.
- **Não importar `settings` de dentro de `art/palette.py` criando dependência
  circular.** `settings.py` é a raiz — ele não importa nada do projeto.
- **Não renderizar na resolução 1280×720.** Todo render vai na superfície
  640×360 recebida por `draw(surf)`. O upscale é feito automaticamente por
  `Game._draw()`.
- **Não modificar a pilha do `SceneManager` durante `update()` ou `draw()`.
  Use `scene_manager.replace()` / `push()` / `pop()` — a mudança será
  aplicada no próximo frame via `apply_pending()`.

---

## Adicionando conteúdo — referência rápida

Ver [docs/HOW_TO_EXTEND.md](docs/HOW_TO_EXTEND.md) para guias passo a passo
de cada tipo de extensão com exemplos de código completos.
