# Game Design Document — v4.0

## A Pedra dos Ancestrais

> **Nota:** Este documento descreve o estado real e completo do jogo na versão 4 (v4_final). Cada valor, mecânica e comportamento descrito aqui está implementado e testado no código. Nenhum elemento é especulativo.

---

| **Campo** | **Informação** |
|---|---|
| Título | A Pedra dos Ancestrais |
| Versão do build | v4_final |
| Gênero | Plataforma 2D com narrativa e elementos de RPG leve |
| Plataforma | PC — Windows / Linux / macOS |
| Engine | Python 3.9+ + Pygame 2.1+ |
| Arte | 100% procedural — zero assets externos |
| Público-alvo | 12+ anos |
| Modo | Single-player |
| Duração média | 30–40 minutos por run |
| Classificação | Livre (sem violência explícita) |
| Execução | `pip install pygame>=2.1` → `python main.py` |

---

## Sumário

1. Visão Geral e Conceito
2. Narrativa e Lore
3. Personagens
4. Mecânicas de Gameplay
5. Sistema de Karma
6. Design das Cenas
7. Inimigos e Boss
8. Puzzles
9. Interface e UX
10. Direção de Arte
11. Arquitetura Técnica
12. Fluxo do Jogo e Finais
13. Estrutura de Arquivos
14. Requisitos e Execução

---

## 1. Visão Geral e Conceito

**A Pedra dos Ancestrais** é um jogo 2D de plataforma com narrativa ambientado no sertão nordestino do Piauí, inspirado na formação geológica real conhecida como **Pedra do Castelo** (município de Castelo do Piauí). O jogador controla **Caio**, um jovem guiado pelo vento até uma pedra ancestral e misteriosa.

### Diferencial central

A maioria dos jogos de narrativa usa menus de escolha para definir moralidade. Em A Pedra dos Ancestrais, **a moral é rastreada de forma completamente silenciosa**: o jogo observa comportamentos naturais (com quem Caio conversa, o que ele quebra, quem ele ajuda, o que ele promete) e calcula o desfecho sem jamais revelar que está fazendo isso. Não há barra de karma, não há indicador, não há aviso.

### O Sinal — fio condutor narrativo

Há um elemento que conecta todos os sistemas do jogo: **o Sinal**. É uma marca invisível que a Pedra coloca em quem ela chama. Caio foi chamado não por ser especial, mas porque a Pedra precisa de alguém que a ouça. Cada elemento do jogo se conecta a isso:

- Seu Zequinha reconhece o Sinal (ele mesmo o carregou décadas atrás) — por isso avisa e some
- Os altares confirmam o Sinal a cada ativação (as partículas âmbar são a Pedra reconhecendo Caio)
- Iracema reconhece o Sinal e propõe o trato com base nele
- O Guardião confirma: *"Você tem o sinal. Pode passar."*
- O que Caio fez com o Sinal define qual dos três finais é revelado

### Pilares de design

| **Pilar** | **Implementação real** |
|---|---|
| Exploração com propósito | Cada NPC, objeto e registro existe por razão narrativa; interagir recompensa lore |
| Plataforma acessível | Coyote time (8 frames), jump buffer (6 frames), colisão AABB em dois eixos separados |
| Moral implícita | Sistema de karma silencioso via Event Bus; zero feedback visual ao jogador |
| Identidade cultural | Sertão piauiense, Tapuias do Alto, cordel, Pedra do Castelo real |
| UX premium | Tela de morte com overlay gradual, pausa com painel, prompts animados, label de ato |

---

## 2. Narrativa e Lore

### 2.1 Premissa

Caio é um rapaz de uma vila do sertão piauiense. Numa manhã de vento forte, sente um chamado vindo da Pedra do Castelo, formação rochosa que existe nos arredores desde antes de qualquer memória viva. Os moradores têm histórias: uns dizem que guarda um tesouro, outros que guarda um segredo, e os mais velhos dizem que a pedra cobra um preço. Caio parte.

### 2.2 O que a Pedra realmente é

A Pedra do Castelo não é apenas uma formação geológica. Ela é um **repositório vivo de memória coletiva**, construído pelos **Tapuias do Alto** — uma civilização ancestral pré-colonial que percebeu que suas histórias se perderiam. Seus pajés condensaram a memória de gerações em cristais âmbar e os depositaram no coração da Pedra, junto a um guardião animado por esse espírito coletivo.

O problema: a memória tem peso. Ao longo dos séculos, a energia acumulada começou a transbordar. Os morcegos corrompidos são a manifestação física desse transbordamento — exatamente como Zinha descreve sem saber: *"os sonhos que a pedra não quer mais."*

A Pedra precisa de alguém que entre, prove ser digno (derrotando o Guardião), e **carregue a memória para fora** — não como tesouro, mas como responsabilidade.

### 2.3 Personagens históricos

**Iracema** foi a última pajé Tapuia, que voluntariamente se tornou espírito ao morrer para permanecer dentro da Pedra como guardiã da memória. Ela existe há séculos, sozinha, esperando alguém digno do Sinal.

**Seu Zequinha** foi chamado pela Pedra quarenta anos atrás, quando jovem. Entrou, passou no teste, recebeu a memória. Passou décadas carregando esse conhecimento sozinho, sem contar a ninguém. Quando Caio aparece, Zequinha reconhece o Sinal e pode finalmente descansar — por isso desaparece.

### 2.4 Lore distribuída — mapa completo

A lore nunca é narrada diretamente. É distribuída em camadas, cada uma opcionalmente acessível:

| **Fonte** | **Conteúdo revelado** | **Gatilho** |
|---|---|---|
| Aldeão 0 | "O vento tá esquisito… parece que a Pedra tá chamando." | Conversar |
| Aldeão 1 | Seu Zequinha saiu à noite — nunca é boa ideia | Conversar |
| Aldeão 2 | "Quem entra naquela pedra nunca volta do mesmo jeito." | Conversar |
| Comerciante | Três homens foram; um voltou rico, um louco, um não voltou | Conversar |
| Seu Zequinha | O Sinal existe; o tesouro cobra preço; cuide das pessoas | Conversar (uma vez) |
| Zinha | Os morcegos são "os sonhos que a pedra não quer mais" | Ser ajudada |
| Altar A (Trilha) | Silhuetas gravando símbolos — os Tapuias preservavam tudo | Ativar |
| Altar B (Trilha) | Uma família na seca — por que decidiram preservar | Ativar |
| Altar C (Trilha) | Pajés depositando cristais âmbar no coração da Pedra | Ativar |
| Registro 1 (Caverna) | Símbolo dos Tapuias do Alto — círculo com cruz | Interagir [X] |
| Registro 2 (Caverna) | 37 gerações; cada entalhe, um nome | Interagir [X] |
| Registro 3 (Caverna) | Rosto de Iracema jovem — ela escolheu ficar | Interagir [X] |
| Iracema (diálogo) | Natureza da dívida e da memória; o trato | Automático (col. 30) |
| Guardião (derrota) | "Você tem o sinal. Pode passar. Mas devia voltar." | Derrotar |
| Câmara final | Rostos, nomes, histórias dos Tapuias do Alto | Chegar lá |

Registros adicionais distribuídos pela **Floresta** (`registro_floresta_0`, `registro_floresta_1`) e pelas **Ruínas** (`registro_ruinas_0`, `registro_ruinas_1`) aprofundam o lore dos Tapuias para jogadores que exploram essas áreas.

### 2.5 Os três finais

#### Final Verdadeiro — "O Tesouro Não é Ouro"

**Condição exata (código):** `coragem >= 2` E `sabedoria >= 2` E `ganancia <= 1`

**Sequência de cenas (6 steps):**

1. A câmara do coração se abre — rostos e histórias gravadas na rocha (120 frames)
2. Partículas de memória flutuam em direção a Caio — ele as recebe (150 frames)
3. Iracema se despede: *"Os que viveram aqui precisavam que alguém lembrasse. Você lembra agora."* (180 frames)
4. Amanhecer. Caio desce a trilha (120 frames)
5. Zinha corre em direção a Caio; ele se ajoelha para falar com ela. Fade antes da resposta. (180 frames)
6. Preto (80 frames) → Créditos

**Significado:** O tesouro é memória, não ouro. Caio sai inteiro. A última imagem — ajoelhar para a criança — é o final em si.

#### Final Neutro — "Quem Entra, Muda"

**Condição exata:** Qualquer combinação que não seja ruim nem verdadeiro (ganância < 3, mas falta coragem ou sabedoria)

**Sequência (5 steps):**

1. Câmara quase vazia — um único cristal fraco pulsando (120 frames)
2. Iracema distante: *"O tesouro só aparece pra quem realmente procura."* (150 frames)
3. Entardecer. Caio desce a trilha, confuso mas vivo (120 frames)
4. Caio parado na beira da vila, de costas, olhando o horizonte (180 frames)
5. Preto → Créditos

**Significado:** Caio procurou algo mas ainda não sabe o quê. A ambiguidade é total.

#### Final Ruim — "A Ganância Cobra Juros"

