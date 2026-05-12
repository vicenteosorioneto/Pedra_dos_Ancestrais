# A Pedra dos Ancestrais

Jogo 2D de plataforma narrativo com elementos leves de RPG, ambientado no sertao nordestino brasileiro. O jogador controla Caio, um jovem guiado pelo vento ate a misteriosa Pedra dos Ancestrais, onde exploracao, combate, memoria e escolhas definem o fim da jornada.

## Visao Geral

- **Genero:** plataforma 2D narrativo com RPG leve
- **Plataforma:** PC Windows
- **Tecnologia:** Python + Pygame
- **Entrega:** executavel `.exe` gerado com PyInstaller
- **Resolucao interna do jogo:** 640 x 360
- **Tela final:** fullscreen 1920 x 1080
- **Escala do mundo:** pixel art ampliada em 3x
- **Interface:** HUD, dialogos, menu, mensagens, game over e escolhas renderizados em Full HD
- **Arte:** pixel art procedural gerada em codigo
- **Audio:** trilhas e efeitos proceduralmente gerados em codigo
- **Progressao:** menu principal -> fases -> caverna final -> escolha -> um de tres finais

## Executavel

O jogo ja foi buildado como produto fechado.

Arquivo final:

```text
dist/PedraDosAncestrais.exe
```

Esse arquivo roda fora do editor e nao depende de abrir o projeto Python manualmente.

## Checklist de Entrega P2

| Requisito | Implementacao |
| --- | --- |
| Produto fechado | Build Windows em `dist/PedraDosAncestrais.exe` |
| Tela de titulo | Menu principal com `Jogar`, `Creditos`, `Controles`, `Opcoes` e `Sair` |
| Creditos | Tela propria de creditos no menu |
| Gameplay | Fases jogaveis com plataforma, exploracao, combate, coleta, dialogos e objetivos |
| Game Over | Ao zerar vida, aparece tela de morte com `Tentar de novo`, menu e controles |
| Reinicio controlado | `Tentar de novo` reinicia a fase sem fechar o jogo |
| Vitoria/progressao | Objetivos completos levam a proxima fase; o final permite jogar novamente |
| Tres finais | No Ato 3, a decisao final da Pedra leva a memoria, tesouro ou silencio |
| Dificuldade crescente | Exploracao inicial, desafios/altares/registros, caverna com guardiao e decisao final |
| Derrota ativa | Inimigos e guardiao causam dano; vida zerada bloqueia gameplay e abre Game Over |
| HUD funcional | Vida por coracoes, objetivos, contadores, mensagens e feedback visual |
| Originalidade | Mecanicas, sistemas, arte procedural e audio procedural implementados em Python/Pygame |

## Estrutura de Jogo

### Menu Principal

O jogo inicia em uma tela de titulo em Full HD com:

- `Jogar`
- `Creditos`
- `Controles`
- `Opcoes`
- `Sair`

### Atos e Fases

| Ato/Fase | Funcao no jogo |
| --- | --- |
| Vila | Apresenta NPCs, coleta, desafio simples e objetivos |
| Floresta | Introduz exploracao com registros, recompensas e inimigos |
| Ruinas | Reforca leitura, selo ancestral e desafio de simbolos |
| Trilha | Testa altares, registros, inimigos e abertura de passagem |
| Caverna | Climax com registros finais, guardiao, Iracema e escolha final |
| Final | Mostra um dos tres finais e o resumo do que o jogador fez |

### Tres Finais

No Ato 3, depois de derrotar o Guardiao e encontrar Iracema, a Pedra apresenta uma decisao final:

| Escolha | Resultado |
| --- | --- |
| Carregar as memorias | Final verdadeiro |
| Tomar o tesouro | Final ruim |
| Partir em silencio | Final neutro |

O final tambem reconhece elementos da jornada, como conversas, inscricoes, altares, recompensas, guardiao e escolha de Iracema.

## Resolucao e Renderizacao

O projeto usa duas camadas visuais:

1. **Mundo em pixel art:** desenhado em 640 x 360 e ampliado para 1920 x 1080.
2. **Interface HD:** textos, HUD, dialogos, menu e mensagens desenhados diretamente em Full HD.

Pipeline:

```text
Mundo do jogo: 640 x 360
        |
        v
Upscale pixel art 3x
        |
        v
Fullscreen 1920 x 1080
        |
        v
Camada HD de interface por cima
```

Isso preserva o estilo pixel art sem deixar frases e HUD borrados.

