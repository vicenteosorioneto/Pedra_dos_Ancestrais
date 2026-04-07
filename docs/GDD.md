# Game Design Document
# A Pedra dos Ancestrais

---

| Campo         | Informação                              |
| ------------- | --------------------------------------- |
| Título        | A Pedra dos Ancestrais                  |
| Gênero        | Plataforma 2D com elementos de RPG leve |
| Plataforma    | PC (Windows / Linux / macOS)            |
| Engine        | Python 3 + Pygame 2                     |
| Público-alvo  | 12+ anos                                |
| Jogadores     | 1 jogador (single-player)               |
| Tempo médio   | 25–40 minutos por partida               |
| Classificação | Livre (sem violência explícita)         |

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Conceito e Proposta de Valor](#2-conceito-e-proposta-de-valor)
3. [Narrativa](#3-narrativa)
4. [Personagens](#4-personagens)
5. [Mecânicas de Gameplay](#5-mecânicas-de-gameplay)
6. [Sistema de Karma](#6-sistema-de-karma)
7. [Design das Cenas](#7-design-das-cenas)
8. [Inimigos e Chefe](#8-inimigos-e-chefe)
9. [Interface e HUD](#9-interface-e-hud)
10. [Direção de Arte](#10-direção-de-arte)
11. [Áudio](#11-áudio)
12. [Fluxo do Jogo](#12-fluxo-do-jogo)
13. [Arquitetura Técnica](#13-arquitetura-técnica)
14. [Requisitos e Ferramentas](#14-requisitos-e-ferramentas)
15. [Escopo e Roadmap](#15-escopo-e-roadmap)
16. [Referências e Inspirações](#16-referências-e-inspirações)

---

## 1. Visão Geral

**A Pedra dos Ancestrais** é um jogo 2D de plataforma com narrativa ambientado no **sertão nordestino do Piauí**, inspirado na formação geológica real conhecida como **Pedra do Castelo** (Castelo do Piauí). O jogador controla **Caio**, um jovem que é guiado pelo vento até uma pedra ancestral e misteriosa, onde deverá superar desafios físicos e morais para descobrir o segredo que ela guarda.

O jogo mistura plataforma de precisão com uma narrativa silenciosa impulsionada por escolhas — o jogador não escolhe respostas em menus, mas suas **ações durante o jogo** (com quem conversa, o que quebra, quem ajuda) moldam o desfecho da história.

### Diferencial principal

A maioria dos jogos de plataforma com narrativa usa diálogos com múltipla escolha para refletir a moralidade do jogador. Em **A Pedra dos Ancestrais**, a moral é rastreada de forma completamente silenciosa: o jogo observa comportamentos naturais do jogador e calcula o final sem que ele perceba que está sendo avaliado.

---

## 2. Conceito e Proposta de Valor

### Declaração de conceito

> *"Um jovem do sertão encontra uma pedra que existe antes dos seus avós. Para entrar, ele precisa apenas ter coragem. Para sair, ele precisa saber quem é."*

### Pilares de design

| Pilar | Descrição |
| --- | --- |
| **Exploração com propósito** | Cada parte do cenário conta uma história; o jogador é recompensado por observar e interagir |
| **Plataforma acessível e responsivo** | Controles precisos com coyote time e jump buffer tornam o jogo justo e agradável |
| **Moral implícita** | O jogo não julga o jogador abertamente; as consequências aparecem no final |
| **Identidade cultural** | Estética, personagens e narrativa profundamente enraizados na cultura do sertão nordestino |

### Público-alvo

- Jogadores de 12 a 30 anos que apreciam narrativa em jogos
- Estudantes e curiosos sobre cultura e folclore nordestino
- Fãs de plataforma 2D com elementos de exploração (Hollow Knight, Celeste, Undertale)

---

## 3. Narrativa

### Premissa

Caio é um rapaz de uma pequena vila do sertão piauiense. Numa manhã de vento forte, ele sente como se algo o chamasse — um sopro que vem da direção da Pedra do Castelo, a formação rochosa que existe nos arredores da vila desde antes de qualquer memória viva. Os moradores da vila têm histórias sobre a pedra: uns dizem que guarda um tesouro, outros que guarda um segredo, e os mais velhos dizem que a pedra cobra um preço.

Caio parte.

### Estrutura narrativa

O jogo é dividido em **4 atos** que seguem uma jornada do herói adaptada ao contexto do sertão:

#### Ato 0 — A Chamada (Tela de Título)
A pedra é apresentada em pixel art ao fundo de um céu crepuscular. Não há texto além do título. O silêncio e a música criam a atmosfera antes do jogo começar.

#### Ato 1 — A Vila (VillageScene)
Caio parte da vila de manhã cedo. Os moradores têm coisas a dizer. Seu Zequinha, o ancião misterioso, avisa que a pedra cobra o que o coração mais deseja — e cobra o preço mais alto. Um comerciante conta que três homens foram à pedra no século passado e nenhum voltou do mesmo jeito. A vila é viva, e o jogador é livre para conversar ou ignorar todos.

A transição para a trilha acontece quando Caio alcança o limite leste da vila.

#### Ato 2 — A Trilha (TrailScene)
Noite. Caio sobe a trilha rochosa em direção à entrada da pedra. O céu é roxo, com lua cheia. Morcegos corrompidos (manifestações da energia negativa da pedra) patrulham as plataformas. Altares espalhados pelo caminho podem ser ativados — cada um acende uma chama e revela um fragmento da lenda através de partículas e efeitos de luz.

Quando os três altares são ativados, um portal de entrada se abre na base da pedra.

#### Ato 3 — A Caverna (CaveScene)
O interior da Pedra. Cristais âmbar iluminam passagens estreitas. O ar tem qualidade diferente. Morcegos mais rápidos. E então Caio encontra **Iracema** — um espírito que vive dentro da pedra desde tempos antigos. Iracema faz uma proposta: ela ajuda Caio a chegar ao coração da pedra, mas ele precisará honrar uma dívida.

No centro da caverna: o **Guardião**, uma estátua de pedra animada que protege o tesouro ancestral. O Guardião não é um vilão — é um teste. Derrotá-lo revela o que a pedra realmente guarda.

O final depende de quem Caio se tornou ao longo da jornada.

### Os três finais

#### Final Verdadeiro — "O Tesouro não é ouro"
*Condição:* Caio conversou com os moradores, enfrentou os desafios com coragem e honrou o trato com Iracema.

A pedra revela uma câmara com registros ancestrais — histórias de gerações gravadas na rocha. O tesouro é memória. Caio sai da pedra diferente: mais inteiro. Os moradores da vila percebem algo mudou nele. Fim com esperança.

#### Final Neutro — "Quem entra, muda"
*Condição:* Caio completou a jornada sem se comprometer com nada nem com ninguém.

A câmara se abre, mas está vazia. Iracema diz: *"O tesouro só aparece pra quem realmente procura."* Caio sai confuso. Talvez volte um dia.

#### Final Ruim — "A ganância cobra juros"
*Condição:* Caio quebrou potes, pegou itens-armadilha, ignorou NPCs e traiçoou Iracema.

A pedra revela o tesouro — ouro e joias ancestrais. Mas ao tocar, Caio sente o peso de tudo que ignorou no caminho. Uma sequência mostra o ouro virando pó. Iracema: *"Você encontrou o que procurava."* Fim ambíguo, sem redenção.

### Lore e universo

A lore é distribuída em fragmentos — nunca narrada diretamente:

- **Diálogos dos NPCs** revelam a história oral da vila
- **Altares na trilha** ativam fragmentos visuais de partículas
- **Registros na caverna** (tiles especiais com símbolos) contam a história dos ancestrais
- **Iracema** é a guardiã da memória — ela não é boa nem má, apenas antiga
- O **Guardião** foi colocado pelos ancestrais para garantir que apenas os dignos chegassem ao coração da pedra

---

## 4. Personagens

### Caio (Protagonista)

| Atributo | Valor |
| --- | --- |
| Aparência | Jovem sertanejo, camisa vermelha, calça azul, chapéu de couro |
| Personalidade | Determinado, curioso, moral definida pelas ações do jogador |
| HP inicial | 3 corações |
| HP máximo | 3 corações |
| Habilidades | Correr, pular (com coyote time), atacar (golpe simples), interagir |

Caio não fala. Sua personalidade é totalmente definida pelas ações do jogador — o jogo não explica seus pensamentos em caixas de texto.

### Seu Zequinha (NPC — Ancião)

O sábio da vila. Conhece a história da pedra melhor do que qualquer outro. Aparece parado perto da saída da vila e desaparece misteriosamente após o diálogo — sugerindo que talvez não seja apenas um velho.

*Diálogo:*
> *"A pedra chama... mas só entra quem está destinado. Se um dia você encontrar o símbolo, saiba: o tesouro não alimenta o corpo. Ele alimenta o que você mais deseja — e cobra o preço mais alto."*

### Aldeãos (NPCs — Villagers)

Habitantes comuns da vila. Cada um tem uma perspectiva diferente sobre a pedra — medo, curiosidade, desdém ou superstição. Conversar com eles aumenta a sabedoria de Caio sem que o jogo informe isso.

*Exemplos de diálogo:*
- Aldeão 1: *"Esse vento tá esquisito hoje... parece que a Pedra tá chamando."*
- Aldeão 2: *"Seu Zequinha foi lá pra cima ontem à noite. Eu vi com meus próprios olhos. Nunca é boa ideia."*
- Comerciante: *"Três homens foram nessa pedra no século passado. Nenhum voltou do mesmo jeito, menino."*

### Iracema (Espírito — NPC da Caverna)

Um espírito feminino que habita a caverna. Representada por partículas de luz azul. Faz um trato com Caio — ajuda a abrir o caminho até o coração da pedra em troca de uma promessa que o jogador decide honrar ou trair.

*Diálogo inicial:*
> *"Você não é o primeiro a procurar alguém aqui dentro. E não será o último a se perder."*

### Guardião (Mini-Boss)

Uma estátua de pedra de 26×44 pixels, animada pela energia ancestral. Não é um vilão — é um guardião. Acorda quando Caio se aproxima do centro da caverna. Tem duas fases:

- **Fase 1:** Caminha em direção ao player, causa knockback por contato
- **Fase 2** (HP ≤ 4): Acelera e passa a gerar ondas de choque no chão

Após ser derrotado, o Guardião fala antes de se desfazer:

> *"Você... tem o sinal. Pode passar. Mas devia voltar."*

---

## 5. Mecânicas de Gameplay

### 5.1 Movimento e Física

O sistema de física é baseado em velocidade e gravidade por frame, com constantes configuráveis:

| Constante | Valor | Descrição |
| --- | --- | --- |
| Velocidade horizontal | 2.5 px/frame | Velocidade de movimento esquerda/direita |
| Força do pulo | −8.0 px/frame | Impulso vertical inicial |
| Gravidade | +0.4 px/frame² | Aceleração gravitacional por frame |
| Velocidade máx. de queda | 10.0 px/frame | Terminal velocity |
| Coyote time | 8 frames | Frames de graça após sair de uma plataforma |
| Jump buffer | 6 frames | Frames em que o pulo é aceito antecipadamente |

**Coyote time:** Permite que o jogador pule por até 8 frames após sair de uma plataforma, mesmo sem estar no chão. Elimina a frustração de pulos perdidos por milissegundos.

**Jump buffer:** Se o jogador pressionar pulo até 6 frames antes de tocar o chão, o pulo é executado assim que o personagem aterra. Torna o jogo mais responsivo.

**Colisão AABB:** O player tem um hitbox de 12×28 pixels. A resolução de colisão é feita primeiro no eixo X, depois no eixo Y — garante que colisões de canto se resolvam de forma previsível.

### 5.2 Controles

| Tecla | Ação |
| --- | --- |
| `A` / `←` | Mover para a esquerda |
| `D` / `→` | Mover para a direita |
| `W` / `↑` / `Espaço` | Pular |
| `Z` ou `J` | Atacar (golpe de curta distância) |
| `X` ou `K` | Interagir com NPCs / ativar altares |
| `ESC` | Pausar |

O mapeamento de teclas é centralizado em um `InputManager` — remapear qualquer tecla exige editar apenas um arquivo.

### 5.3 Combate

O sistema de combate é simples e deliberado — o jogo não é um beat 'em up:

**Ataque do player:**
- Hitbox de ataque: 20×16 pixels, projetada na direção que Caio está olhando
- Duração do hitbox ativo: 8 frames (do frame 4 ao 12 do ciclo de ataque)
- Cooldown de ataque: 24 frames (~0.4 segundos a 60 FPS)
- Animação dedicada com frame único de ataque

**Receber dano:**
- Caio perde 1 coração ao ser atingido por um inimigo
- Ao tomar dano, Caio entra em estado HURT com knockback vertical
- **iFrames:** 60 frames de invencibilidade após tomar dano (evita múltiplos hits simultâneos)
- Se HP chega a zero: estado DEAD, sem possibilidade de reverter sem reiniciar

**Feedback de dano:**
- Camera shake ao tomar dano do boss
- Coração quebra em partículas no HUD
- Flash vermelho na tela

### 5.4 Interação com NPCs

- Caio pode falar com qualquer NPC dentro de 40 pixels de distância
- O HUD mostra `[X] conversar` quando próximo de um NPC
- O diálogo bloqueia o input de movimento enquanto ativo
- Cada NPC tem uma sequência de linhas exibidas com efeito typewriter
- Pressionar X avança a linha ou fecha o diálogo se na última linha
- Se o texto ainda está sendo digitado, X completa o texto imediatamente (skip do typewriter)

### 5.5 Altares (Ato 2 — Trilha)

Três altares estão posicionados ao longo da trilha, em plataformas elevadas:

1. **Altar 1** — Posição intermediária, acessível logo no início
2. **Altar 2** — Plataforma mais alta, exige sequência de pulos precisos
3. **Altar 3** — Próximo ao topo da trilha, bloqueado por morcegos próximos

**Mecânica:**
- Caio pressiona X perto do altar para ativá-lo
- Partículas âmbar surgem do altar e uma mensagem aparece brevemente
- Quando os 3 altares estão ativos, o portal de entrada da caverna se abre

**Propósito narrativo:** Os altares representam os três pilares da sabedoria ancestral: *Coragem*, *Paciência* e *Memória*.

---

## 6. Sistema de Karma

O sistema de karma é **completamente invisível para o jogador**. Não há barra, não há indicadores — o jogo simplesmente observa.

### Atributos rastreados

| Atributo | Faixa | Como aumenta | Como diminui |
| --- | --- | --- | --- |
| **Coragem** | 0–5 | Enfrentar inimigos, ajudar espíritos | Ignorar NPCs em perigo |
| **Ganância** | 0–5 | Quebrar potes decorativos, pegar itens-armadilha | Deixar itens valiosos voluntariamente |
| **Sabedoria** | 0–5 | Conversar com NPCs, ler registros, resolver puzzles | — |
| **Dívida de Iracema** | True / False / None | Honrar o trato | Trair o trato |

### Cálculo do final

```
SE ganância ≥ 3:
    final = "ruim"
SENÃO SE coragem ≥ 2 E sabedoria ≥ 2 E ganância ≤ 1:
    final = "verdadeiro"
SENÃO:
    final = "neutro"
```

### Exemplos de ações e consequências

| Ação do jogador | Efeito no karma |
| --- | --- |
| Conversar com todos os aldeões | +3 sabedoria |
| Conversar com Seu Zequinha | +1 sabedoria |
| Derrotar um morcego | +1 coragem |
| Quebrar um pote decorativo | +1 ganância |
| Honrar o trato com Iracema | divida = True |
| Trair o trato com Iracema | divida = False |
| Ativar os 3 altares | +1 sabedoria por altar |

---

## 7. Design das Cenas

### 7.1 Tela de Título (IntroScene)

**Atmosfera:** Crepúsculo no sertão. Céu em gradiente roxo-vermelho-laranja. Lua cheia visível. Estrelas com seed fixa (aparecem sempre no mesmo lugar).

**Elemento central:** A Pedra do Castelo desenhada em pixel art procedural, com suas 3 colunas de alturas diferentes, janelas escuras com brilho âmbar interno e rachaduras verticais.

**Elementos interativos:**
- Partículas de poeira sobem lentamente do chão
- Texto "A PEDRA DOS ANCESTRAIS" com sombra dourada
- Subtítulo "Uma lenda do Piauí" em tom mais suave
- "Pressione ENTER para começar" pisca a cada 40 frames

**Transição:** Ao pressionar Enter ou Espaço, a cena é substituída pelo Ato 1.

---

### 7.2 Ato 1 — A Vila (VillageScene)

**Dimensões:** 60 colunas × 22 linhas de tiles = 960 × 352 pixels de mundo

**Parallax de fundo (5 camadas):**

| Camada | Velocidade | Conteúdo |
| --- | --- | --- |
| 0 | 0.05× | Gradiente de céu do sertão |
| 1 | 0.05× | Sol com raios, Pedra do Castelo ao fundo (pequena) |
| 2 | 0.15× | Pedra do Castelo (versão media, parallax) |
| 3 | 0.30× | Silhueta de montanhas distantes |
| 4 | 0.55× | Colinas de solo próximas |

**Layout do mapa:**
- Chão principal nas linhas 14–21 (pedra topo → pedra meio → terra)
- 5 plataformas flutuantes em alturas variadas (linhas 8–12)
- Cactos como obstáculos naturais e hazards visuais (sem dano neste ato)
- Potes decorativos e caixotes espalhados (interagíveis — quebrar aumenta ganância)
- Trepadeiras penduradas nas plataformas (decoração)

**NPCs posicionados:**

| NPC | Posição | Patrulha | Chave de diálogo |
| --- | --- | --- | --- |
| Aldeão 1 (variante 0) | col 7, chão | 40px | `aldeao_1` |
| Aldeão 2 (variante 1) | col 21, chão | Parado | `aldeao_2` |
| Seu Zequinha | col 30, chão | Parado | `zequinha` |
| Aldeão 3 (variante 2) | col 37, chão | Parado | `aldeao_2` |

**Evento especial:** Após Caio falar com Seu Zequinha, o ancião **desaparece** na próxima atualização. Uma mensagem de sistema aparece: *"Zequinha... sumiu?"*

**Saída:** Lado direito do mapa (col 58). Ao sair, transição fade para a Trilha.

---

### 7.3 Ato 2 — A Trilha (TrailScene)

**Dimensões:** 70 colunas × 22 linhas = 1120 × 352 pixels de mundo

**Tema visual:** Noturno. Céu roxo-escuro com gradiente para navy. Lua cheia com halo de luz difusa. Estrelas com seed aleatória diferente a cada sessão.

**Mecânica de escalada:** O mapa é construído como uma série de degraus que sobem da esquerda para a direita — o jogador literalmente sobe a montanha. Cada segmento tem altura diferente, exigindo julgamento nos pulos.

**Plataformas de castelo:** Intercaladas com as plataformas de pedra, plataformas de pedra lavrada (tile_pedra_castelo) dão ao mapa um aspecto de ruínas antigas no topo da montanha.

**Tochas:** Posicionadas ao longo da trilha, com chama animada e halo de luz âmbar. Criam pontos de referência visuais e luz ambiente.

**Altares (3):**
- Altar A: col 20, altura da escalada 2
- Altar B: col 38, altura da escalada 4
- Altar C: col 55, altura da escalada 6 (mais difícil de alcançar)

**Inimigos:**

| Inimigo | Posição | Variante |
| --- | --- | --- |
| BatEnemy 1 | col 12, y=10×TILE | Normal |
| BatEnemy 2 | col 22, y=9×TILE | Normal |
| BatEnemy 3 | col 31, y=8×TILE | Normal |

**Portal de entrada:** Aparece na base da pedra (extremidade direita do mapa) quando os 3 altares são ativados. Antes disso, o mapa termina numa parede.

---

### 7.4 Ato 3 — A Caverna (CaveScene)

**Dimensões:** 60 colunas × 22 linhas = 960 × 352 pixels de mundo

**Tema visual:** Escuro profundo. Background em gradiente roxo-azul-escuro. Teto e chão fechados (tiles de rocha de caverna). Cristais âmbar emitem brilho próprio.

**Iluminação dinâmica:** Fontes de luz posicionadas a cada 15 colunas, usando `draw_ambient_light()` com blending aditivo. Cria pools de luz que se misturam com a escuridão.

**Elementos visuais:**
- Estalactites no teto (procedurais, desenhadas via `_draw_cave_details`)
- Pontos bioluminescentes pulsando no chão (efeito seno)
- Cristais âmbar como tiles sólidos (TileID 11)
- Plataformas de rocha brilhante (TileID 10) em alturas variadas

**Progressão:**

```
Entrada (col 0) → Corredor inicial → Plataformas médias → Morcegos rápidos
                                                          → Encontro com Iracema (col ~35)
                                                          → Boss arena (col ~45)
                                                          → Coração da pedra (col 58)
```

**Inimigos:**

| Inimigo | Posição | Variante |
| --- | --- | --- |
| BatEnemy 1 | col 11, y=8×TILE | `faster=True` |
| BatEnemy 2 | col 19, y=7×TILE | `faster=True` |
| BatEnemy 3 | col 28, y=8×TILE | `faster=True` |

**Guardião Estátua (Mini-Boss):**
- Posição: col 31, chão da caverna (y = 17×TILE − 44)
- Acorda quando Caio passa do col 25
- HP: 8 pontos
- Fase 1 (HP 8–5): velocidade 0.6 px/frame, movimento direto
- Fase 2 (HP 4–0): velocidade 1.2 px/frame + ondas de choque no chão a cada 2 segundos

---

## 8. Inimigos e Chefe

### BatEnemy — Morcego Corrompido

**Conceito:** Morcegos infectados pela energia negativa acumulada na pedra ao longo de séculos. Não são criaturas naturais — são manifestações de ganância e medo humanos.

| Atributo | Valor |
| --- | --- |
| Hitbox | 14×10 pixels |
| HP | 2 |
| Dano causado | 1 coração |
| Velocidade | 1.5 px/frame (normal) / 2.25 px/frame (faster) |
| Patrulha | 60 pixels da posição inicial |
| Oscilação vertical | Senoidal, amplitude 8px, frequência 0.04 |

**IA:** Patrulha horizontal simples com oscilação vertical senoidal — cria movimento fluido de morcego voando. Inverte direção ao atingir os limites da patrulha.

**Morte:** Emite 6 partículas roxas ao morrer.

---

### GuardianStatue — Guardião Estátua (Mini-Boss)

**Conceito:** Uma estátua de pedra animada pelos ancestrais, programada para testar os visitantes da pedra. Não age por malícia — age por dever.

| Atributo | Fase 1 | Fase 2 |
| --- | --- | --- |
| HP | 8 → 5 | 4 → 0 |
| Velocidade | 0.6 px/frame | 1.2 px/frame |
| Hitbox | 26×44 pixels | 26×44 pixels |
| Dano | Knockback (sem HP) | Knockback + ondas de choque |
| Ondas de choque | Não | A cada 120 frames |

**Mecânica de ondas de choque (Fase 2):**
- O Guardião golpeia o chão, criando duas ondas em direções opostas
- Cada onda tem hitbox de 8×6 pixels e velocidade 3.0 px/frame
- Dura 40 frames por onda
- Causar 1 ponto de dano ao player + camera shake

**Barra de HP:** Renderizada sobre o Guardião. Muda de vermelho (fase 1) para âmbar (fase 2).

**Comportamento de acordar:** Nos primeiros 60 frames após aparecer, o Guardião pisca os olhos — animação que usa o frame 1 do sprite.

---

## 9. Interface e HUD

### 9.1 HUD (Heads-Up Display)

O HUD é minimalista, consistente com a filosofia de não intrometer na experiência:

**Corações (HP):**
- Posição: canto superior esquerdo
- Fundo semitransparente com borda dourada (60×20 pixels)
- Cada coração é desenhado pixel a pixel (12×12 pixels, formato coração real)
- Coração cheio: vermelho com highlight e outline preto
- Coração vazio: escuro, mantém a silhueta
- Ao perder HP: o coração quebra em 4 partículas vermelhas

**Prompt de interação:**
- Aparece centralizado, acima do chão, quando Caio está próximo de um NPC
- Formato: `[X] conversar`
- Desaparece automaticamente quando Caio se afasta

### 9.2 Caixa de Diálogo

A caixa de diálogo aparece na parte inferior da tela:

| Elemento | Detalhes |
| --- | --- |
| Posição | y = SCREEN_H − 84 px |
| Altura | 80 pixels |
| Fundo | Cor `hud_bg` com alpha 220 |
| Borda | Dupla: preta externa + dourada interna |
| Avatar do NPC | 40×40 pixels no canto esquerdo com borda dourada |
| Nome do NPC | Fonte monoespaçada bold, cor dourada |
| Texto | Efeito typewriter: 2 caracteres por frame |
| Indicador de avanço | Triângulo ▼ dourado piscante quando a linha termina |
| Linha anterior | Exibida acima em cor mais escura (contexto) |

**Velocidade do typewriter:** 2 caracteres por frame = ~120 caracteres por segundo a 60 FPS — rápido o suficiente para não ser cansativo, lento o suficiente para ser lido.

### 9.3 Mensagens de Sistema

Para mensagens temporárias (eventos, dicas):
- Aparecem no centro-topo da tela
- Fade in/out suave com alpha proporcional ao tempo restante
- Duração padrão: 120 frames (2 segundos)

### 9.4 Efeitos de Tela

| Efeito | Quando aparece | Duração |
| --- | --- | --- |
| Fade in | Ao entrar em cada cena | 20–25 frames |
| Fade out | Ao sair de cada cena | 20 frames |
| Camera shake | Ao tomar dano do boss | 12–15 frames |
| Flash branco | Ao tomar dano forte | 8 frames |

---

## 10. Direção de Arte

### 10.1 Filosofia visual

O jogo usa **pixel art procedural** — todos os sprites, tiles e efeitos são gerados em Python puro, sem arquivos de imagem externos. Isso foi uma decisão deliberada: garante que o jogo funcione em qualquer ambiente sem dependências de assets, e força uma consistência visual definida por código.

**Resolução interna:** 640×360 pixels (upscaled 2× para 1280×720)

A resolução interna baixa é intencional: reforça o estilo pixel art e mantém o desempenho alto mesmo em hardware modesto.

### 10.2 Paleta de cores — Sertão (Atos 1 e 2)

| Nome | RGB | Uso |
| --- | --- | --- |
| sky_dawn | (255, 140, 60) | Céu do amanhecer |
| sky_mid | (220, 80, 40) | Meio do gradiente de céu |
| rock_light | (180, 140, 90) | Destaque de pedra |
| rock_mid | (140, 100, 60) | Cor base de pedra |
| rock_dark | (90, 60, 35) | Sombra de pedra |
| soil | (160, 110, 55) | Terra do sertão |
| cactus | (60, 120, 50) | Cacto |
| caio_shirt | (180, 40, 30) | Camisa vermelha do Caio |
| caio_pants | (50, 70, 140) | Calça azul do Caio |
| heart_red | (220, 40, 40) | Corações de HP |
| GOLD | (220, 180, 60) | UI, bordas, nomes |

### 10.3 Paleta de cores — Caverna (Ato 3)

| Nome | RGB | Uso |
| --- | --- | --- |
| bg_deep | (10, 5, 20) | Fundo profundo |
| bg_mid | (25, 15, 45) | Fundo médio |
| rock_cave | (40, 30, 60) | Rocha da caverna |
| rock_glow | (80, 50, 120) | Rocha com bioluminescência |
| amber_glow | (200, 130, 30) | Cristais e altares |
| spirit_blue | (80, 160, 220) | Partículas de Iracema |
| biolum | (60, 200, 150) | Pontos bioluminescentes |

### 10.4 Sprites e animações

**Caio (Player):**
- Sprite base: 16×32 pixels
- Frame 0: Idle (com breathing animation — sobe 1px a cada 30 frames)
- Frame 1: Caminhada A (pé esquerdo à frente)
- Frame 2: Caminhada B (pé direito à frente)
- Frame 3: Pulo / queda / ataque
- Ciclo de caminhada: [1, 0, 2, 0] — 4 frames, troca a cada 8 ticks
- Flip horizontal para direção esquerda

**NPCs:**
- Aldeão: variantes por índice (0, 1, 2) — roupas diferentes
- Ancião (Seu Zequinha): sprite único, bengala e roupa de ancião

**Inimigos:**
- Morcego: 2 frames de animação (asa aberta / asa fechada), troca a cada 8 ticks
- Guardião: 2 frames (acordando / caminhando), troca a cada 20 ticks

### 10.5 Tiles

Todos os tiles são 16×16 pixels com textura de ruído procedural (pixels de variação aleatória com seed fixa):

| Tile | Técnica visual | Detalhe |
| --- | --- | --- |
| Pedra topo | Gradiente + highlight | Topo claro, borda esquerda escura |
| Pedra castelo | Grade de juntas | Padrão de alvenaria com janelas escuras |
| Cristal | Polígono âmbar | Highlight e sombra diagonal |
| Rocha brilhante | Base + spots | Pontos bioluminescentes com fade |
| Cacto | Transparência | Tronco central com braços, espinhos |
| Pote | Elipse + boca | Artefato cerâmico nordestino |

---

## 11. Áudio

> *Nota: O sistema de áudio está arquitetado mas sem assets de som na versão atual. Esta seção descreve o design de áudio planejado.*

### 11.1 Música

| Cena | Estilo | Instrumentos sugeridos |
| --- | --- | --- |
| Tela de título | Ambient contemplativo | Violão sertanejo, ventania suave |
| Vila (Ato 1) | Folk nordestino leve | Zabumba, triângulo, sanfona |
| Trilha (Ato 2) | Tensão crescente | Cordas tensas, percussão esparsa |
| Caverna (Ato 3) | Ambient misterioso | Sintetizador, sons de pedra, gota d'água |
| Boss | Épico percussivo | Percussão tribal intensa |
| Final Verdadeiro | Resolução melancólica esperançosa | Violão + vocal sem letra |
| Final Ruim | Dissonância | Notas graves, ausência de harmonia |

### 11.2 Efeitos sonoros planejados

| Evento | Som sugerido |
| --- | --- |
| Pulo | Whoosh suave |
| Ataque | Impacto breve |
| Tomar dano | Grunt + impacto |
| Inimigo morto | Dispersão aérea |
| Diálogo abrindo | Clique de pedra suave |
| Altar ativado | Chime âmbar ascendente |
| Guardião acorda | Rugido de pedra pesada |
| Fade de cena | Silêncio com eco |

### 11.3 Implementação técnica

O pygame já está inicializado com `pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)`. Sons serão carregados como `pygame.mixer.Sound` e tocados em canais dedicados.

---

## 12. Fluxo do Jogo

```
                    ┌─────────────────────┐
                    │    TELA DE TÍTULO   │
                    │   (IntroScene)      │
                    └──────────┬──────────┘
                               │ ENTER / ESPAÇO
                               ▼
                    ┌─────────────────────┐
                    │    ATO 1 — VILA     │
                    │  (VillageScene)     │
                    │                     │
                    │  [fala com NPCs?]   │ ←── Karma: sabedoria
                    │  [explora?]         │ ←── Karma: sabedoria
                    │  [quebra potes?]    │ ←── Karma: ganância
                    └──────────┬──────────┘
                               │ Alcança borda leste
                               ▼
                    ┌─────────────────────┐
                    │   ATO 2 — TRILHA   │
                    │   (TrailScene)      │
                    │                     │
                    │  [derrota morcegos] │ ←── Karma: coragem
                    │  [ativa altares]    │ ←── Karma: sabedoria
                    └──────────┬──────────┘
                               │ 3 altares ativados + portal
                               ▼
                    ┌─────────────────────┐
                    │  ATO 3 — CAVERNA   │
                    │   (CaveScene)       │
                    │                     │
                    │  [encontra Iracema] │ ←── Karma: divida_iracema
                    │  [derrota guardião] │ ←── Karma: coragem
                    └──────────┬──────────┘
                               │ Chega ao coração da pedra
                               ▼
                    ┌─────────────────────┐
                    │  CÁLCULO DO FINAL   │
                    │  (karma.final_type) │
                    └──────────┬──────────┘
                    ┌──────────┴──────────┐─────────────────┐
                    ▼                     ▼                  ▼
              "verdadeiro"           "neutro"             "ruim"
              (coração da           (câmara              (ouro que
               memória)              vazia)               vira pó)
```

---

## 13. Arquitetura Técnica

### 13.1 Stack tecnológica

| Componente | Tecnologia | Versão |
| --- | --- | --- |
| Linguagem | Python | 3.9+ |
| Engine/Framework | Pygame | 2.1+ |
| Assets | Geração procedural | — |
| Dados de conteúdo | JSON | — |
| Testes | pytest | — |

### 13.2 Arquitetura do software

O projeto usa uma **arquitetura em camadas** com comunicação via **Event Bus**:

```
config/       → constantes por domínio
shared/       → enums, tipos, utilitários
core/         → engine: loop, cenas, câmera, event bus, input
gameplay/     → lógica de jogo: player, inimigos, NPCs
systems/      → subsistemas reutilizáveis: karma, tilemap, HUD, diálogo
art/          → arte procedural: sprites, tiles, efeitos
content/      → dados puros em JSON: diálogos, mapas futuros
scenes/       → composição: orquestra todos os sistemas
tests/        → testes unitários sem pygame
```

### 13.3 Padrões de design utilizados

| Padrão | Onde é usado | Benefício |
| --- | --- | --- |
| Scene Stack | `core/scene_manager.py` | Gerencia transições e pausa sem perder estado |
| Event Bus | `core/event_bus.py` | Sistemas se comunicam sem acoplamento direto |
| Input Abstraction | `core/input_manager.py` | Player não conhece teclas específicas |
| State Machine | `gameplay/player/states.py` | Estados de player type-safe com transições validadas |
| Data Loader | `systems/dialogue_loader.py` | Conteúdo separado de lógica |
| Shim / Backward Compat | `entities/*.py` | Refatoração incremental sem quebrar nada |

### 13.4 Pipeline de render

```
Superfície interna (640×360)
  └── upscale 2× → Janela (1280×720)
```

Todo o render acontece na superfície interna em resolução de pixel art. O upscale é feito ao final de cada frame com `pygame.transform.scale()`.

### 13.5 Performance

- **60 FPS** com cap via `pygame.time.Clock`
- **Culling de tiles:** apenas tiles visíveis na câmera são renderizados
- **Cache de tiles:** cada tile é gerado uma vez e cacheado em dicionário
- **Culling de entidades:** NPCs e inimigos fora do rect visível pulam o draw

---

## 14. Requisitos e Ferramentas

### 14.1 Requisitos do jogador

| Requisito | Mínimo |
| --- | --- |
| Sistema Operacional | Windows 10 / Ubuntu 20.04 / macOS 12 |
| Python | 3.9+ |
| RAM | 256 MB |
| GPU | Qualquer (render por CPU via pygame) |
| Armazenamento | < 5 MB |

### 14.2 Instalação e execução

```bash
# 1. Instalar dependência
pip install pygame>=2.1.0

# 2. Executar
python main.py
```

### 14.3 Ferramentas de desenvolvimento

| Ferramenta | Uso |
| --- | --- |
| Python 3.9+ | Linguagem principal |
| Pygame 2.1+ | Engine de render e input |
| pytest | Testes unitários (karma, estados, eventos) |
| VS Code | Editor com extensão Python |
| Git | Controle de versão |

---

## 15. Escopo e Roadmap

### 15.1 Escopo atual (versão MVP)

- [x] Engine: loop, cenas, câmera, event bus, input manager
- [x] Tela de título com pixel art da pedra
- [x] Ato 1 — Vila com NPCs, diálogos e parallax
- [x] Ato 2 — Trilha noturna com morcegos e altares
- [x] Ato 3 — Caverna com boss (GuardianStatue)
- [x] Sistema de karma silencioso com 3 finais
- [x] HUD com corações e partículas
- [x] Efeitos de tela (fade, flash, camera shake)
- [x] Arte procedural completa (sprites, tiles, efeitos)
- [x] Diálogos carregados de JSON
- [x] Testes unitários para sistemas core

### 15.2 Próximas versões

**v1.1 — Conteúdo**
- [ ] Cena de final com texto e arte dedicada (3 variações)
- [ ] Cena de créditos
- [ ] Mais NPCs e diálogos na vila

**v1.2 — Polimento**
- [ ] Música e efeitos sonoros
- [ ] Animações de morte de inimigos mais elaboradas
- [ ] Save system (salvar progresso de karma entre sessões)
- [ ] Menu de pausa com opções

**v2.0 — Expansão**
- [ ] Ato 4 — O coração da pedra (cena de final interativa)
- [ ] Sistema de puzzle nos altares (além de apenas ativar)
- [ ] Loja do comerciante (itens que impactam gameplay e karma)
- [ ] Mapa de mundo entre atos

### 15.3 Cronograma estimado

| Fase | Conteúdo | Duração estimada |
| --- | --- | --- |
| Alpha | Engine + Atos 1-3 (atual) | Concluído |
| Beta | Finais + som + polish | 3 semanas |
| Release v1.0 | Build estável completa | 1 semana |
| v1.1 | Conteúdo extra | 2 semanas |

---

## 16. Referências e Inspirações

### Jogos referência

| Jogo | O que inspirou |
| --- | --- |
| **Celeste** | Precisão de plataforma, coyote time, narrativa emocional |
| **Undertale** | Moral implícita, personagens memoráveis, múltiplos finais |
| **Hollow Knight** | Atmosfera, lore distribuído no cenário, pixel art |
| **Ori and the Blind Forest** | Beleza visual 2D, narrativa sem palavras |
| **Gris** | Metáfora visual como narrativa, identidade cultural |

### Referências culturais

| Referência | Relevância |
| --- | --- |
| **Pedra do Castelo (Castelo do Piauí)** | Formação geológica real que inspirou a pedra do jogo |
| **Cordel nordestino** | Estrutura narrativa oral, moralidade implícita |
| **Folclore do sertão** | Lendas de lugares ancestrais, espíritos guardiões |
| **Obra de Ariano Suassuna** | Estética, personagens e filosofia do sertão |
| **Cinema de Glauber Rocha** | Misticismo e realidade no sertão como tema dramático |

### Referências técnicas

| Referência | Uso |
| --- | --- |
| Pygame documentation | API de render, input, mixer |
| "Game Programming Patterns" (Nystrom) | Scene Manager, Event Bus, State Machine |
| "The Art of Game Design" (Schell) | Pilares de design, karma silencioso |

---

*Documento elaborado para o projeto acadêmico "A Pedra dos Ancestrais".*
*Versão do documento: 1.0*
*Última atualização: Abril de 2026*