**Condição exata:** `ganancia >= 3`

**Sequência (6 steps):**

1. Câmara cheia de ouro e joias (120 frames)
2. Ao tocar, tudo escurece e petrifica (100 frames)
3. Iracema fria: *"Você encontrou o que procurava."* — sem mais nada (120 frames)
4. As paredes se fecham. Corra. (sequência de fuga, 100 frames)
5. Caio sai. A poeira escura não sai das suas mãos (150 frames)
6. Preto → Créditos

**Nota de design:** O Final Ruim não mata Caio. A punição é carregar algo que não se limpa — uma mancha que só ele vê. O final verdadeiramente ruim não é dramático; é sutil e perturbador.

---

## 3. Personagens

### 3.1 Caio — Protagonista

| **Atributo** | **Valor** |
|---|---|
| Sprite | 24×42 pixels, pixel art procedural |
| HP inicial | 3 corações |
| HP máximo | 3 corações |
| Hitbox de colisão | 12×28 pixels |
| Frames de animação | 0=idle, 1=walkA, 2=walkB, 3=jump/fall, 4=attack, 5=crouch |
| Velocidade | 2.5 px/frame |
| Força de pulo | -8.0 px/frame (impulso inicial) |
| Ciclo de animação de caminhada | `[1, 0, 2, 0]`, troca a cada 8 ticks |

Caio não fala. Sua personalidade é definida inteiramente pelas ações do jogador. O chapéu de couro é elemento visual permanente; nas cenas de final, ele se ajoelha (frame 5/crouch) diante de momentos importantes.

**Animações implementadas:**

- **Idle:** respira (+1px a cada 30 frames)
- **Walk:** ciclo `[1, 0, 2, 0]`, troca a cada 8 ticks (`ANIM_SPEED = 8`)
- **Jump/Fall:** frame 3 (braços levemente levantados)
- **Attack:** frame 4 (braço direito estendido com hitbox ativo nos frames 4–12)
- **Hurt:** flash de iframe (pisca a cada 4 frames durante 60 frames de invencibilidade)
- **Dead:** frame 3 estático, sem movimento

### 3.2 Aldeão 0 — "O Vigilante"

Silhueta distinta: **alto e magro, braços cruzados no peito, chapéu de palha de aba dupla da largura do sprite**. Camisa azul-marinho. Expressão séria. Patrulha 30px em torno da posição inicial. Diálogo: observação sobre o vento e o chamado da Pedra.

### 3.3 Aldeão 1 — "A Mãezinha"

Silhueta distinta: **baixa e larga, vestido em A-line (alarga para baixo), lenço vermelho vivo na cabeça, cesto no braço direito**. Bochechas rosadas, sorriso. Posição fixa. Diálogo: observação sobre Seu Zequinha ter saído à noite.

### 3.4 Aldeão 2 — "O Velho Quieto"

Silhueta distinta: **corpo curvado para frente, barba rala branca, calça com remendos de cor diferente, bengala grossa e rústica**. Não balança (velho cansado). Posição fixa. Diálogo: sobre quem entra na Pedra nunca voltar do mesmo jeito.

### 3.5 Seu Zequinha — Ancião Misterioso

Silhueta distinta: **robe terroso-escuro longo, cabelos brancos compridos nas laterais (até os ombros), chapéu pontudo, bengala ornamentada com pomo brilhante**. Sprite 24×46 pixels. Posição fixa no col. 30 da Vila. Não patrulha.

**Comportamento único:** Após o diálogo (uma única vez, `_talked = True`), inicia countdown de 90 frames. Ao atingir zero, chama `self.hide()` e publica `system_message`: `"...Zequinha sumiu."` A bengala permanece visível no mapa como objeto.

**Diálogo completo (6 linhas):**

1. "A pedra chama… mas só entra quem está destinado."
2. "Se um dia você encontrar o símbolo, saiba:"
3. "o tesouro não alimenta o corpo."
4. "Ele alimenta o que você mais deseja — e cobra o preço mais alto."
5. "Cuide das pessoas no caminho, menino."
6. "A pedra vê tudo que você faz antes de chegar nela."

As linhas 5 e 6 são a instrução direta do sistema de karma, dita em voz alta sem que o jogador reconheça como tal.

### 3.6 Zinha — A Criança

Silhueta distinta: **minúscula (18×28 pixels), laço rosa gigante no cabelo, olhos grandes e azuis (íris azul visível), vestido amarelo-vivo com bolinhas, expressão de susto**.

**Mecânica única:** Zinha está presa em cima de uma caixa instável (20×20 pixels) apoiada por dois suportes (4×16 pixels cada). A caixa treme a cada 180 frames (camera shake leve). O jogador pode:

- **Atacar os suportes** com Z: cada suporte tem 2 HP. Ao destruir ambos, a caixa desce gradualmente (aceleração de 0.1 px/frame, máximo 2.0 px/frame). Ao chegar ao chão: publica `zinha_helped`, exibe diálogo, Zinha fala sobre os morcegos.
- **Ignorar:** Após 600 frames sem intervenção, a caixa desce sozinha. Publica `zinha_ignored`. Zinha não fala. Nenhuma notificação.

O jogador nunca é avisado que há karma em jogo. Zinha reaparece nas cenas de final — correndo até Caio no Final Verdadeiro, imóvel nos demais.

### 3.7 Comerciante

Silhueta distinta: **gordo, baixo, bigodão espesso de 3 linhas, avental branco com dois bolsos salientes, bochechas rosadas**. Posição fixa no col. 45. Diálogo: os três homens que foram à Pedra (um rico, um louco, um não voltou).

### 3.8 Iracema — Espírito

Não tem sprite fixo. É representada por uma silhueta humana feminina gerada por partículas azuis (`SPIRIT_BLUE = (80, 160, 220)`) com forma reconhecível: cabeça oval, ombros, tronco, mãos estendidas, saia flutuante. A cada frame, ~22% das partículas não aparecem (dispersão), criando o efeito etéreo.

**Estados:** `idle → talking → choosing → done`

No estado `choosing`, dois altares físicos aparecem à esquerda (SIM, âmbar) e à direita (NÃO, vermelho-escuro) de Iracema. O jogador se move até um e pressiona X. Sem menu. Sem texto de escolha. Apenas posicionamento e ação.

O trato possui três desfechos registrados pelo karma:

- `aceitou_trato_honrou()` — jogador aceita e cumpre a promessa
- `aceitou_trato_traiu()` — jogador aceita mas age contrariamente
- `recusou_trato()` — jogador recusa ou ignora (timeout 30 segundos)

---

## 4. Mecânicas de Gameplay

### 4.1 Física do Player

Todas as constantes estão em `config/physics.py` e são aplicadas por frame (60 FPS):

| **Constante** | **Valor** | **Efeito** |
|---|---|---|
| `PLAYER_SPEED` | 2.5 px/frame | Velocidade horizontal |
| `PLAYER_JUMP_FORCE` | -8.0 px/frame | Impulso vertical inicial |
| `PLAYER_GRAVITY` | +0.4 px/frame² | Aceleração gravitacional |
| `PLAYER_MAX_FALL` | 10.0 px/frame | Velocidade máxima de queda |
| `COYOTE_FRAMES` | 8 | Frames de graça após sair de plataforma |
| `JUMP_BUFFER_FRAMES` | 6 | Frames de antecipação do pulo |
| `TILE_SIZE` | 16 px | Tamanho de cada tile |

**Coyote time:** Ao sair de uma plataforma com `vy > 0` (caindo), o sistema concede 8 frames durante os quais o pulo ainda é aceito. Elimina a frustração de pulos perdidos por milissegundos.

**Jump buffer:** Se o jogador pressionar pulo até 6 frames antes de tocar o chão, o pulo é executado imediatamente ao aterrissar. Torna o controle mais responsivo em sequências rápidas.

**Colisão AABB em dois eixos separados:**

1. Aplica `vx`, resolve colisões horizontais
2. Aplica `vy`, resolve colisões verticais (detecta `on_ground`, `vy = 0`)

Isso garante que colisões de canto se resolvam de forma previsível e sem travamentos.

**Hitbox vs. sprite:** O hitbox de colisão (12×28 pixels) é menor que o sprite (24×42 pixels). O jogador cabe em espaços ligeiramente menores que sua aparência sugere — decisão de design deliberada para reduzir frustração.

**Queda fora do mundo:** Se `player.y > tilemap.height + 40`, aplica 1 dano e reposiciona na coordenada y=0 (topo). Evita quedas infinitas.

### 4.2 Controles

| **Tecla** | **Ação** |
|---|---|
| `A` / `←` | Mover esquerda |
| `D` / `→` | Mover direita |
| `W` / `↑` / `Espaço` | Pular |
| `Z` ou `J` | Atacar (golpe) |
| `X` ou `K` | Interagir / ativar / escolher |
| `ESC` | Pausar |
| `ENTER` / `Espaço` | Confirmar (menus, diálogo) |
| `M` | Menu principal (durante pausa) |

