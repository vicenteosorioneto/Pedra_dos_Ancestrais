# Arquitetura — A Pedra dos Ancestrais

## Estrutura de pastas

```text
pedra_dos_ancestrais/
│
├── main.py                        # Bootstrap: cria Game e chama run()
│
├── config/                        # Constantes agrupadas por domínio
│   ├── display.py                 # SCREEN_W, WINDOW_W, FPS, TITLE, SCALE
│   ├── physics.py                 # PLAYER_SPEED, GRAVITY, COYOTE_FRAMES...
│   ├── palette.py                 # PALETTE_SERTAO, PALETTE_CAVE, BLACK, GOLD
│   └── scene_ids.py               # SCENE_INTRO, SCENE_VILLAGE, SCENE_TRAIL...
│
├── shared/                        # Tipos e utilitários sem dependência de jogo
│   ├── enums.py                   # SceneID, PlayerState, TileID, GameEvent
│   └── utils.py                   # clamp, lerp, load_json, get_logger
│
├── core/                          # Motor do jogo
│   ├── game.py                    # Loop principal, upscale, injeção de serviços
│   ├── scene_manager.py           # Pilha de cenas (push/pop/replace)
│   ├── camera.py                  # Câmera com lerp e parallax
│   ├── event_bus.py               # Pub/sub desacoplado entre sistemas
│   └── input_manager.py           # InputState + mapeamento ação → tecla
│
├── scenes/                        # Cenas / atos do jogo
│   ├── base_scene.py              # Contrato base (on_enter, update, draw...)
│   ├── intro_scene.py             # Tela de título
│   ├── village_scene.py           # Ato 1 — Vila do sertão
│   ├── trail_scene.py             # Ato 2 — Trilha noturna
│   └── cave_scene.py              # Ato 3 — Caverna / boss
│
├── gameplay/                      # Lógica de jogo (sem pygame.K_* direto)
│   ├── player/
│   │   ├── player.py              # Player: física, animação, events via bus
│   │   └── states.py              # PlayerState enum + tabela de transições
│   ├── enemies/
│   │   ├── base_enemy.py          # Enemy: física, colisão, take_damage
│   │   ├── bat_enemy.py           # Morcego corrompido
│   │   └── guardian_statue.py     # Mini-boss
│   └── npcs/
│       └── npc.py                 # NPC, VillagerNPC, ElderNPC
│
├── systems/                       # Subsistemas reutilizáveis
│   ├── karma.py                   # KarmaSystem + KarmaSummary + EventBus
│   ├── dialogue.py                # DialogueBox + SystemMessage
│   ├── dialogue_loader.py         # Carrega content/dialogue/*.json
│   ├── hud.py                     # HUD (corações, interação, partículas)
│   └── tilemap.py                 # Tilemap (colisão + render)
│
├── art/                           # Arte procedural (sem lógica de jogo)
│   ├── sprites.py                 # Sprites gerados em código
│   ├── tiles.py                   # Tiles 16×16 com cache
│   ├── palette.py                 # Re-exporta paletas de config/
│   └── fx.py                      # Particle, ParticleSystem, ScreenEffects
│
├── content/                       # Dados puros — zero Python de lógica
│   └── dialogue/
│       └── npcs.json              # Todos os diálogos dos NPCs
│
├── entities/                      # SHIMS — re-exportam de gameplay/
│   ├── player.py                  # → gameplay/player/player.py
│   ├── enemy.py                   # → gameplay/enemies/base_enemy.py
│   ├── bat_enemy.py               # → gameplay/enemies/bat_enemy.py
│   ├── guardian_statue.py         # → gameplay/enemies/guardian_statue.py
│   └── npc.py                     # → gameplay/npcs/npc.py
│
├── settings.py                    # SHIM — re-exporta de config/
│
├── tests/
│   ├── test_karma.py
│   ├── test_player_states.py
│   ├── test_event_bus.py
│   └── test_dialogue_loader.py
│
└── docs/
    ├── ARCHITECTURE.md
    └── HOW_TO_EXTEND.md
```

---

## Diagrama de dependências

```text
settings.py (shim) ◀── código legado
config/            ◀── todos os módulos (raiz — não importa nada do projeto)
shared/            ◀── importa apenas config/

art/               ◀── config/, shared/
core/              ◀── config/, shared/
systems/           ◀── config/, shared/, art/, core/
gameplay/          ◀── config/, shared/, art/, systems/
scenes/            ◀── tudo acima (camada de composição)
main.py            ◀── core/, scenes/
```

