# Arquitetura — A Pedra dos Ancestrais

## Visão geral

O jogo é uma aplicação Python single-process, sem rede e sem banco de dados.
Todo o estado vive em memória durante a sessão; não existe sistema de save ainda.

---

## Diagrama de módulos

```
main.py
  └── Game (core/game.py)
        ├── SceneManager (core/scene_manager.py)  ← pilha de cenas
        ├── KarmaSystem  (systems/karma.py)        ← estado global persistente entre cenas
        └── [cena atual]
              ├── Player        (entities/player.py)
              ├── NPC / Enemy   (entities/*.py)
              ├── Tilemap       (systems/tilemap.py)
              ├── Camera        (core/camera.py)
              ├── DialogueBox   (systems/dialogue.py)
              ├── HUD           (systems/hud.py)
              └── ParticleSystem / ScreenEffects  (art/fx.py)
```

---

## Loop principal (Game.run)

```
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

  4. clock.tick(60)                      ← cap de 60 FPS
```

---

## Ciclo de vida de uma cena

O `SceneManager` usa uma **pilha**. Cada cena implementa:

| Método          | Quando é chamado                          |
|-----------------|-------------------------------------------|
| `on_enter()`    | Cena chega ao topo da pilha               |
| `on_exit()`     | Cena é removida da pilha                  |
| `on_resume()`   | Cena volta ao topo após pop de outra      |
| `handle_event(event)` | A cada evento pygame                |
| `update()`      | A cada frame (lógica)                     |
| `draw(surf)`    | A cada frame (render na superfície 640×360) |

### Transições

```python
scene_manager.push(nova_cena)     # empilha (pausa a atual)
scene_manager.pop()               # remove a cena do topo
scene_manager.replace(nova_cena)  # substitui (troca de ato)
```

A mudança só é efetivada em `apply_pending()`, sempre no início do próximo frame,
evitando modificar a pilha durante a iteração do loop.

---

## Sistema de karma

`KarmaSystem` é instanciado em `Game.__init__` e repassado para cada cena.
Ele acumula três atributos discretos (0–5) e um flag binário:

| Atributo         | Tipo    | Incrementado por                     |
|------------------|---------|--------------------------------------|
| `coragem`        | int 0–5 | ajudou espírito, enfrentou inimigo   |
| `ganancia`       | int 0–5 | pegou item armadilha, quebrou pote   |
| `sabedoria`      | int 0–5 | leu registro, conversou com NPC      |
| `divida_iracema` | bool/None | resultado do trato com Iracema     |

A propriedade `final_type` calcula o final (`"ruim"` / `"neutro"` / `"verdadeiro"`)
com base nos valores acumulados ao longo de todos os atos.

---

## Pipeline de render

```
┌─────────────────────────────────────────────┐
│  Surface interna: 640 × 360 px              │
│                                             │
│  1. Parallax BG (camadas 0–4)               │
│  2. Tilemap (culling automático)            │
│  3. Entities (NPCs, inimigos, player)       │
│  4. ParticleSystem                          │
│  5. ScreenEffects (flash, fade, vignette)   │
│  6. HUD (corações, prompt)                  │
│  7. DialogueBox (sobre o HUD)               │
└────────────────┬────────────────────────────┘
                 │  pygame.transform.scale(×2)
                 ▼
┌─────────────────────────────────────────────┐
│  Janela: 1280 × 720 px                      │
└─────────────────────────────────────────────┘
```

---

## Física do player

Todos os valores estão em `settings.py`.

| Constante          | Valor | Descrição                           |
|--------------------|-------|-------------------------------------|
| `PLAYER_SPEED`     | 2.5   | Velocidade horizontal (px/frame)    |
| `PLAYER_JUMP_FORCE`| −8.0  | Impulso vertical do pulo            |
| `PLAYER_GRAVITY`   | 0.4   | Aceleração gravitacional por frame  |
| `PLAYER_MAX_FALL`  | 10.0  | Velocidade máxima de queda          |
| `COYOTE_FRAMES`    | 8     | Frames de graça após sair da borda  |
| `JUMP_BUFFER_FRAMES`| 6    | Frames de buffer de pulo antecipado |

**Resolução de colisão AABB:** move X → resolve X → move Y → resolve Y.
Essa ordem garante que colisões de canto se resolvam previsível.

---

## Arte procedural

Nenhum arquivo de imagem externo é carregado. Tudo é gerado em código:

| Módulo          | Responsabilidade                                  |
|-----------------|---------------------------------------------------|
| `art/sprites.py`| Frames de Caio, NPCs, inimigos, ícone da janela   |
| `art/tiles.py`  | Tiles 16×16 com cache (`_tile_cache`)             |
| `art/palette.py`| Paletas nomeadas (sertão e caverna)               |
| `art/fx.py`     | `Particle`, `ParticleSystem`, `ScreenEffects`     |

O cache de tiles (`_tile_cache` em `tiles.py`) garante que cada tile ID seja
gerado apenas uma vez por sessão.

---

## IDs de tiles

| ID | Tile             | Sólido |
|----|------------------|--------|
| 0  | Ar (vazio)       | Não    |
| 1  | Pedra topo       | Sim    |
| 2  | Pedra meio       | Sim    |
| 3  | Pedra base       | Sim    |
| 4  | Terra            | Sim    |
| 5  | Cacto base       | Não    |
| 6  | Cacto topo       | Não    |
| 7  | Trepadeira       | Não    |
| 8  | Pedra castelo    | Sim    |
| 9  | Rocha caverna    | Sim    |
| 10 | Rocha brilhante  | Sim    |
| 11 | Cristal          | Sim    |
| 12 | Água             | Não    |
| 13 | Grama seca       | Não    |
| 14 | Pote             | Não    |
| 15 | Caixote          | Sim    |

---

## Dependências entre módulos

```
settings.py ◀── todos os módulos (sem dependência circular)

core/game.py
  ├── core/scene_manager.py
  ├── systems/karma.py
  └── scenes/intro_scene.py (importação lazy)

scenes/*.py
  ├── core/camera.py
  ├── core/scene_manager.py
  ├── systems/{tilemap, dialogue, hud, karma}.py
  ├── entities/{player, npc, enemy, bat_enemy, guardian_statue}.py
  └── art/{sprites, fx}.py

entities/*.py
  ├── art/sprites.py
  └── art/fx.py

systems/tilemap.py
  └── art/tiles.py

art/*.py
  └── settings.py (paletas, TILE_SIZE)
```

Regra de ouro: **`settings.py` não importa nada do projeto**. Ele é a folha
mais baixa da árvore de dependências.