O mapeamento é centralizado no `InputManager` (`core/input_manager.py`) via `DEFAULT_BINDINGS`. Alterar qualquer tecla exige editar apenas esse arquivo.

**Dataclass `InputState`:** campos booleanos `move_left`, `move_right`, `jump`, `attack`, `interact`, `pause` — retornados por `InputManager.poll()` a cada frame.

### 4.3 Combate

**Ataque de Caio:**

| **Parâmetro** | **Valor** |
|---|---|
| Hitbox do ataque | 20×16 pixels |
| Direção | Para onde Caio está olhando |
| Frame de início (ativo) | Frame 4 da animação |
| Frame de fim (ativo) | Frame 12 da animação |
| Duração total | 16 frames |
| Cooldown | 24 frames (~0.4s) |

O hitbox só existe durante os frames 4–12 da animação. Fora dessa janela, o ataque não detecta colisão.

**Dano recebido por Caio:**

| **Parâmetro** | **Valor** |
|---|---|
| Dano por hit | 1 coração |
| Knockback vertical | -4.0 px/frame (pulo pequeno) |
| iFrames | 60 frames de invencibilidade (`IFRAMES = 60`) |
| Estado HURT | 20 frames sem controle horizontal |
| Morte | HP = 0 → estado DEAD |

**iFrames:** Durante os 60 frames de invencibilidade, Caio pisca a cada 4 frames (alterna visível/invisível). Nenhum dano é aplicado nesse período, mesmo que o inimigo toque Caio continuamente. Partículas de dano (`emit_damage()`) são emitidas — 5 partículas vermelhas.

**Morte:** Estado DEAD bloqueia todo input. O HUD inicia overlay de morte gradual. Após o overlay escurecer (40 frames), aparece "Caio caiu." e "Mas a pedra espera." Após 110 frames totais, os botões de reinício aparecem.

### 4.4 Máquina de Estados do Player

Os estados do player são gerenciados por `PlayerState` (`gameplay/player/states.py`) com transições validadas:

| **Estado** | **Transições válidas** |
|---|---|
| `IDLE` | WALKING, JUMPING, FALLING, ATTACKING, HURT, DEAD |
| `WALKING` | IDLE, JUMPING, FALLING, ATTACKING, HURT, DEAD |
| `JUMPING` | FALLING, HURT, DEAD, ATTACKING |
| `FALLING` | IDLE, WALKING, HURT, DEAD |
| `ATTACKING` | IDLE, HURT, DEAD |
| `HURT` | IDLE, DEAD |
| `DEAD` | *(terminal — sem transições)* |

DEAD é estado terminal: nenhum input é processado após atingi-lo.

### 4.5 Interação com Objetos

Caio pode interagir com qualquer objeto dentro de `INTERACT_RADIUS = 40 pixels`. O sistema verifica `interact_rect` (inflate do hitbox padrão) do objeto contra o rect do player.

**Prompt:** O HUD exibe o texto correspondente com animação de pulso senoidal. O texto varia por tipo:

| **Objeto** | **Prompt exibido** |
|---|---|
| NPCs (conversar) | `[X] conversar` |
| Relíquias âmbar | `[X] observar` |
| Altares (inativos) | `[X] ativar altar` |
| Altares (ativos) | `Altar ativo ✓` |
| Cristais (puzzle) | `[X] girar cristal` |
| Tocha (puzzle) | `[X] tocha` |
| Registros | `[X] ler registro` |

**Nota de design crítica:** Relíquias âmbar exibem `[X] observar` — não `[X] quebrar`. Pressionar X apenas emite partículas sem consequência. A destruição só ocorre com o ataque Z. Quem quebra relíquias sem prestar atenção está demonstrando exatamente o comportamento que o karma rastreia.

### 4.6 Altares

Três altares na Trilha, acessíveis com X quando próximo. Ao ativar:

1. Emite 1 partícula âmbar (`emit_altar()`) continuamente
2. Publica `altar_activated` com índice e texto do fragmento de lore
3. O fragmento é exibido no topo da tela por 200 frames (fade in/out suave)
4. Após 3 altares ativados: publica mensagem "O portal se abre…" e abre o portal da Caverna

Os altares ficam permanentemente ativos após a ativação (chama animada visível).

---

## 5. Sistema de Karma

O sistema é completamente invisível para o jogador. Nenhuma barra, nenhum indicador, nenhuma mensagem sobre karma é exibida em momento algum.

### 5.1 Atributos

| **Atributo** | **Tipo** | **Faixa** | **Persiste entre mortes?** |
|---|---|---|---|
| `coragem` | int | 0–5 | Sim |
| `ganancia` | int | 0–5 | Sim |
| `sabedoria` | int | 0–5 | Sim |
| `divida_iracema` | bool/None | honrou / traiu / recusou | Sim |

O karma é uma instância gerenciada pelo `KarmaSystem` (`systems/karma.py`). Ao morrer, o jogador reinicia o ato mas o karma acumulado é preservado. Ao ir para o Menu Principal (M na pausa), o karma é resetado (nova partida).

### 5.2 Mapa completo de ações e efeitos

| **Ação do jogador** | **Evento publicado** | **Coragem** | **Ganância** | **Sabedoria** |
|---|---|---|---|---|
| Conversar com qualquer NPC (1ª vez) | `DIALOGUE_CLOSED` | — | — | +1 |
| Ajudar Zinha (suportes destruídos) | `zinha_helped` | +1 | — | +1 |
| Ignorar Zinha (600 frames sem agir) | `zinha_ignored` | -1 | — | — |
| Quebrar pote comum (ataque Z) | `POT_BROKEN` | — | +1 | — |
| Pegar item armadilha (ataque Z em relíquia) | `ITEM_COLLECTED` (is_trap=True) | — | +1 | — |
| Ler registro ancestral | — | — | — | +1 |
| Resolver puzzle perfeitamente | — | — | — | +1 |
| Derrotar o Guardião (ajudou o espírito) | `BOSS_DEFEATED` | +1 | — | — |
| Matar qualquer inimigo | `ENEMY_KILLED` | +1 | — | — |
| Aceitar trato de Iracema e honrar | — | — | — | divida=honrou |
| Aceitar trato de Iracema e trair | — | — | — | divida=traiu |
| Recusar trato (ou timeout 30s) | — | — | — | divida=recusou |

**Máximos teóricos:** coragem ≤ 5 (cap), sabedoria ≤ 5 (cap), ganância ≤ 5 (cap). A função interna aplica `max(0, min(5, v))` em toda operação.

### 5.3 Cálculo do final

```python
@property
def final_type(self) -> str:
    if self.ganancia >= 3:
        return "ruim"
    elif self.coragem >= 2 and self.sabedoria >= 2 and self.ganancia <= 1:
        return "verdadeiro"
    else:
        return "neutro"
```

**Análise dos casos limítrofes:**

| **Comportamento** | **Coragem** | **Sabedoria** | **Ganância** | **Final** |
|---|---|---|---|---|
| Explorou tudo, matou inimigos, leu registros | ≥2 | ≥2 | ≤1 | Verdadeiro |
| Conversou com todos, recusou Iracema | ≥2 | ≥2 | ≤1 | Verdadeiro |
| Só lutou, não explorou | ≥2 | <2 | 0 | Neutro |
| Quebrou 3+ potes/relíquias | — | — | ≥3 | Ruim |
| Ganância=2, mas sem sabedoria | — | <2 | 2 | Neutro |
| Indiferente (nenhuma ação especial) | 0 | 0 | 0 | Neutro |

### 5.4 Progresso narrativo (JourneySummary)

Além das três dimensões de karma, o sistema registra o **progresso narrativo** do jogador:

```python
@dataclass
class JourneySummary:
    village_talks: int        # Conversas na Vila
    forest_records: int       # Registros lidos na Floresta
    ruins_seals: int          # Selos das Ruínas
    ruins_records: int        # Registros lidos nas Ruínas
    trail_altars: int         # Altares ativados na Trilha
    trail_records: int        # Registros lidos na Trilha
    cave_records: int         # Registros lidos na Caverna
    rewards: int              # Itens coletados
    guardian_freed: bool      # Guardião derrotado
    iracema_choice: str       # "honrou" / "traiu" / "recusou"
```

### 5.5 Implementação técnica

O karma se subscreve automaticamente aos eventos do `EventBus`:

- `ENEMY_KILLED` → `enfrentou_inimigo()` → coragem +1
- `POT_BROKEN` → `destruiu_pote_decorativo()` → ganância +1
- `DIALOGUE_CLOSED` → `conversou_com_npc()` → sabedoria +1
- `ITEM_COLLECTED` (is_trap=True) → `pegou_item_armadilha()` → ganância +1

Nunca é chamado diretamente por nenhuma cena. Quando `SceneManager.replace()` é chamado, ele executa `bus.clear()` (limpa todos os listeners) e o karma se re-subscreve via injeção de dependência na próxima cena. Isso garante que nenhum listener se acumule entre reinícios.

---

## 6. Design das Cenas

### 6.1 Tela de Título (IntroScene)

**Atmosfera:** Crepúsculo no sertão. Gradiente de céu roxo-vermelho-laranja. Lua cheia. Estrelas fixas (seed 99999).

