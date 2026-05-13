# Game Design Document
# A Pedra dos Ancestrais

Documento atualizado para consolidar o GDD da P1 com a entrega da P2, refletindo o estado atual do projeto neste workspace e as atualizacoes encontradas no GitHub em 13/05/2026.

---

## 1. Identificacao

| Campo | Informacao |
| --- | --- |
| Titulo | A Pedra dos Ancestrais |
| Genero | Plataforma 2D narrativo com elementos leves de RPG |
| Plataforma | PC Windows |
| Tecnologia | Python 3 + Pygame 2 |
| Build de entrega | `dist/PedraDosAncestrais.exe` |
| Resolucao interna | 640 x 360 |
| Janela final | 1920 x 1080 fullscreen |
| Jogadores | 1 jogador |
| Publico-alvo | 12+ |
| Estilo visual | Pixel art procedural |
| Audio | Musicas e efeitos gerados por codigo |
| Status P2 | Produto jogavel e fechado em executavel |

---

## 2. Pitch

**A Pedra dos Ancestrais** e um jogo 2D de plataforma ambientado no sertao piauiense e inspirado na Pedra do Castelo, em Castelo do Piaui. O jogador controla Caio, um jovem chamado por uma pedra misteriosa ligada a memoria de sua familia, de sua vila e dos povos ancestrais que passaram por aquele lugar.

O jogo combina exploracao, plataforma, dialogos, combate simples, leitura de inscricoes, ativacao de altares, recompensas e uma decisao final. A moral central e que **a memoria de um povo vale mais que riqueza material**.

---

## 3. Proposta de Valor

| Pilar | Implementacao atual |
| --- | --- |
| Exploracao com proposito | NPCs, registros, altares, recompensas e inscricoes revelam lore e progresso |
| Plataforma acessivel | Movimento responsivo com coyote time, jump buffer e colisao AABB |
| Moral implicita | Sistema de karma silencioso acompanha coragem, sabedoria, ganancia e escolha de Iracema |
| Identidade cultural | Sertao piauiense, Pedra do Castelo, memoria ancestral e tradicao oral |
| Produto fechado | Build Windows gerado com PyInstaller em `dist/PedraDosAncestrais.exe` |

---

## 4. Narrativa

Caio vive em uma pequena vila do sertao piauiense. Em uma manha de vento forte, sente que a Pedra o chama. Os moradores contam historias contraditorias: alguns falam em tesouro, outros em maldicao, outros em memoria. Caio segue para descobrir o que existe dentro da Pedra.

A Pedra nao guarda apenas ouro. Ela guarda nomes, historias, simbolos, escolhas e lembrancas. Ao longo da jornada, o jogador decide, por suas acoes, se Caio sera alguem que carrega essa memoria, alguem que busca riqueza ou alguem que atravessa tudo sem se comprometer.

### O Sinal

O fio narrativo da P2 e **o Sinal**: uma marca invisivel de quem foi chamado pela Pedra. Ele conecta Seu Zequinha, os altares, Iracema, o Guardiao e a decisao final.

- Seu Zequinha reconhece que Caio foi chamado.
- Os altares e inscricoes confirmam a ligacao de Caio com a Pedra.
- Iracema testa se Caio entende o peso da memoria.
- O Guardiao permite a passagem apenas depois de ser vencido.
- A escolha final define o que Caio leva para fora da Pedra.

---

## 5. Personagens

| Personagem | Papel |
| --- | --- |
| Caio | Protagonista silencioso; suas acoes definem sua moral |
| Seu Zequinha | Anciao da vila; avisa Caio sobre o preco da Pedra |
| Aldeoes | Moradores que apresentam medo, crenca, curiosidade e memoria oral |
| Comerciante | Conta historias de pessoas que buscaram a Pedra antes de Caio |
| Zinha | Crianca ligada ao tema da protecao e da memoria |
| Iracema | Espirito da Pedra; apresenta o trato e o peso da lembranca |
| Guardiao | Estatua ancestral que protege o coracao da Pedra |

---

## 6. Fluxo da P2

O fluxo implementado na P2 e:

