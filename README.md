# A Pedra dos Ancestrais

Jogo 2D de plataforma narrativo, ambientado no sertao piauiense e inspirado na Pedra do Castelo, em Castelo do Piaui. O jogador controla Caio, um jovem chamado por uma pedra misteriosa ligada a memoria de sua familia e de seus antepassados.

Durante a jornada, Caio explora vila, floresta, ruinas, trilha e caverna, conversa com personagens, le inscricoes, ativa altares, enfrenta inimigos e toma uma decisao final que leva a um de tres finais.

## Equipe

Desenvolvido por:

- Guilherme de Abreu
- Antonio Vicente
- Joao Emannuel
- Victor Gabriel
- Joao Victor Melo

## Pitch

**A Pedra dos Ancestrais** e um jogo de plataforma com narrativa e escolhas morais. O objetivo e chegar ao coracao da Pedra e decidir o que Caio levara para fora dela: memoria, tesouro ou silencio.

O diferencial do projeto e misturar plataforma 2D, folclore regional, memoria ancestral e tres finais diferentes em um jogo autoral feito em Python/Pygame.

## Inspiracao e Moral

O jogo e inspirado na **Pedra do Castelo**, ponto turistico e formacao rochosa real de Castelo do Piaui, conhecida por suas grutas, saloes, pinturas rupestres e lendas locais.

A moral do jogo e que **a memoria de um povo vale mais que riqueza material**. A Pedra nao guarda apenas tesouro: ela guarda nomes, historias, simbolos e lembrancas de geracoes antigas. O jogador decide se Caio respeita essa heranca, tenta se aproveitar dela ou sai sem assumir essa responsabilidade.

## Entrega Final

O projeto foi entregue como produto fechado em executavel Windows:

```text
dist/PedraDosAncestrais.exe
```

Esse arquivo roda fora do editor e nao depende de abrir o projeto Python manualmente.

Build final atualizado em 13/05/2026.

## Visao Geral Tecnica

- **Genero:** plataforma 2D narrativo
- **Plataforma:** PC Windows
- **Tecnologia:** Python + Pygame
- **Build:** PyInstaller
- **Resolucao interna:** 640 x 360
- **Janela/tela final:** 1920 x 1080 fullscreen
- **Estilo visual:** pixel art procedural
- **Interface:** HUD, dialogos, menu, creditos, game over e finais em Full HD
- **Audio:** musicas e efeitos proceduralmente gerados em codigo
- **Progressao:** menu principal -> fases -> caverna final -> escolha -> final

## Controles

| Tecla | Acao |
| --- | --- |
| `A` / seta esquerda | Mover para a esquerda |
| `D` / seta direita | Mover para a direita |
| `W` / seta cima / `Espaco` | Pular |
| `Z` ou `J` | Atacar |
| `X` ou `K` | Interagir / avancar dialogo |
| `ENTER` | Confirmar / tentar novamente |
| `ESC` | Pausar / voltar |
| `M` | Voltar ao menu quando pausado |
| `Alt + F4` | Fechar o jogo |

## Estrutura do Jogo

| Parte | Funcao |
| --- | --- |
| Menu principal | Tela inicial com Jogar, Creditos, Controles, Opcoes e Sair |
| Vila | Apresenta NPCs, interacao, coleta e primeiro objetivo |
| Floresta | Introduz exploracao, registros e inimigos |
| Ruinas | Reforca leitura, selo ancestral e desafio |
| Trilha | Testa plataforma, altares, registros, inimigos e progressao |
| Caverna | Climax com registros finais, Guardiao, Iracema e escolha final |
| Final | Mostra um dos tres finais e o resumo da jornada |

## Tres Finais

No fim da caverna, depois do Guardiao e do encontro com Iracema, a Pedra apresenta tres escolhas:

| Escolha | Resultado |
| --- | --- |
| Carregar as memorias | Final verdadeiro |
| Tomar o tesouro | Final ruim |
| Partir em silencio | Final neutro |