**Elemento oculto:** Um único pixel âmbar pisca **uma única vez** nos frames 60–80 da cena, antes de qualquer input. É a Pedra sinalizando que já está ativa. Quem perceber compreenderá retroativamente.

**Elementos visuais:**
- Partículas de poeira sobem lentamente (emissão via `emit_altar()` a cada 8 frames)
- Pedra do Castelo desenhada em pixel art procedural (3 colunas de alturas diferentes, janelas com brilho âmbar interno, rachaduras verticais)
- Texto "A PEDRA DOS ANCESTRAIS" com sombra dourada
- Subtítulo "Uma lenda do Piauí" em tom suave
- "Pressione ENTER para começar" — pisca a cada 40 frames, aparece após 60 frames

**Dica de controles:** Após 300 frames (5 segundos), aparece com fade gradual:
- "A/D Mover  W/Espaço Pular"
- "Z Atacar  X Interagir  ESC Pausar"

**Transição:** Fade out ao pressionar ENTER ou X → VillageScene.

### 6.2 Ato 1 — A Vila (VillageScene)

**Label no HUD:** "Ato 1 — A Vila"

**Dimensões:** 60 colunas × 22 linhas = 960 × 352 pixels de mundo

**Hora do dia:** Manhã cedo. Gradiente de céu laranja-vermelho. Sol com raios no canto superior.

**Parallax (5 camadas):**

| **Camada** | **Fator** | **Conteúdo** |
|---|---|---|
| 0 | 0.05× | Gradiente de céu |
| 1 | 0.05× | Sol com raios + Pedra do Castelo pequena |
| 2 | 0.15× | Pedra do Castelo média |
| 3 | 0.30× | Silhueta de montanhas |
| 4 | 0.55× | Colinas de solo |

**Mapa — layout:**
- Chão principal: linha 14 (STONE_TOP) + linhas 15–21 (STONE_MID)
- 5 plataformas flutuantes: cols 5–10 (row 10), 14–18 (row 11), 24–30 (row 10), 35–39 (row 9), 46–51 (row 11)
- Cactos decorativos: cols 3, 12, 20, 33, 52 (linha 13, sem colisão real)
- 5 potes comuns: cols 8, 18, 28, 40, 50
- 2 relíquias âmbar: cols 11, 38

**NPCs e posições:**

| **Personagem** | **Col.** | **Patrulha** | **Karma ao conversar** |
|---|---|---|---|
| Aldeão 0 (vigilante) | 7 | 30px | +1 sabedoria |
| Aldeão 1 (mãezinha) | 21 | Parado | +1 sabedoria |
| Seu Zequinha | 30 | Parado | +1 sabedoria |
| Aldeão 2 (velho) | 37 | Parado | +1 sabedoria |
| Comerciante | 45 | Parado | +1 sabedoria |
| Zinha | 15 | Presa na caixa | +1 coragem +1 sab (se ajudada) |

**Bengala de Zequinha:** Após Zequinha sumir, uma bengala e um trapo vermelho (cor da camisa de Caio) ficam visíveis na col. 32 do mapa — permanentes até o fim da sessão.

**Saída:** Col. 57. Fade out → TrailScene. Protegida por flag `_exiting` para não disparar duas vezes.

**Morte:** Publica `PLAYER_DIED` → HUD exibe tela de morte. Aguarda ENTER (reinicia ato) ou ESC (vai para menu).

### 6.3 Ato 2 — A Trilha (TrailScene)

**Label no HUD:** "Ato 2 — A Trilha"

**Dimensões:** 70 colunas × 22 linhas = 1120 × 352 pixels de mundo

**Hora do dia:** Noite. Lua cheia com halo. Estrelas com seed aleatória por sessão (seed muda a cada run, diferente da Vila).

**Estrutura de escalada:** O mapa é construído como degraus que sobem da esquerda para a direita — o jogador literalmente sobe a montanha. 6 segmentos de escalada mais plataformas de castelo (PEDRA_CASTELO) intercaladas.

**Altares (3):**

| **Altar** | **Col.** | **Linha** | **Fragmento de lore** |
|---|---|---|---|
| A | 20 | FLOOR-2 | Silhuetas gravando símbolos — os Tapuias preservavam tudo |
| B | 38 | FLOOR-5 | Uma família na seca — por que preservar |
| C | 55 | FLOOR-7 | Pajés depositando cristais âmbar |

**Inimigos:**

| **Inimigo** | **Col.** | **Linha** | **Tipo** |
|---|---|---|---|
| BatEnemy 1 | 12 | 10 | Normal |
| BatEnemy 2 | 22 | 9 | Normal |
| BatEnemy 3 | 31 | 8 | Normal |

**Portal:** Visível apenas quando os 3 altares estão ativos. Antes: parede sólida (cols 68–69, todas as linhas). Depois: animação de onda senoidal azul (`SPIRIT_BLUE`), com legenda "→ Caverna".

**Relíquia e potes:**
- 1 relíquia âmbar: col. 17, linha FLOOR-1
- 2 potes comuns: cols 6 e 10, linha FLOOR

**Tochas:** Posicionadas nos cols 10, 22, 34, 46, 58 com chama animada e halo âmbar. Criadas via `math.sin()` no draw.

**Contador de altares:** Exibido no canto superior esquerdo (`Altares: 0/3`). Muda de cor âmbar-escuro para âmbar-claro ao completar.

### 6.4 Ato 3 — A Caverna (CaveScene)

**Label no HUD:** "Ato 3 — A Caverna"

**Dimensões:** 60 colunas × 22 linhas = 960 × 352 pixels de mundo

**Teto:** Linhas 0–3 = ROCHA_CAVE, linha 4 = CAVE_TOP
**Chão:** Linha 18 = CAVE_TOP, linhas 19–21 = ROCHA_CAVE

**Plataformas internas (6 grupos):**

| **Col** | **Linha** | **Tipo** | **Comprimento** |
|---|---|---|---|
| 8 | 13 | CRISTAL | 6 |
| 18 | 11 | ROCK_GLOW | 5 |
| 26 | 13 | CRISTAL | 4 |
| 36 | 12 | ROCK_GLOW | 5 |
| 44 | 13 | CRISTAL | 5 |
| 52 | 11 | ROCK_GLOW | 5 |

**Progressão da caverna:**

```
Col 0–10:   Entrada + corredor + BatEnemy 1 (faster)
Col 10–20:  Plataformas médias + Registros 1 e 2
Col 20–28:  BatEnemy 2 e 3 (faster) em patrulha apertada
Col 28–35:  Puzzle 1 (cristais) na col 39
Col 30+:    Trigger de Iracema (automático)
Col 35:     Iracema + altares do trato
Col 42–48:  Puzzle 2 (sombras/tocha) na col 43
Col 25+:    Trigger do Guardião
Col 31:     Guardião Estátua (boss)
Col 55:     Registro 3
Col 57+:    Câmara do coração (acesso após Guardião derrotado)
```

**Inimigos (todos faster=True):**

| **Inimigo** | **Col** | **Linha** |
|---|---|---|
| BatEnemy 1 | 11 | 8 |
| BatEnemy 2 | 19 | 7 |
| BatEnemy 3 | 28 | 8 |

**Registros ancestrais:**

| **Registro** | **Col** | **Linha** | **Conteúdo** |
|---|---|---|---|
| 1 | 8 | CEIL+1 | Símbolo dos Tapuias do Alto — círculo com cruz |
| 2 | 22 | CEIL+1 | 37 gerações — cada entalhe, um nome |
| 3 | 55 | CEIL+1 | O rosto de Iracema, mais jovem — ela escolheu ficar |

**Câmara final:** Cols 57+, acesso liberado após Guardião derrotado E speech do Guardião concluído. Emite partículas âmbar e exibe gravuras simbólicas nas paredes. Transição para EndingScene usa o karma acumulado para calcular o final.

**Iluminação:** Pools de luz âmbar desenhados a cada 15 colunas via `draw_ambient_light()` com `BLEND_RGBA_ADD`. Cria atmosfera de escuridão profunda com ilhas de luz.

---

## 7. Inimigos e Boss

### 7.1 BatEnemy — Morcego Corrompido

**Lore:** Morcegos infectados pela energia ancestral transbordando da câmara. São "os sonhos que a pedra não quer mais" — memórias negativas solidificadas em criaturas.

**Sprite:** 24×14 pixels. 2 frames de animação (asas abertas / semifechadas), troca a cada 8 ticks. Cor normal: roxo-escuro `(100, 50, 150)`. Olhos: roxo-magenta normal, âmbar `(255, 180, 60)` quando faster.

| **Atributo** | **Normal** | **Faster** |
|---|---|---|
| HP | 2 | 2 |
| Dano | 1 coração | 1 coração |
| Velocidade | 1.5 px/frame | 2.25 px/frame (×1.5) |
| Patrulha | 60px da posição inicial | 60px |
| Oscilação vertical | seno, amplitude 8px, freq 0.04 | amplitude 10px, freq 0.06 |