```text
Menu principal
  -> Vila
  -> Floresta
  -> Ruinas
  -> Trilha
  -> Caverna
  -> Escolha final
  -> Final verdadeiro / neutro / ruim
  -> Creditos ou retorno ao menu
```

Cada fase introduz ou reforca um aspecto do jogo:

| Cena | Funcao |
| --- | --- |
| Menu principal | Jogar, Creditos, Controles, Opcoes e Sair |
| Vila | NPCs, dialogos, primeira exploracao e contexto narrativo |
| Floresta | Registros, inimigos, recompensas e progressao |
| Ruinas | Selo ancestral, inscricoes e desafios de exploracao |
| Trilha | Altares, morcegos, plataformas e abertura do portal |
| Caverna | Registros finais, Iracema, Guardiao e decisao moral |
| Final | Mostra um dos tres finais e o resumo da jornada |

---

## 7. Controles

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

---

## 8. Gameplay

### Movimento

O player usa fisica por frame, com constantes em `config/physics.py`:

| Sistema | Valor / comportamento |
| --- | --- |
| Velocidade horizontal | 2.5 px/frame |
| Forca do pulo | -8.0 px/frame |
| Gravidade | +0.4 px/frame |
| Velocidade maxima de queda | 10 px/frame |
| Coyote time | 8 frames |
| Jump buffer | 6 frames |
| Colisao | AABB em eixos separados |

### Combate

Caio pode atacar com `Z` ou `J`. O ataque usa hitbox curta na direcao em que o personagem esta olhando. Inimigos causam dano por contato; o player possui invencibilidade temporaria apos sofrer dano.

### Interacao

O jogo mostra prompts quando Caio esta perto de objetos interativos:

- `[X] conversar`
- `[X] ativar altar`
- `[X] ler registro`
- `[X] observar`
- Opcoes de escolha na caverna final

---

## 9. Sistema de Karma

O karma e invisivel para o jogador. Nao existe barra, aviso ou pontuacao na tela. O sistema registra comportamento e decide o final.

| Atributo | Faixa | Aumenta quando |
| --- | --- | --- |
| Coragem | 0 a 5 | Enfrenta inimigos, ajuda espiritos, supera o Guardiao |
| Sabedoria | 0 a 5 | Conversa, le registros, ativa altares, resolve desafios |
| Ganancia | 0 a 5 | Quebra objetos decorativos ou escolhe o tesouro |
| Divida de Iracema | `True` / `False` / `None` | Honra, trai ou recusa o trato |

### Calculo de final

```text
Se ganancia >= 3:
    final = ruim
Senao se coragem >= 2 e sabedoria >= 2 e ganancia <= 1:
    final = verdadeiro
Senao:
    final = neutro
```

### Resumo de jornada

A P2 tambem registra progresso para o encerramento:

- Conversas na vila
- Registros da floresta
- Selos e registros das ruinas
- Altares e registros da trilha
- Registros da caverna
- Recompensas coletadas
- Guardiao liberto
- Escolha de Iracema

---

## 10. Tres Finais

| Final | Condicao | Resultado narrativo |
| --- | --- | --- |
| Verdadeiro | Coragem e sabedoria suficientes, baixa ganancia | Caio entende que o tesouro e memoria |
| Neutro | Jornada completa sem compromisso forte | Caio sai vivo, mas incompleto |
| Ruim | Ganancia alta | Caio encontra riqueza, mas perde o sentido da heranca |

Na caverna final, o jogador escolhe entre:

- Carregar as memorias.
- Tomar o tesouro.
- Partir em silencio.

Essa escolha conversa com o karma acumulado e reforca o tema central da obra.

---

## 11. Interface e HUD

A P2 implementa interface em Full HD por `systems/hd_ui.py`, renderizada sobre a base interna 640 x 360 e escalada para 1920 x 1080.

Elementos implementados:

- HUD de vida com coracoes.
- Objetivos da fase.
- Contadores de progresso.
- Prompts de interacao.
- Mensagens de sistema.
- Menu principal com telas internas.
- Tela de pausa.
- Game over com tentativa novamente.
- Tela de final e creditos.
- Feedback visual de dano, coleta, leitura e conclusao de objetivo.