**Regra de ouro:** dependências só descem. `core/` nunca conhece `gameplay/`. `systems/` nunca conhece `scenes/`.

---

## Loop principal (Game.run)

```text
while running:
  1. _handle_events()
     ├── pygame.event.get()
     ├── scene.handle_event(event)
     └── scene_manager.apply_pending()   ← aplica troca de cena do frame anterior

  2. _update()
     ├── scene.update()
     └── scene_manager.apply_pending()

  3. _draw()
     ├── screen.fill(black)              ← limpa superfície 640×360
     ├── scene.draw(screen)
     └── window.blit(scale(screen, 2×)) ← upscale para 1280×720

  4. clock.tick(60)
```

---

## Serviços injetados nas cenas

`Game.__init__` cria os serviços uma vez. Cada cena recebe todos eles no construtor:

| Serviço        | Tipo            | Responsabilidade                       |
| -------------- | --------------- | -------------------------------------- |
| `scene_manager`| `SceneManager`  | Push/pop/replace de cenas              |
| `bus`          | `EventBus`      | Pub/sub desacoplado                    |
| `karma`        | `KarmaSystem`   | Karma global entre cenas               |
| `input_manager`| `InputManager`  | Poll de InputState sem pygame.K_*      |

Cenas passam `bus` e `input_manager` para entidades que precisam deles.

---

## Event Bus — fluxo de comunicação

```text
Player.take_damage()
  └── bus.publish("player_damaged", hp=2, x=100, y=200)
        ├── HUD._on_player_damaged()       → quebra coração
        ├── KarmaSystem._on_enemy_killed() → (se inimigo morreu)
        └── [futuros subscribers]          → sons, achievements, etc.
```

Eventos definidos em `shared/enums.py → GameEvent`.

---

## Ciclo de vida de uma cena

| Método                | Quando é chamado                              |
| --------------------- | --------------------------------------------- |
| `on_enter()`          | Cena chega ao topo da pilha                   |
| `on_exit()`           | Cena é removida da pilha                      |
| `on_resume()`         | Cena volta ao topo após pop de outra          |
| `handle_event(event)` | A cada evento pygame                          |
| `update()`            | A cada frame (lógica)                         |
| `draw(surf)`          | A cada frame (render na superfície 640×360)   |

---

## InputState — fluxo de input

```text
pygame.key.get_pressed()        (apenas no InputManager)
  └── InputManager.poll()
        └── InputState(move_left, move_right, jump, attack, interact, pause)
              └── player.handle_input(inp)   (sem pygame.K_* direto)
```

Para remapear: editar `DEFAULT_BINDINGS` em `core/input_manager.py`.

---

## PlayerState — máquina de estados

Estados definidos em `shared/enums.py`. Transições válidas em `gameplay/player/states.py`:

```text
IDLE ──────┬──▶ WALKING
           ├──▶ JUMPING
           ├──▶ FALLING
           ├──▶ ATTACKING
           ├──▶ HURT
           └──▶ DEAD (terminal)

DEAD — sem saída
```

`Player._set_state(new)` valida a transição antes de aplicar. Typos em strings de estado são impossíveis.

---

## Pipeline de render

```text
640×360 (surface interna)
  1. Background / parallax
  2. Tilemap (culling automático)
  3. NPCs, inimigos
  4. Player
  5. ParticleSystem
  6. ScreenEffects (flash, fade, vignette)
  7. HUD
  8. DialogueBox
       │
       ▼  pygame.transform.scale(×2)
1280×720 (janela)
```

---

## IDs de tiles

Definidos em `shared/enums.py → TileID`. Os sólidos estão em `SOLID_TILE_IDS`:

| ID    | Nome                       | Sólido |
| ----- | -------------------------- | ------ |
| 0     | AIR                        | Não    |
| 1     | PEDRA_TOPO                 | Sim    |
| 2     | PEDRA_MEIO                 | Sim    |
| 3     | PEDRA_BASE                 | Sim    |
| 4     | TERRA                      | Sim    |
| 5–7   | CACTO, TREPADEIRA          | Não    |
| 8     | PEDRA_CASTELO              | Sim    |
| 9–11  | ROCHA_CAVE, GLOW, CRISTAL  | Sim    |
| 12–14 | AGUA, GRAMA, POTE          | Não    |
| 15    | CAIXOTE                    | Sim    |