**IA:** Patrulha horizontal simples com oscilação vertical senoidal (`y = y_base + sin(time * freq) * amplitude`). Inverte direção nos limites. Não persegue o player — apenas patrulha. Isso é intencional: a ameaça não é inteligente, é obstinada.

**Morte:** Emite 6 partículas roxas via `emit_death()`. Publica `ENEMY_KILLED`. Karma +1 coragem.

### 7.2 GuardianStatue — Guardião Estátua (Boss)

**Lore:** Criado pelos pajés Tapuias como último teste. Não age por malícia — age por dever. Ao longo dos séculos, absorveu fragmentos de memória e desenvolveu algo próximo a uma voz. Por isso consegue falar ao ser derrotado.

**Sprite:** 38×52 pixels. Gerado proceduralmente com textura de ruído (seed fixa). Olhos âmbar (fase 1) ou dourados brilhantes (fase 2). Fissura diagonal aparece na fase 2.

**HP total: 14.** Barra de HP segmentada em 14 segmentos, cores diferentes por fase (verde na Fase 1, laranja na Fase 2).

**Trigger:** Ativo quando `player.x > 25 * TILE`. Nos primeiros 80 frames após o trigger, pisca (fase de despertar — `awaken_timer`) — ritual, não aviso. Só recebe dano após acordar completamente.

| **Atributo** | **Fase 1 (HP 14→5)** | **Fase 2 (HP ≤4→0)** |
|---|---|---|
| Velocidade base | 0.6 px/frame | 1.4 px/frame |
| Velocidade de rush | — | 3.5× base (durante 30 frames) |
| Hitbox | 26×44 pixels | 26×44 pixels |
| Dano | knockback | knockback |
| Ondas de choque | Não | A cada 100 frames (`SHOCKWAVE_INTERVAL`) |
| Cor da barra de HP | Verde | Laranja |
| Cooldown do rush | — | 240 frames |

**Movimentação suavizada:** O boss usa `lerp` na velocidade horizontal (`_vel_x`) para movimentação fluida, evitando travamentos bruscos.

**Ondas de choque (Fase 2):**
- Duas ondas simultâneas em direções opostas via `_create_shockwave()`
- Hitbox: 8×6 pixels, velocidade: 3.0 px/frame
- Dura 40 frames por onda
- Causa 1 dano + camera shake ao tocar o player

**Rush (Fase 2):**
- Ativado quando player está a distância > 3 tiles
- Velocidade: 3.5× base por 30 frames
- Cooldown: 240 frames entre rushes

**Derrota e dissolução:**

1. HP → 0: `alive = False`, `_defeat_timer = 0`
2. Delay de 50 frames → diálogo: *"Você tem o sinal. Pode passar. Mas devia voltar."*
3. Dissolução via `emit_boss_death()`: 24 fragmentos âmbar + 16 faíscas, fade de alpha gradual
4. Transição de fase emite `emit_phase_burst()`: 12 partículas de burst
5. Após `dissolve_done()` (180 frames): caminho para câmara final liberado

---

## 8. Puzzles

Ambos os puzzles são **opcionais**. Há caminhos alternativos que contornam cada um, porém mais difíceis. Resolver concede +1 sabedoria cada via `resolveu_puzzle_perfeito()`.

### 8.1 Puzzle 1 — Cristais de Luz

**Localização:** Col. 39 da Caverna, câmara própria.

**Conceito:** 3 cristais posicionados ao redor de um ponto central. Cada cristal emite um feixe de luz na direção de seu ângulo atual. O objetivo é fazer os 3 feixes convergirem no ponto central.

**Mecânica:**
- Pressionar X em um cristal o gira 45° no sentido horário
- O feixe é renderizado como série de pontos âmbar com fade de distância
- Quando os 3 feixes convergem (ângulos solução: 135°, 180°, 225°), o puzzle está resolvido
- Estado inicial dos ângulos: `[45°, 90°, 315°]` — sempre o mesmo

**Feedback de resolução:** 30 partículas âmbar emitidas do ponto central + mensagem "Os feixes convergem…"

**Caminho alternativo:** Plataformas mais difíceis contornam a câmara do puzzle.

### 8.2 Puzzle 2 — Sombras e Plataformas

**Localização:** Col. 43 da Caverna, câmara mais alta que larga.

**Conceito:** Uma tocha interagível alterna quais plataformas existem. Plataformas "de luz" são sólidas quando a tocha está acesa; "de sombra" são sólidas quando apagada. O jogador precisa usar a alternância para subir.

**Mecânica:**
- Pressionar X na tocha: alterna entre `lit = True` e `lit = False`
- Plataformas ativas: sólidas e desenhadas em cor âmbar-escuro
- Plataformas inativas: translúcidas (ghost, alpha 60) e intangíveis
- Plataforma "de luz": col. 44, linha 13 (ativa quando lit=True)
- Plataforma "de sombra": col. 47, linha 11 (ativa quando lit=False)
- Colisão com plataformas extras é tratada manualmente (fora do tilemap padrão)

**Solução:** Apagar → subir pelo lado esquerdo → acender → subir pelo lado direito → alcançar saída no topo. Player alcançar `y < puzzle2_exit_y = 10 * TILE` marca o puzzle como resolvido.

**Feedback de resolução:** Mensagem "A passagem se abre." + +1 sabedoria.

---

## 9. Interface e UX

### 9.1 HUD

**Corações de HP:**
- Posição: canto superior esquerdo
- Fundo semitransparente com borda preta e borda interna dourada
- Cada coração: 12×12 pixels, gerado com equação matemática de coração
- Coração cheio: vermelho `(220, 40, 40)` com highlight superior-esquerdo e sombra inferior
- Coração vazio: escuro `(80, 30, 30)`, mantém silhueta
- Cacheado: cada coração é gerado uma vez e reutilizado (sem loop por frame)

**Label de ato:** Canto superior direito, cor âmbar-escuro. Exibe o ato atual: "Ato 1 — A Vila", "Ato 2 — A Trilha", "Ato 3 — A Caverna". Limpo nas EndingScene e CreditsScene.

**Mensagens de sistema:**
- Aparecem no topo central com fundo semitransparente preto
- Fade in/out suave (primeiros/últimos 15 frames)
- Cor âmbar com brilho proporcional ao alpha
- **Deduplicação:** se a mesma mensagem já está ativa, renova o timer em vez de adicionar cópia
- Máximo de 3 mensagens simultâneas (a mais antiga é removida)
- Duração padrão: 150 frames

**Prompt de interação:** Centro da tela, acima do chão de diálogo. Animação senoidal de pulso lento (não pisca — pulsa suavemente). Borda da cor do prompt, fundo escuro semitransparente.

**Flash de dano:** Overlay vermelho semitransparente ao tomar dano via `ScreenEffects.flash()`. Alpha máximo: 90. Sobe apenas se o novo flash for mais intenso que o atual (evita resets).

### 9.2 Tela de Morte (premium)

Ativada ao receber `PLAYER_DIED`:

| **Fase** | **Frames** | **O que acontece** |
|---|---|---|
| 0–39 | 0–39 | Overlay preto sobe gradualmente (alpha +4/frame, max 200) |
| 1 | 40+ | "Caio caiu." em vermelho escuro aparece com fade |
| 2 | 70+ | "Mas a pedra espera." em âmbar-apagado |
| 3 | 110+ | "[ENTER] Tentar de novo" e "[ESC] Menu" pulsam suavemente |

O jogo só processa input de morte após o overlay iniciar. ENTER reinicia o ato atual. ESC vai para o menu (com fade out). O karma é preservado em ambos os casos.

### 9.3 Tela de Pausa (premium)

Ativada por ESC durante o jogo (exceto durante fade in/out ou morte):
- Overlay escuro semitransparente (alpha 175) sobre o jogo congelado
- Painel central 200×110 pixels com fundo quase opaco e borda dupla (preta externa, âmbar interna, âmbar-escuro segunda borda interna)
- Título "PAUSADO" em dourado, fonte monoespaçada bold 14pt
- Linha separadora
- "[ENTER] Continuar" em branco
- "[M] Menu principal" em âmbar-apagado
- Nome do ato atual em cor âmbar muito escura (rodapé do painel)

ENTER despausa. M inicia fade out → IntroScene (com reset de karma).

### 9.4 Caixa de Diálogo

| **Elemento** | **Detalhes** |
|---|---|
| Posição | `y = SCREEN_H − 84 px` (interno) |
| Fundo | HUD_BG com alpha 220 + borda preta externa + borda dourada interna |
| Avatar | 40×40 pixels, canto esquerdo da caixa, borda dourada |
| Nome do speaker | Fonte bold 9pt, cor dourada (ou azul para Iracema) |
| Linha anterior | Exibida acima em tom âmbar-escuro (contexto) |
| Texto atual | Typewriter: 2 chars/frame (~120 chars/s a 60 FPS) |
| Skip typewriter | X/K durante digitação completa o texto imediatamente |
| Avançar | X/K quando linha completa: passa para próxima |
| Indicador | Triângulo ▼ dourado pisca quando linha está completa |