---

## 12. Arte

O jogo usa pixel art procedural. Os sprites, tiles, efeitos e elementos de interface sao desenhados por codigo, sem depender de assets externos de imagem.

| Area | Implementacao |
| --- | --- |
| Sprites | `art/sprites.py` |
| Tiles | `art/tiles.py` |
| Efeitos | `art/fx.py` |
| Paleta | `art/palette.py` e `config/palette.py` |

O estilo visual busca remeter ao sertao, a pedra, a noite da trilha, as ruinas, os cristais da caverna e a presenca espiritual de Iracema.

---

## 13. Audio

A P2 possui sistema de audio em `systems/audio.py`, com musicas e efeitos gerados proceduralmente em codigo.

O audio cobre:

- Ambiencia de menu e fases.
- Feedback de interacao.
- Feedback de combate.
- Eventos narrativos.
- Momento final.

---

## 14. Arquitetura Tecnica

| Camada | Responsabilidade |
| --- | --- |
| `config/` | Constantes de tela, fisica, paleta e IDs de cena |
| `core/` | Loop principal, cena, input, camera e Event Bus |
| `shared/` | Enums e utilitarios |
| `gameplay/` | Player, estados, NPCs e inimigos |
| `entities/` | Shims de compatibilidade |
| `systems/` | Karma, HUD, dialogos, tilemap, audio, recompensas |
| `art/` | Arte procedural |
| `content/` | Dialogos em JSON |
| `scenes/` | Composicao das fases e fluxo narrativo |
| `tests/` | Testes unitarios |

### Padroes usados

- Scene Manager para troca de cenas.
- Event Bus para comunicacao desacoplada.
- Input Manager centralizado.
- State Machine para estados do player.
- Data Loader para dialogos em JSON.
- KarmaSystem separado da UI.
- PyInstaller para empacotamento.

---

## 15. Estrutura Atual do Projeto

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

---

## 16. Entrega P2

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
| Testes automatizados | Cumprido |
| Documentacao atualizada | Cumprido |

### Build final

```text
dist/PedraDosAncestrais.exe
```

Build final atualizado em 13/05/2026.

---

## 17. Testes

Suites existentes:

| Suite | Arquivo |
| --- | --- |
| Estados do player | `tests/test_player_states.py` |
| Event Bus | `tests/test_event_bus.py` |
| Dialogue Loader | `tests/test_dialogue_loader.py` |
| Karma | `tests/test_karma.py` |
| Karma e finais | `tests/test_karma_endings.py` |

Comando validado:

```bash
.venv\Scripts\python.exe -m pytest tests\
```

Resultado em 13/05/2026:

```text
56 passed
```

---

## 18. Como Rodar

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

---

## 19. Como Gerar o Executavel

Com o ambiente virtual ativo:

```bash
python -m PyInstaller PedraDosAncestrais.spec
```

Saida:

```text
dist/PedraDosAncestrais.exe
```

Antes de gerar o build, feche qualquer instancia aberta do jogo para o Windows nao bloquear a substituicao do `.exe`.

---

## 20. Referencias

| Referencia | Uso |
| --- | --- |
| Pedra do Castelo, Castelo do Piaui | Inspiracao geografica e cultural |
| Cordel nordestino | Moralidade, tradicao oral e ritmo narrativo |
| Celeste | Plataforma responsiva e acessivel |
| Undertale | Moral implicita e finais diferentes |
| Hollow Knight | Lore distribuido pelo mundo |
| Pygame | Render, input, audio e loop principal |

---

## 21. Historico de Atualizacao

| Data | Atualizacao |
| --- | --- |
| Abril/2026 | GDD P1 com conceito, narrativa, mecanicas planejadas e arquitetura inicial |
| Maio/2026 | P2 consolidada com build executavel, fluxo completo, finais, HUD HD, audio, testes e README atualizado |
| 13/05/2026 | Documento atualizado com base no branch atual e no conteudo mais recente do GitHub |

---

*Documento do projeto academico "A Pedra dos Ancestrais".*