O final tambem mostra o que a Pedra reconheceu na jornada: conversas, inscricoes, altares, recompensas, Guardiao e escolha de Iracema.

## Game Loop

### Loop Micro

```text
Explorar -> encontrar desafio -> pular/atacar/interagir -> receber recompensa/informacao -> completar objetivo -> avancar
```

### Loop Macro

```text
Menu -> Vila -> Floresta -> Ruinas -> Trilha -> Caverna -> Escolha final -> Final -> Jogar novamente
```

## Dificuldade Crescente

| Momento | Implementacao |
| --- | --- |
| Apresentacao | Vila e floresta ensinam movimento, interacao, coleta e leitura |
| Teste | Trilha combina plataformas, inimigos, altares, registros e objetivos |
| Climax | Caverna tem Guardiao, registros finais, Iracema e decisao moral |

## HUD e Interface

Durante a gameplay, o jogador recebe informacoes constantes:

- Vida por coracoes
- Objetivos da fase
- Contadores de progresso
- Prompt de interacao
- Mensagens de sistema
- Feedback visual ao tomar dano, coletar item e completar objetivos

A interface ativa fica em `systems/hd_ui.py`, renderizada diretamente em 1920 x 1080 para manter textos e HUD legiveis.

## Checklist P2

| Requisito | Status |
| --- | --- |
| Produto fechado em `.exe` | Cumprido |
| Tela de titulo | Cumprido |
| Menu com Jogar, Creditos e Sair | Cumprido |
| Gameplay jogavel | Cumprido |
| Game Over | Cumprido |
| Tentar novamente sem fechar | Cumprido |
| Tela de vitoria/final | Cumprido |
| Dificuldade crescente | Cumprido |
| Derrota ativa | Cumprido |
| HUD funcional | Cumprido |
| Contadores relevantes | Cumprido |
| Creditos da equipe | Cumprido |
| Codigo autoral | Cumprido |
| Build fora do editor | Cumprido |

## Sistemas Principais

| Sistema | Arquivo |
| --- | --- |
| Loop principal | `core/game.py` |
| Menu principal | `scenes/intro_scene.py` |
| Player | `gameplay/player/player.py` |
| Fisica | `config/physics.py` |
| Tilemap e colisao | `systems/tilemap.py` |
| HUD Full HD | `systems/hd_ui.py` |
| Dialogos | `systems/dialogue.py` |
| Dados de dialogo | `content/dialogue/npcs.json` |
| Karma e finais | `systems/karma.py` |
| Audio procedural | `systems/audio.py` |
| Recompensas | `systems/rewards.py` |
| Efeitos visuais | `art/fx.py` |
| Cena final | `scenes/ending_scene.py` |

## Como Rodar Pelo Codigo

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

## Como Gerar o Executavel

Com o ambiente virtual ativo:

```bash
python -m PyInstaller PedraDosAncestrais.spec
```

Saida:

```text
dist/PedraDosAncestrais.exe
```

Antes de gerar o build, feche qualquer instancia aberta do jogo para o Windows nao bloquear a substituicao do `.exe`.

## Testes

Com o ambiente virtual ativo:

```bash
.venv\Scripts\python.exe -m pytest tests\test_karma.py tests\test_karma_endings.py
```

Resultado validado:

```text
38 passed
```

## Estrutura do Projeto

```text
Pedra_dos_Ancestrais/
|-- main.py
|-- requirements.txt
|-- PedraDosAncestrais.spec
|-- config/
|-- core/
|-- scenes/
|-- gameplay/
|-- entities/
|-- systems/
|-- art/
|-- content/
|-- docs/
|-- tests/
|-- build/
`-- dist/
```

## Observacoes de Entrega

- O jogo nao comeca direto na fase.
- O jogo nao fecha ao morrer.
- O jogador pode tentar novamente sem reiniciar o programa.
- O jogo tem menu, creditos, gameplay, HUD, game over, progressao e finais.
- O arquivo principal para avaliacao e `dist/PedraDosAncestrais.exe`.