**Fonte dos diálogos:** Carregados via `DialogueLoader` de `content/dialogue/npcs.json`. Formato: `{ "npc_key": ["linha 1", "linha 2", ...] }`. Mais de 40 chaves disponíveis: aldeao_0–2, zequinha, comerciante, crianca, guardiao, iracema, altar_0–4, registro_0–4, camara_0–2, pedra_decisao, pedra_final_memoria, pedra_final_tesouro, pedra_final_silencio, entre outras.

**Avatar de Iracema:** Não é sprite estático — o espaço do avatar exibe partículas azuis animadas (`SPIRIT_BLUE`) geradas em tempo real.

### 9.5 Efeitos de Transição

| **Efeito** | **Duração** | **Velocidade** |
|---|---|---|
| Fade in (entrada na cena) | ~25 frames | -10 alpha/frame (de 255 a 0) |
| Fade out (saída da cena) | ~25 frames | +10 alpha/frame (de 0 a 255) |
| Camera shake (boss) | 12–15 frames | Intensidade 4 pixels |
| Camera shake (Zinha) | 4 frames | Intensidade 1 pixel |

Os fades bloqueiam todo o input (fade in bloqueia a cena inteira; fade out bloqueia e chama o callback ao atingir 255).

---

## 10. Direção de Arte

### 10.1 Filosofia

**Pixel art procedural:** Todos os sprites, tiles, fundos e efeitos são gerados em Python puro, por código, sem um único arquivo de imagem externo. O jogo completo tem menos de 5 MB. Isso foi uma decisão deliberada: garante funcionamento em qualquer ambiente sem dependências de assets e força consistência visual definida por código.

**Resolução interna:** 640×360 pixels, upscalado **3×** para 1920×1080 via `pygame.transform.scale()`. A baixa resolução interna reforça o estilo pixel art e mantém alta performance.

**Linguagem de cores consistente:** Qualquer elemento âmbar = memória ancestral / o Sinal. Qualquer elemento azul/ciano = espírito (Iracema). Qualquer elemento roxo = corrupção (morcegos, energia transbordando). Essa linguagem não é explicada — é estabelecida gradualmente.

### 10.2 Paletas

**Sertão (Atos 1–2) — `PALETTE_SERTAO`:**

| **Nome** | **RGB** | **Uso** |
|---|---|---|
| `sky_dawn` | (255, 140, 60) | Céu do amanhecer |
| `sky_mid` | (220, 80, 40) | Gradiente de céu |
| `horizon` | (255, 200, 80) | Linha do horizonte |
| `rock_light` | (180, 140, 90) | Destaque de pedra |
| `rock_mid` | (140, 100, 60) | Base de pedra |
| `rock_dark` | (90, 60, 35) | Sombra de pedra |
| `soil` | (160, 110, 55) | Terra do sertão |
| `caio_skin` | (200, 150, 100) | Pele de Caio |
| `caio_shirt` | (178, 40, 30) | Camisa vermelha |
| `caio_pants` | (52, 72, 142) | Calça azul |
| `caio_hat` | (100, 70, 30) | Chapéu de couro |
| `caio_boots` | (80, 50, 20) | Botas |
| `heart_red` | (220, 40, 40) | Coração cheio |
| `heart_empty` | (80, 30, 30) | Coração vazio |
| `hud_bg` | (20, 15, 10) | Fundo do HUD |
| `GOLD` | (220, 180, 60) | UI, bordas, nomes |

**Caverna (Ato 3) — `PALETTE_CAVE`:**

| **Nome** | **RGB** | **Uso** |
|---|---|---|
| `bg_deep` | (10, 5, 20) | Fundo profundo |
| `rock_cave` | (40, 30, 60) | Rocha da caverna |
| `rock_glow` | (80, 50, 120) | Rocha bioluminescente |
| `amber_glow` | (200, 130, 30) | Brilho âmbar / o Sinal |
| `spirit_blue` | (80, 160, 220) | Iracema / espírito |
| `biolum` | (60, 200, 150) | Bioluminescência |
| `corrupt_purple` | (100, 50, 150) | Partículas de morcego morto |

### 10.3 Sprites dos NPCs — silhuetas distintas

Cada personagem é reconhecível a distância, sem precisar ler o nome:

| **NPC** | **Elemento de silhueta único** |
|---|---|
| Aldeão 0 | Alto e magro, braços cruzados no peito, chapéu de palha de aba dupla da largura do sprite |
| Aldeão 1 | Baixa e larga, vestido A-line (alarga para baixo), lenço vermelho vivo, cesto no braço direito |
| Aldeão 2 | Curvado para frente, barba rala branca, bengala grossa rústica, calça com remendos de cor diferente |
| Zequinha | Robe longo terroso, cabelos brancos compridos nas laterais, bengala ornamentada com pomo brilhante |
| Zinha | Minúscula, laço rosa enorme, olhos grandes com íris azul visível, vestido amarelo-vivo |
| Comerciante | Gordo, bigodão espesso de 3 linhas, avental com dois bolsos salientes, bochechas rosadas |
| Iracema | Silhueta humana feminina feita exclusivamente de partículas azuis — sem sprite fixo |

### 10.4 Tiles (16×16 pixels, todos procedurais)

| **ID** | **Nome** | **Técnica visual** |
|---|---|---|
| 0 | AIR | Transparente (sem colisão) |
| 1 | PEDRA_TOPO | Gradiente + highlight no topo |
| 2 | PEDRA_MEIO | Ruído procedural escuro |
| 3 | PEDRA_BASE | Base de pedra sólida |
| 4 | TERRA | Ruído em tom terroso |
| 5 | CACTO_BASE | Transparência, tronco + espinhos |
| 6 | CACTO_TOPO | Continuação do cacto |
| 7 | TREPADEIRA | Vines verdes decorativos |
| 8 | PEDRA_CASTELO | Grade de juntas de alvenaria |
| 9 | ROCHA_CAVE | Ruído em tons roxo-escuro |
| 10 | ROCK_GLOW | Cave rock + pontos bioluminescentes com fade |
| 11 | CRISTAL | Polígono âmbar com highlight diagonal |
| 12 | AGUA | Ondas azuis animadas |
| 13 | GRAMA_SECA | Hastes finas em marrom queimado |
| 14 | POTE | Elipse + boca, sem brilho |
| 15 | CAIXOTE | Retângulo com madeira texturizada |

### 10.5 Sistema de Efeitos Visuais (art/fx.py)

**Classe `ParticleSystem` — emitters pré-configurados:**

| **Emitter** | **Cor** | **Count** | **Gatilho** |
|---|---|---|---|
| `emit_death()` | Roxo (100, 50, 150) | 6 | `ENEMY_KILLED` |
| `emit_dust()` | Bege | 2 | Passos do player |
| `emit_altar()` | Âmbar | 1 | Altar ativo / câmara final |
| `emit_damage()` | Vermelho | 5 | `PLAYER_DAMAGED` |
| `emit_boss_death()` | Âmbar (24) + faíscas (16) | 40 total | `BOSS_DEFEATED` |
| `emit_phase_burst()` | Âmbar brilhante | 12 | Fase 2 do boss |

**Classe `ScreenEffects`:**
- `camera_shake(intensity=4, frames=12)` — tremor de câmera
- `flash(color, frames=8)` — flash colorido sobre a tela
- `fade_out(frames=30)` / `fade_in(frames=30)` — transição de cena
- `apply_vignette(dest_surf, intensity=80)` — vinheta de escurecimento nas bordas

**Funções globais:**
- `draw_stars(surface, count=150, seed=42)` — campo de estrelas com seed determinístico
- `draw_ambient_light(surface, sources, w, h)` — iluminação dinâmica via `BLEND_RGBA_ADD`

---

## 11. Arquitetura Técnica

### 11.1 Stack

| **Componente** | **Tecnologia** | **Versão** |
|---|---|---|
| Linguagem | Python | 3.9+ |
| Engine / Framework | Pygame | 2.1+ |
| Arte | Geração procedural | Python puro |
| Testes | pytest | — |
| Diálogos | JSON externo | content/dialogue/ |
| Áudio | pygame.mixer | via Pygame |

### 11.2 Estrutura de pastas e responsabilidades