Configuracao principal:

```text
config/display.py
```

Valores atuais:

```python
SCREEN_W = 640
SCREEN_H = 360
WINDOW_W = 1920
WINDOW_H = 1080
SCALE = 3
FULLSCREEN = True
HD_UI = True
```

## Controles

| Tecla | Acao |
| --- | --- |
| `A` / seta esquerda | Mover para a esquerda |
| `D` / seta direita | Mover para a direita |
| `W` / seta cima / `Espaco` | Pular |
| `Z` ou `J` | Atacar |
| `X` ou `K` | Interagir / confirmar dialogo |
| `ENTER` | Confirmar / tentar novamente |
| `ESC` | Pausar / voltar / menu |
| `M` | Voltar ao menu quando pausado |
| `Alt + F4` | Fechar |

## HUD e Interface

Durante a gameplay, a tela mostra:

- Vida do jogador por coracoes
- Lista de objetivos da fase
- Contadores de progresso, como conversas, registros, altares e recompensas
- Nome do ato/fase
- Prompt de interacao
- Mensagens de sistema
- Feedback visual ao tomar dano ou coletar recompensas

A HUD antiga em pixel art foi mantida no codigo, mas a versao ativa usa `systems/hd_ui.py`, renderizada diretamente em 1920 x 1080 para maior legibilidade.

## Como Rodar pelo Codigo

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependencias:

```bash
python -m pip install -r requirements.txt
```

Execute:

```bash
python main.py
```

## Como Gerar o .exe

Com o ambiente virtual ativo:

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name PedraDosAncestrais --add-data="content:content" main.py
```

Saida:

```text
dist/PedraDosAncestrais.exe
```

Antes de rebuildar, feche qualquer instancia aberta do jogo, porque o Windows pode bloquear a substituicao do `.exe`.

## Testes

Execute:

```bash
python -m pytest tests/ -v
```

Resultado validado na versao final:

```text
56 passed
```

Os testes cobrem sistemas centrais como karma, finais, event bus, dialogos e estados do jogador.

## Mecânicas e Sistemas

| Sistema | Arquivo principal |
| --- | --- |
| Loop principal e render final | `core/game.py` |
| Configuracao de tela/fullscreen | `config/display.py` |
| Menu principal | `scenes/intro_scene.py` |
| Movimento do jogador | `gameplay/player/player.py` |
| Estados do jogador | `gameplay/player/states.py` |
| Fisica e pulo | `config/physics.py` |
| Colisao por tiles | `systems/tilemap.py` |
| HUD e UI Full HD | `systems/hd_ui.py` |
| HUD legado/pixel art | `systems/hud.py` |
| Dialogos | `systems/dialogue.py` e `systems/dialogue_loader.py` |
| Dados de dialogo | `content/dialogue/npcs.json` |
| Sistema de karma/finais | `systems/karma.py` |
| Audio procedural | `systems/audio.py` |
| Recompensas | `systems/rewards.py` |
| Minigames | `systems/minigames.py` |
| Efeitos visuais | `art/fx.py` |

## Estrutura do Projeto

```text
pedra_dos_ancestrais/
|
|-- main.py
|-- requirements.txt
|-- settings.py
|
|-- config/
|   |-- display.py
|   |-- physics.py
|   |-- palette.py
|   `-- scene_ids.py
|
|-- core/
|   |-- game.py
|   |-- scene_manager.py
|   |-- camera.py
|   |-- event_bus.py
|   `-- input_manager.py
|
|-- scenes/
|   |-- intro_scene.py
|   |-- village_scene.py
|   |-- forest_scene.py
|   |-- ruins_scene.py
|   |-- trail_scene.py
|   |-- cave_scene.py
|   `-- ending_scene.py
|
|-- gameplay/
|   |-- player/
|   |-- enemies/
|   `-- npcs/
|
|-- entities/
|-- systems/
|-- art/
|-- content/
|-- shared/
|-- docs/
`-- tests/
```

## Observacoes de Entrega

- O jogo nao comeca direto na fase.
- O jogo nao fecha ao morrer.
- O jogo possui tela de titulo, game over, progressao e finais.
- O `.exe` em `dist/` e o build final devem ser entregues para avaliacao.
- `build/`, `dist/` e arquivos `.spec` sao ignorados pelo git por serem artefatos locais de build.
- O arquivo `settings.py` existe como compatibilidade para imports antigos; configuracoes novas ficam em `config/`.
