# A Pedra dos Ancestrais

Jogo 2D de plataforma com elementos leves de RPG, ambientado no sertão nordestino brasileiro. O jogador controla Caio, um jovem guiado pelo vento até a misteriosa Pedra dos Ancestrais, onde escolhas silenciosas moldam o final da jornada.

## Visão Geral

- **Gênero:** plataforma 2D narrativo com RPG leve
- **Plataforma:** PC, via Python e Pygame
- **Resolução interna:** 640 x 360
- **Janela:** 1280 x 720, com upscale 2x
- **Arte:** pixel art procedural gerada em código
- **Progressão:** atos, exploração, combate simples, diálogos e sistema de karma invisível

## Requisitos

- Python 3.9 ou superior
- Git
- Pygame 2.1 ou superior

As dependências do projeto estão em `requirements.txt`.

## Como Rodar

Clone o repositório:

```bash
git clone https://github.com/vicenteosorioneto/pedra_dos_ancestrais.git
cd pedra_dos_ancestrais
```

Crie e ative um ambiente virtual:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute o jogo:

```bash
python main.py
```

Uma janela 1280 x 720 será aberta com a tela de título. Pressione uma tecla para começar.

## Início Rápido

```bash
git clone https://github.com/vicenteosorioneto/pedra_dos_ancestrais.git
cd pedra_dos_ancestrais
python -m pip install -r requirements.txt
python main.py
```

No PowerShell, evite executar `pip install pygame>=2.1.0` sem aspas, porque o caractere `>` pode ser interpretado como redirecionamento. Se quiser instalar diretamente, use:

```bash
python -m pip install "pygame>=2.1.0"
```

## Controles

| Tecla | Ação |
| --- | --- |
| `A` / `←` | Mover para a esquerda |
| `D` / `→` | Mover para a direita |
| `W` / `↑` / `Espaço` | Pular |
| `Z` ou `J` | Atacar |
| `X` ou `K` | Interagir |
| `ESC` | Pausar |
| `Alt + F4` | Fechar |

## Mecânicas

| Mecânica | Onde fica |
| --- | --- |
| Movimento do jogador | `gameplay/player/player.py` |
| Estados do jogador | `gameplay/player/states.py` |
| Coyote time e jump buffer | `config/physics.py` |
| Colisão por tiles | `systems/tilemap.py` |
| Sistema de karma | `systems/karma.py` |
| Diálogos | `systems/dialogue.py` e `systems/dialogue_loader.py` |
| Dados de diálogo | `content/dialogue/npcs.json` |
| HUD | `systems/hud.py` |
| Efeitos visuais | `art/fx.py` |

## Estrutura do Projeto

```text
pedra_dos_ancestrais/
|
|-- main.py                  # Ponto de entrada
|-- requirements.txt         # Dependências
|-- settings.py              # Shim de compatibilidade para configurações antigas
|
|-- config/                  # Constantes por domínio
|   |-- display.py           # Tela, escala, FPS e título
|   |-- physics.py           # Física, pulo, gravidade e tiles
|   |-- palette.py           # Paletas globais
|   `-- scene_ids.py         # IDs das cenas
|
|-- core/                    # Motor do jogo
|   |-- game.py              # Loop principal e render final
|   |-- scene_manager.py     # Pilha de cenas
|   |-- camera.py            # Câmera
|   |-- event_bus.py         # Comunicação por eventos
|   `-- input_manager.py     # Abstração de input
|
|-- scenes/                  # Cenas e atos
|   |-- intro_scene.py       # Tela de título
|   |-- village_scene.py     # Vila
|   |-- trail_scene.py       # Trilha
|   |-- cave_scene.py        # Caverna
|   |-- forest_scene.py      # Floresta
|   |-- ruins_scene.py       # Ruínas
|   `-- ending_scene.py      # Final
|
|-- gameplay/                # Lógica de jogo refatorada
|   |-- player/              # Player e estados
|   |-- enemies/             # Inimigos e chefe
|   `-- npcs/                # NPCs
|
|-- entities/                # Shims legados para compatibilidade
|-- systems/                 # Karma, diálogo, HUD e tilemap
|-- art/                     # Sprites, tiles, paletas e efeitos procedurais
|-- content/                 # Dados puros, como diálogos em JSON
|-- shared/                  # Enums e utilitários compartilhados
|-- docs/                    # Documentação técnica e design
`-- tests/                   # Testes automatizados
```

## Pipeline de Render

```text
Superfície interna 640 x 360
        |
        v
Upscale 2x
        |
        v
Janela 1280 x 720
```

Todos os sistemas desenham na superfície interna. No fim de cada frame, `core/game.py` amplia a imagem para a janela final.

## Testes

Execute:

```bash
pytest tests/ -v
```

Os testes cobrem partes centrais como karma, event bus, carregamento de diálogos e estados do jogador. Eles não dependem de uma janela gráfica aberta.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Como estender o jogo](docs/HOW_TO_EXTEND.md)
- [Game Design Document](docs/GDD.md)

## Observações

O arquivo `settings.py` existe para manter compatibilidade com imports antigos. Para código novo, prefira importar diretamente dos módulos em `config/`.