```
pedra_dos_ancestrais/
│
├── main.py                    # Ponto de entrada, instancia Game()
│
├── config/
│   ├── display.py             # Resolução 640×360, upscale 3×, 60 FPS
│   ├── physics.py             # Constantes de física
│   ├── palette.py             # Paletas PALETTE_SERTAO e PALETTE_CAVE
│   └── scene_ids.py           # Enum de IDs de cena
│
├── shared/
│   ├── enums.py               # PlayerState, TileID, GameEvent
│   └── utils.py               # clamp, lerp, load_json, get_logger
│
├── core/
│   ├── game.py                # Loop principal, injeção de dependências
│   ├── event_bus.py           # Pub/sub com subscribe/unsubscribe/clear
│   ├── input_manager.py       # InputState dataclass + DEFAULT_BINDINGS
│   └── scene_manager.py       # Stack de cenas (push/pop/replace)
│
├── systems/
│   ├── karma.py               # KarmaSystem, KarmaSummary, JourneySummary
│   ├── dialogue_loader.py     # Carrega content/dialogue/npcs.json
│   ├── dialogue.py            # DialogueSystem com typewriter e avatar
│   ├── hud.py                 # HUD, tela de morte, tela de pausa, flash
│   ├── tilemap.py             # Tilemap com culling e colisão AABB
│   └── audio.py               # Gerenciador de áudio via pygame.mixer
│
├── art/
│   ├── palette.py             # Helpers get(), darken(), lighten()
│   ├── sprites.py             # Todos os sprites pixel a pixel
│   ├── tiles.py               # TileRenderer com 16 tiles procedurais
│   ├── fx.py                  # Particle, ParticleSystem, ScreenEffects
│   └── backgrounds.py         # Fundos de parallax por cena
│
├── gameplay/
│   ├── player/
│   │   ├── states.py          # PlayerState enum + VALID_TRANSITIONS
│   │   └── player.py          # Player: física AABB, coyote, buffer, combate
│   ├── enemies/
│   │   ├── base_enemy.py      # Enemy: classe base abstrata
│   │   ├── bat_enemy.py       # BatEnemy com IA senoidal
│   │   └── guardian_statue.py # GuardianStatue: 2 fases + rush + ShockWave
│   └── npcs/
│       └── __init__.py
│
├── entities/                  # Shims de compatibilidade (re-exports)
│
├── scenes/
│   ├── base_scene.py          # BaseScene: on_enter/on_exit/update/draw
│   ├── intro_scene.py         # Tela de título
│   ├── village_scene.py       # Ato 1 — A Vila
│   ├── trail_scene.py         # Ato 2 — A Trilha
│   ├── cave_scene.py          # Ato 3 — A Caverna
│   ├── ending_scene.py        # 3 finais com sequências de steps
│   └── credits_scene.py       # Créditos com scroll + reset de karma
│
├── content/
│   └── dialogue/
│       └── npcs.json          # 40+ chaves de diálogo
│
└── tests/
    ├── test_player_states.py  # 7 testes da máquina de estados
    ├── test_event_bus.py      # 6 testes do EventBus
    ├── test_dialogue_loader.py# 5 testes do DialogueLoader
    └── test_karma_endings.py  # 28+ testes do karma e finais
```

### 11.3 Padrões de design

| **Padrão** | **Implementação** | **Benefício** |
|---|---|---|
| Service Injection | BaseScene recebe `scene_manager`, `bus`, `karma`, `input_manager` no constructor | Testabilidade e desacoplamento |
| Event Bus | `core/event_bus.py` | Karma nunca é chamado diretamente; sistemas desacoplados |
| Scene Stack | `core/scene_manager.py` com push/pop/replace | Transições com estado preservado |
| State Machine | `PlayerState` + `VALID_TRANSITIONS` | Estados validados por tabela de transição |
| Observer | KarmaSystem via EventBus | Karma ouve eventos sem ser conhecido pelos publicadores |
| Template Method | `BaseScene.on_enter()` / `update()` / `draw()` | Ciclo de vida padronizado para todas as cenas |
| Cache | `TileRenderer._cache`, corações do HUD | Tiles e corações gerados uma vez, reutilizados |
| Dataclass | `KarmaSummary`, `JourneySummary`, `InputState` | Imutabilidade e clareza de dados |

### 11.4 Eventos do sistema (GameEvent enum)

| **Evento** | **Publicado por** | **Ouvido por** |
|---|---|---|
| `PLAYER_DAMAGED` | Player | HUD (flash), ScreenEffects (shake) |
| `PLAYER_DIED` | Player | HUD (tela de morte) |
| `PLAYER_HEALED` | Player | HUD |
| `ENEMY_KILLED` | Enemy | KarmaSystem (coragem +1) |
| `DIALOGUE_OPENED` | DialogueSystem | HUD (esconde prompts) |
| `DIALOGUE_CLOSED` | DialogueSystem | KarmaSystem (sabedoria +1) |
| `DIALOGUE_ADVANCE` | InputManager | DialogueSystem |
| `POT_BROKEN` | PotCommon | KarmaSystem (ganância +1) |
| `ITEM_COLLECTED` | RelicAmber | KarmaSystem (ganância +1 se is_trap) |
| `SCENE_TRANSITION` | SceneManager | Audio (troca música) |
| `KARMA_CHANGED` | KarmaSystem | *(interno)* |
| `BOSS_DEFEATED` | GuardianStatue | KarmaSystem (coragem +1), SceneManager |

### 11.5 Pipeline de render

```
Frame do jogo:
  1. inp.poll()                     — captura InputState das teclas
  2. scene_manager.apply_pending()  — aplica troca de cena se pendente
  3. scene.handle_event(events)     — processa eventos pygame
  4. scene.update()                 — lógica de jogo
  5. internal.fill((0,0,0))         — limpa superfície interna (640×360)
  6. scene.draw(internal)           — render da cena na superfície interna
  7. pygame.transform.scale(         — upscale 3×
       internal, (1920, 1080), screen)
  8. pygame.display.flip()          — exibe no monitor
  9. clock.tick(60)                 — cap de 60 FPS
```

**Culling:** Apenas tiles dentro do rect da câmera são renderizados via `get_solid_rects_near()`. Entidades fora do rect visível pulam o draw. Isso mantém a performance constante mesmo em mapas de 70 colunas.

### 11.6 Testes

**4 suites de testes** separadas, executáveis via pytest sem dependência de pygame:

| **Suite** | **Arquivo** | **Testes** | **Cobertura** |
|---|---|---|---|
| Player States | test_player_states.py | 7 | VALID_TRANSITIONS, estado DEAD terminal |
| Event Bus | test_event_bus.py | 6 | subscribe, publish, unsubscribe, clear |
| Dialogue Loader | test_dialogue_loader.py | 5 | JSON válido, chave inexistente, JSON inválido |
| Karma & Finais | test_karma_endings.py | 28+ | 3 finais, caps, casos limítrofes, fluxo completo |

```bash
pytest tests/
```

---

## 12. Fluxo do Jogo e Finais

### 12.1 Fluxo completo

```
┌─────────────────────────────────────┐
│         TELA DE TÍTULO              │
│         (IntroScene)                │
│  • pixel âmbar pisca 1× (frame 60)  │
│  • dica de controles (frame 300)    │
└──────────────┬──────────────────────┘
               │ ENTER / X
               ▼
┌─────────────────────────────────────┐
│       ATO 1 — A VILA                │
│       (VillageScene)                │
│                                     │
│  NPCs (cada um +1 sabedoria)        │
│  Zinha (ajudar: +cor+sab            │
│         ignorar: -cor)              │
│  Potes (quebrar: +ganância)         │
│  Relíquias (destruir: +ganância)    │
└──────────────┬──────────────────────┘
               │ player.x > col. 57
               ▼
┌─────────────────────────────────────┐
│       ATO 2 — A TRILHA              │
│       (TrailScene)                  │
│                                     │
│  Morcegos (matar: +coragem)         │
│  Altares (ativar: +sabedoria)       │
│  Registros (ler: +sabedoria)        │
│  Relíquia (destruir: +ganância)     │
│  [portal abre com 3 altares]        │
└──────────────┬──────────────────────┘
               │ player.x > col. 66 (portal aberto)
               ▼
┌─────────────────────────────────────┐
│       ATO 3 — A CAVERNA             │
│       (CaveScene)                   │
│                                     │
│  Morcegos faster (+coragem)         │
│  Puzzle 1 cristais (+sabedoria)     │
│  Puzzle 2 sombras (+sabedoria)      │
│  Registros (lore, +sabedoria)       │
│  Iracema + trato (honrou/traiu/rec) │
│  Guardião (+coragem)                │
└──────────────┬──────────────────────┘
               │ player.x > col. 57 + Guardião derrotado
               ▼
┌─────────────────────────────────────┐
│       CÁLCULO DO FINAL              │
│       karma.final_type              │
└──────┬───────────────┬──────────────┘
       │               │               │
  ganancia≥3    cond. verdadeiro     else
       ▼               ▼               ▼
┌──────────┐  ┌──────────────┐  ┌──────────┐
│   RUIM   │  │  VERDADEIRO  │  │  NEUTRO  │
│  6 steps │  │    6 steps   │  │  5 steps │
└────┬─────┘  └──────┬───────┘  └────┬─────┘
     └────────────────┴───────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │       CRÉDITOS        │
          │    (CreditsScene)     │
          │    scroll lento       │
          │    tag do final       │
          │  [ENTER] → IntroScene │
          │    karma resetado     │
          └───────────────────────┘
```

### 12.2 Cenas de Final — sequências detalhadas

**EndingScene TRUE (6 steps):**

