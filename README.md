# A Pedra dos Ancestrais

Jogo 2D de plataforma com RPG leve ambientado no **sertão nordestino brasileiro**.
O jogador controla Caio, guiado pelo vento até a misteriosa Pedra dos Ancestrais.

---

## Como clonar e rodar

### Requisitos

- [Python 3.9+](https://www.python.org/downloads/) instalado e no PATH
- Git instalado (`git --version` para confirmar)
- Nenhuma outra dependência além do Pygame

### Passo a passo

**1. Clone o repositório**

```bash
git clone https://github.com/vicenteosorioneto/pedra_dos_ancestrais.git
cd pedra_dos_ancestrais
```

**2. Crie e ative um ambiente virtual** *(recomendado)*

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instale as dependências**

```bash
pip install pygame>=2.1.0
```

**4. Rode o jogo**

```bash
python main.py
```

Uma janela 1280×720 vai abrir com a tela de título. Pressione qualquer tecla para começar.

### Rodando os testes

```bash
pytest tests/ -v
```

Todos os 55 testes devem passar. Nenhum deles abre janela ou depende do Pygame instalado com display.

---

## Início rápido

```bash
# Versão resumida para quem já tem Python e Git
git clone https://github.com/vicenteosorioneto/pedra_dos_ancestrais.git
cd pedra_dos_ancestrais
pip install pygame>=2.1.0
python main.py
```

**Requisitos:** Python 3.9+ · Pygame 2.1+

---

## Controles

| Tecla              | Ação       |
|--------------------|------------|
| `A` / `←`          | Mover esquerda |
| `D` / `→`          | Mover direita  |
| `W` / `↑` / `Espaço` | Pular       |
| `Z` ou `J`         | Atacar     |
| `X` ou `K`         | Interagir  |
| `ESC`              | Pausar     |
| `Alt + F4`         | Fechar     |

---

## Estrutura do projeto

```
pedra_dos_ancestrais/
│
├── main.py              # Ponto de entrada
├── settings.py          # Constantes globais (resolução, física, paletas, IDs)
├── requirements.txt
│
├── core/                # Motor do jogo
│   ├── game.py          # Loop principal, inicialização, upscale
│   ├── scene_manager.py # Pilha de cenas (push / pop / replace)
│   └── camera.py        # Câmera com lerp e parallax
│
├── scenes/              # Cenas / atos do jogo
│   ├── intro_scene.py   # Tela de título
│   ├── village_scene.py # Ato 1 — Vila do sertão
│   ├── trail_scene.py   # Ato 2 — Trilha noturna
│   └── cave_scene.py    # Ato 3 — Caverna / boss
│
├── entities/            # Objetos do mundo
│   ├── player.py        # Caio (protagonista)
│   ├── npc.py           # NPCs com patrulha e diálogo
│   ├── enemy.py         # Classe base de inimigo
│   ├── bat_enemy.py     # Morcego corrompido
│   └── guardian_statue.py # Mini-boss — Guardião Estátua
│
├── systems/             # Subsistemas reutilizáveis
│   ├── karma.py         # Karma silencioso (coragem / ganância / sabedoria)
│   ├── dialogue.py      # Caixa de diálogo com efeito typewriter
│   ├── hud.py           # HUD (corações, prompt de interação, partículas)
│   └── tilemap.py       # Renderização e colisão por tiles
│
├── art/                 # Pipeline de arte procedural
│   ├── sprites.py       # Sprites gerados em código (Caio, NPCs, inimigos)
│   ├── tiles.py         # Tiles 16×16 com cache
│   ├── palette.py       # Paletas de cores nomeadas
│   └── fx.py            # Partículas, efeitos de tela, iluminação
│
└── docs/                # Documentação técnica
    ├── ARCHITECTURE.md  # Arquitetura, fluxo de dados, ciclo de vida
    └── HOW_TO_EXTEND.md # Como adicionar cenas, entidades, tiles, diálogos
```

---

## Mecânicas principais

| Mecânica          | Arquivo fonte                |
|-------------------|------------------------------|
| Física / pulo     | `entities/player.py`         |
| Coyote time       | `settings.py` → `COYOTE_FRAMES` |
| Colisão AABB      | `systems/tilemap.py`         |
| Sistema de karma  | `systems/karma.py`           |
| Diálogos          | `systems/dialogue.py` → `DIALOGUE_DATA` |
| Efeitos visuais   | `art/fx.py`                  |

---

## Pipeline de render

```
640×360 (interna) ──upscale 2×──▶ 1280×720 (janela)
```

Todos os sistemas renderizam na superfície interna. O `Game._draw()` faz o
upscale ao final de cada frame.

---

## Documentação completa

- [Arquitetura](docs/ARCHITECTURE.md)
- [Como estender o jogo](docs/HOW_TO_EXTEND.md)