| **Step** | **Duração** | **Cena** | **Texto** |
|---|---|---|---|
| 1 | 120f | Câmara com gravuras pulsando | "A câmara do coração se abre. / Rostos. Nomes. Histórias gravadas na rocha." |
| 2 | 150f | Partículas fluem para Caio | "Partículas de memória flutuam em sua direção. / Você as recebe." |
| 3 | 180f | Iracema se despede (partículas dispersando) | "Os que viveram aqui precisavam que alguém lembrasse. Você lembra agora." |
| 4 | 120f | Exterior — amanhecer | "Amanhecer. Você desce a trilha." |
| 5 | 180f | Zinha corre; Caio se ajoelha | *(sem texto — a imagem é o final)* |
| 6 | 80f | Preto | — |

**EndingScene NEUTRAL (5 steps):**

| **Step** | **Duração** | **Cena** | **Texto** |
|---|---|---|---|
| 1 | 120f | Câmara quase vazia, cristal fraco | "A câmara está quase vazia. / Um único cristal fraco no centro." |
| 2 | 150f | Iracema distante | "O tesouro só aparece pra quem realmente procura. Você procurou… alguma coisa." |
| 3 | 120f | Exterior — entardecer | "Entardecer. Você desce a trilha. / Confuso. Mas vivo." |
| 4 | 180f | Caio de costas no horizonte | *(sem texto)* |
| 5 | 80f | Preto | — |

**EndingScene BAD (6 steps):**

| **Step** | **Duração** | **Cena** | **Texto** |
|---|---|---|---|
| 1 | 120f | Sala de ouro | "Ouro. Joias. O que você veio buscar." |
| 2 | 100f | Ouro petrificando | "Ao tocar — / tudo escurece." |
| 3 | 120f | Iracema fria | "Você encontrou o que procurava." |
| 4 | 100f | Paredes fechando, fuga | "As paredes se fecham. / Corra." |
| 5 | 150f | Mãos com poeira escura permanente | "Você sai. / Mas a poeira não sai das suas mãos." |
| 6 | 80f | Preto | — |

**Navegação nas cenas de final:** ENTER salta para o próximo step (após 20 frames de carência por step para evitar skip acidental).

### 12.3 Créditos (CreditsScene)

Scroll automático a 0.5 px/frame sobre fundo da tela de título. Exibe a tag do final recebido no topo:
- Final Verdadeiro: "Final: O Tesouro Não é Ouro" (dourado)
- Final Neutro: "Final: Quem Entra, Muda" (azul-acinzentado)
- Final Ruim: "Final: A Ganância Cobra Juros" (vermelho-escuro)

ENTER em qualquer momento vai para IntroScene com reset completo do karma (`coragem=0, sabedoria=0, ganancia=0, divida_iracema=None`).

---

## 13. Estrutura de Arquivos

```
pedra_dos_ancestrais/
├── main.py                        ~40 linhas
├── config/
│   ├── display.py                 ~12 linhas
│   ├── physics.py                 ~11 linhas
│   ├── palette.py                 ~52 linhas
│   └── scene_ids.py               ~10 linhas
├── shared/
│   ├── enums.py                   ~35 linhas
│   └── utils.py                   ~37 linhas
├── core/
│   ├── game.py                    ~80 linhas
│   ├── event_bus.py               ~40 linhas
│   ├── input_manager.py           ~53 linhas
│   └── scene_manager.py           ~54 linhas
├── systems/
│   ├── karma.py                   ~202 linhas
│   ├── dialogue_loader.py         ~36 linhas
│   ├── dialogue.py                ~120 linhas
│   ├── hud.py                     ~175 linhas
│   ├── tilemap.py                 ~68 linhas
│   └── audio.py                   ~60 linhas
├── art/
│   ├── palette.py                 ~16 linhas
│   ├── sprites.py                 ~605 linhas
│   ├── tiles.py                   ~200 linhas
│   ├── fx.py                      ~246 linhas
│   └── backgrounds.py             ~200 linhas
├── gameplay/
│   ├── player/
│   │   ├── states.py              ~30 linhas
│   │   └── player.py              ~268 linhas
│   ├── enemies/
│   │   ├── base_enemy.py          ~83 linhas
│   │   ├── bat_enemy.py           ~67 linhas
│   │   └── guardian_statue.py     ~186 linhas
│   └── npcs/
│       └── __init__.py
├── entities/                       (shims de compatibilidade)
├── scenes/
│   ├── base_scene.py              ~60 linhas
│   ├── intro_scene.py             ~82 linhas
│   ├── village_scene.py           ~175 linhas
│   ├── trail_scene.py             ~240 linhas
│   ├── cave_scene.py              ~295 linhas
│   ├── ending_scene.py            ~346 linhas
│   └── credits_scene.py           ~122 linhas
├── content/
│   └── dialogue/
│       └── npcs.json              40+ chaves de diálogo
└── tests/
    ├── test_player_states.py      ~34 linhas
    ├── test_event_bus.py          ~57 linhas
    ├── test_dialogue_loader.py    ~37 linhas
    └── test_karma_endings.py      ~268 linhas
```

---

## 14. Requisitos e Execução

### 14.1 Requisitos

| **Componente** | **Mínimo** |
|---|---|
| Sistema operacional | Windows 10 / Ubuntu 20.04 / macOS 12 |
| Python | 3.9+ |
| Pygame | 2.1+ |
| RAM | 256 MB |
| GPU | Qualquer (render via CPU — pygame software renderer) |
| Armazenamento | < 5 MB |
| Display | 1920×1080 mínimo (upscale 3× de 640×360) |

### 14.2 Instalação e execução

```bash
# Instalar dependência
pip install pygame>=2.1.0

# Executar (a partir da pasta pedra_dos_ancestrais/)
python main.py
```

### 14.3 Executar os testes

```bash
# A partir da pasta pedra_dos_ancestrais/
pytest tests/

# Saída esperada: todos os testes passam, 0 falham.
```

### 14.4 Histórico de versões

| **Versão** | **Mudanças principais** |
|---|---|
| v1 | Engine base, física do player, cenas estruturadas, karma v1, arte procedural básica (retângulos) |
| v2 | Sprites redesenhados pixel a pixel, NPCs com silhuetas distintas, arte v2 |
| v3 | Bug fix do Event Bus (acúmulo de listeners), tela de morte premium, tela de pausa premium, prompts animados, label de ato, flag `_exiting` em todas as cenas, delay manual do Guardião, deduplicação de mensagens HUD |
| v4 (atual) | Upscale 3× para 1920×1080 (era 2×/1280×720), arquitetura Service Injection (dependências injetadas no constructor — sem singletons globais), Guardian rebalanceado (HP 14, rush na Fase 2, velocidade 1.4), KarmaSystem expandido com `KarmaSummary` e `JourneySummary`, diálogos migrados para JSON externo (40+ chaves), 4 suites de testes separadas, sistema de áudio integrado, `PlayerState` com `VALID_TRANSITIONS` validadas, 16 tiles procedurais, 12 GameEvents documentados |

---

## Apêndice A — Consistência narrativa

| **Elemento** | **Introduzido** | **Contextualizado** | **Resolvido** |
|---|---|---|---|
| O Sinal | IntroScene (pixel âmbar) | Zequinha: "só entra quem está destinado" | Guardião: "você tem o sinal" |
| Morcegos corrompidos | TrailScene (visualmente) | Zinha: "sonhos que a pedra não quer mais" | Implícito: energia transbordando |
| Desaparecimento de Zequinha | VillageScene | Não explicado diretamente | Final Verdadeiro: bengala + trapo vermelho |
| O trato de Iracema | CaveScene | Iracema: diálogo completo com altares | Final: honrar ou trair define nuance do resultado |
| Os Tapuias do Alto | Altares (fragmentos) | Registros da caverna | Câmara do coração |
| Zinha e a memória | VillageScene (fala dela) | Conecta com lore dos morcegos | Final Verdadeiro: ela corre até Caio |
| Bengala de Zequinha | VillageScene (objeto) | Não explicado | Final Verdadeiro: com trapo vermelho |

---

## Apêndice B — Glossário

| **Termo** | **Significado no jogo** |
|---|---|
| O Sinal | Marca invisível da Pedra em quem ela escolhe; responsabilidade, não privilégio |
| Karma | Sistema de rastreamento silencioso de comportamento; nunca visível ao jogador |
| Relíquia âmbar | Objeto sagrado com brilho pulsante; destruir = ganância |
| Pote comum | Objeto decorativo sem valor especial; destruir = ganância |
| O Trato | Promessa a Iracema de compartilhar a memória; pode ser honrado, traído ou recusado |
| Tapuias do Alto | Civilização ancestral fictícia, base do lore |
| Corrompido | Estado dos morcegos — infectados pela energia transbordando |
| A câmara do coração | Interior final da Pedra; o que é revelado depende de quem Caio se tornou |
| Event Bus | Sistema pub/sub central que desacopla todos os sistemas do jogo |
| Service Injection | Padrão arquitetural da v4: cada cena recebe suas dependências no constructor |
| JourneySummary | Registro narrativo completo da jornada do jogador |

---

*Game Design Document — A Pedra dos Ancestrais*
*Versão: 4.0 — Build v4_final*
*Documento gerado em Maio de 2026*
*Reflete exatamente o estado implementado e testado do código.*
