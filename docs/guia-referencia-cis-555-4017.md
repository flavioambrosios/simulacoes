# Guia de Referência: CIs 555 e 4017

**Disciplina:** Física / Robótica / Eletrodinâmica  
**Público-alvo:** Ensino Médio  

---

## Sumário

1. [O que é um circuito integrado?](#1-o-que-é-um-circuito-integrado)
2. [Como identificar os pinos](#2-como-identificar-os-pinos)
3. [CI 555: visão geral](#3-ci-555-visão-geral)
4. [CI 555: função de cada pino](#4-ci-555-função-de-cada-pino)
5. [CI 4017: visão geral](#5-ci-4017-visão-geral)
6. [CI 4017: função de cada pino](#6-ci-4017-função-de-cada-pino)
7. [Como os dois CIs trabalham juntos](#7-como-os-dois-cis-trabalham-juntos)
8. [Cuidados importantes](#8-cuidados-importantes)
9. [Resumo rápido](#9-resumo-rápido)

---

## 1. O que é um circuito integrado?

Um **circuito integrado (CI)** é um pequeno componente que reúne muitos elementos eletrônicos dentro de uma única cápsula. Em vez de montar separadamente vários transistores, resistores e outros elementos, usamos um CI que já executa determinada função.

Neste guia estudaremos:

* **CI 555:** temporizador e gerador de pulsos.
* **CI 4017:** contador que distribui os pulsos por dez saídas sequenciais.

> Os nomes **NE555**, **LM555** e **TLC555**, por exemplo, representam versões da família 555. O comportamento básico dos oito pinos é semelhante, mas limites elétricos, tensão de alimentação e corrente de saída podem variar. Consulte a folha de dados do componente que estiver usando.

---

## 2. Como identificar os pinos

Observe o CI **por cima**, com o entalhe (meia-lua) voltado para cima. O pino 1 fica à esquerda do entalhe. A numeração segue no sentido anti-horário, formando um “U”.

![Numeração dos pinos dos CIs 555 e 4017 vistos de cima](img/pinagem-cis.svg)

### Antes de ligar

1. Localize o entalhe ou a pequena marca circular da cápsula.
2. Confirme a posição do pino 1.
3. Conte novamente os pinos antes de conectar VCC e GND.
4. Faça todas as ligações com a fonte desligada.

---

## 3. CI 555: visão geral

O CI 555 compara a tensão de um capacitor com duas referências internas:

* aproximadamente $\frac{1}{3}V_{CC}$;
* aproximadamente $\frac{2}{3}V_{CC}$.

Essas comparações permitem controlar a saída e produzir atrasos ou oscilações. Os três usos mais comuns são:

* **Astável:** gera pulsos continuamente, como um relógio eletrônico.
* **Monoestável:** gera um único pulso com duração definida após receber um disparo.
* **Biestável:** funciona como uma memória simples, alternando entre dois estados.

Nos experimentos do semáforo e dos dez LEDs, o 555 é usado em **modo astável**.

---

## 4. CI 555: função de cada pino

| Pino | Nome | Tipo | Função geral |
| ---: | :--- | :---: | :--- |
| 1 | GND | Alimentação | Referência de 0V e terminal negativo da alimentação. |
| 2 | TRIGGER (Disparo) | Entrada | Quando sua tensão cai abaixo de aproximadamente $\frac{1}{3}V_{CC}$, solicita que a saída vá para o estado alto. |
| 3 | OUTPUT (Saída) | Saída | Fornece o sinal alto/baixo produzido pelo 555. Pode enviar os pulsos ao clock de outro CI. |
| 4 | RESET | Entrada | Reinicia o CI quando recebe nível baixo. Se não for usado, normalmente deve ficar ligado ao VCC. |
| 5 | CONTROL VOLTAGE (Controle) | Entrada | Permite alterar externamente as referências internas do 555. Em montagens simples pode ficar sem ligação; um capacitor pequeno para o GND pode melhorar a imunidade a ruídos. |
| 6 | THRESHOLD (Limiar) | Entrada | Quando sua tensão ultrapassa aproximadamente $\frac{2}{3}V_{CC}$, solicita que a saída vá para o estado baixo. |
| 7 | DISCHARGE (Descarga) | Transistor interno | Conecta o circuito temporizador ao GND por meio de um transistor interno, permitindo a descarga do capacitor. Não é uma saída de sinal comum. |
| 8 | VCC | Alimentação | Terminal positivo da alimentação. |

### Entendendo os pinos principais

#### Pinos 2 e 6: observam o capacitor

No modo astável, os pinos 2 e 6 costumam ser ligados ao mesmo ponto do capacitor:

* o pino 2 percebe quando a tensão fica suficientemente baixa;
* o pino 6 percebe quando a tensão fica suficientemente alta.

O capacitor carrega e descarrega entre esses limites, fazendo a saída mudar repetidamente.

#### Pino 3: entrega os pulsos

O pino 3 alterna entre nível baixo e nível alto. No circuito com o 4017, cada transição adequada do sinal serve como um pulso de contagem.

#### Pino 4: RESET ativo em nível baixo

“Ativo em nível baixo” significa que a função RESET acontece quando o pino é levado ao GND. Para permitir o funcionamento normal, mantenha-o em nível alto, geralmente ligado ao VCC.

#### Pino 5: não é alimentação

O pino 5 não deve ser confundido com VCC. Ele acessa a tensão de controle interna. Quando o circuito estiver sujeito a ruído, é comum usar um capacitor de aproximadamente **10nF** entre o pino 5 e o GND.

#### Pino 7: não é uma saída de clock

O pino 7 controla a descarga do capacitor. O sinal de clock deve ser retirado do **pino 3**, não do pino 7.

---

## 5. CI 4017: visão geral

O CD4017 é um **contador decimal com dez saídas decodificadas**. Ele mantém apenas uma das saídas Q0–Q9 em nível alto por vez.

Quando recebe pulsos no pino 14:

1. Q0 fica ativa;
2. no pulso seguinte, Q1 fica ativa;
3. depois Q2, Q3 e assim sucessivamente;
4. após Q9, a contagem retorna a Q0.

Essa característica permite produzir sequências luminosas sem programação.

---

## 6. CI 4017: função de cada pino

| Pino | Nome | Tipo | Função geral |
| ---: | :--- | :---: | :--- |
| 1 | Q5 | Saída | Sexta etapa da sequência. |
| 2 | Q1 | Saída | Segunda etapa da sequência. |
| 3 | Q0 | Saída | Primeira etapa; normalmente fica ativa após o RESET. |
| 4 | Q2 | Saída | Terceira etapa da sequência. |
| 5 | Q6 | Saída | Sétima etapa da sequência. |
| 6 | Q7 | Saída | Oitava etapa da sequência. |
| 7 | Q3 | Saída | Quarta etapa da sequência. |
| 8 | GND | Alimentação | Referência de 0V e terminal negativo da alimentação. |
| 9 | Q8 | Saída | Nona etapa da sequência. |
| 10 | Q4 | Saída | Quinta etapa da sequência. |
| 11 | Q9 | Saída | Décima etapa da sequência. |
| 12 | CARRY OUT | Saída | Sinal de transporte usado principalmente para acionar outro contador; pode ficar sem ligação quando não for utilizado. |
| 13 | CLOCK INHIBIT / ENABLE | Entrada | Em nível alto, bloqueia a contagem. Em nível baixo, permite que os pulsos do clock sejam contados. |
| 14 | CLOCK | Entrada | Recebe os pulsos. Com o pino 13 em nível baixo, a contagem avança na transição de baixo para alto. |
| 15 | RESET | Entrada | Em nível alto, reinicia o contador em Q0. Em nível baixo, permite a contagem normal. |
| 16 | VCC | Alimentação | Terminal positivo da alimentação. |

### Ordem das dez saídas

Os números dos pinos físicos não acompanham a ordem da contagem. Use esta sequência:

| Ordem | Saída | Pino físico |
| ---: | :---: | ---: |
| 1 | Q0 | 3 |
| 2 | Q1 | 2 |
| 3 | Q2 | 4 |
| 4 | Q3 | 7 |
| 5 | Q4 | 10 |
| 6 | Q5 | 1 |
| 7 | Q6 | 5 |
| 8 | Q7 | 6 |
| 9 | Q8 | 9 |
| 10 | Q9 | 11 |

### Entendendo os pinos de controle

#### Pino 13: pausa a contagem

* **Pino 13 no GND:** contagem liberada.
* **Pino 13 no VCC:** contagem bloqueada na etapa atual.

Esse pino não apaga as saídas; apenas impede que novos pulsos façam a sequência avançar.

#### Pino 15: reinicia a sequência

* **Pino 15 no GND:** funcionamento normal.
* **Pino 15 no VCC:** Q0 fica ativa e as demais saídas ficam inativas.

O RESET também pode limitar uma sequência. Por exemplo, conectar uma saída posterior ao pino 15 faz o contador retornar a Q0 quando essa saída for alcançada. Essa técnica deve ser planejada de acordo com a quantidade de etapas desejada.

#### Pino 12: CARRY OUT

O pino 12 fornece um sinal cuja frequência é aproximadamente a frequência do clock dividida por dez. Ele é usado para encadear contadores ou indicar ciclos completos. Em um circuito com apenas um 4017, pode permanecer **sem ligação**.

> O pino 12 é uma saída. Não precisa ser ligado ao GND ou ao VCC quando não estiver sendo utilizado.

---

## 7. Como os dois CIs trabalham juntos

```mermaid
flowchart LR
    RC[Potenciômetro + capacitor] --> T[CI 555]
    T -->|Pulsos: pino 3| C[Clock do CI 4017: pino 14]
    C --> Q[Saídas Q0 até Q9]
    Q --> R[Resistores]
    R --> L[LEDs ou outras cargas]
```

O processo ocorre assim:

1. O capacitor do circuito RC carrega e descarrega.
2. O CI 555 transforma essa variação em pulsos no pino 3.
3. O pino 14 do CI 4017 recebe os pulsos.
4. A cada pulso válido, o nível alto avança para a saída seguinte.
5. Os componentes ligados às saídas respondem à sequência.

O CI 555 controla **quando** ocorre a mudança. O CI 4017 controla **qual saída** fica ativa.

### Exemplo de montagem em protoboard

O mapa abaixo mostra uma aplicação prática dos dois CIs em uma protoboard de 830 pontos, formando um sequencial de dez LEDs. As posições são sugestões e devem ser conferidas com a numeração da placa utilizada.

![Mapa do CI 555 e do CI 4017 em protoboard de 830 pontos](img/protoboard-830-sequencial-10-leds.svg)

O roteiro detalhado dessa montagem está no [Guia de Experimento: Fita Sequencial de 10 LEDs](guia-experimento-sequencial-10-leds.md).

---

## 8. Cuidados importantes

### Entradas não devem ficar flutuando

Uma entrada “flutuante” não está ligada claramente ao VCC nem ao GND e pode captar ruído elétrico.

* No 555, mantenha o pino 4 em nível alto quando o RESET não for utilizado.
* No 4017, defina os níveis dos pinos 13 e 15; para contagem normal, ligue ambos ao GND.
* Saídas não utilizadas, como Q6 ou CARRY OUT, podem ficar sem ligação.

### Nunca ligue duas saídas diretamente

Não una diretamente duas saídas de um CI nem saídas de CIs diferentes. Se uma estiver em nível alto e outra em nível baixo, poderá ocorrer corrente excessiva. Quando for necessário combinar sinais, use componentes e circuitos apropriados, como diodos ou portas lógicas.

### Proteja os LEDs

Cada LED ligado diretamente a uma saída deve possuir resistor limitador de corrente. O valor adequado depende da tensão de alimentação, da cor do LED e dos limites do CI. Nos experimentos deste conjunto, usamos **1kΩ com alimentação de 5V** para manter uma corrente conservadora.

### Posso usar uma fonte ou bateria de 9V?

Em geral, o **NE555** e o **CD4017** podem operar com 9V, mas é necessário observar a versão e os limites indicados na folha de dados de cada componente.

A opção mais segura para os experimentos deste conjunto é:

`Fonte ou bateria de 9V → entrada do módulo MB102 → saída regulada de 5V → circuito`

Nesse caso, os CIs recebem **5V regulados** e os resistores de **1kΩ** indicados nos guias podem ser mantidos.

Cuidados importantes:

* Não conecte 9V na saída de 5V do módulo MB102. Ligue os 9V na entrada apropriada do módulo e selecione a saída de 5V.
* Se aplicar 9V diretamente aos CIs, confirme antes se ambos suportam essa tensão e alimente os dois com a mesma fonte e o mesmo GND.
* Com 9V aplicados diretamente, use resistores maiores nos LEDs, preferencialmente entre **2,2kΩ e 4,7kΩ**, para reduzir a corrente exigida das saídas do CD4017.
* O capacitor eletrolítico deve possuir tensão nominal de pelo menos **16V** quando o circuito for alimentado diretamente com 9V.
* Uma bateria retangular de 9V serve para testes, mas possui pouca capacidade e pode descarregar rapidamente, principalmente com vários LEDs.

> **Recomendação para a aula:** use os 9V apenas na entrada do módulo regulador e alimente o circuito pela saída de 5V. Isso reduz o risco de danos e mantém os valores dos componentes apresentados nos guias.

### Confira a compatibilidade entre as versões dos CIs

O nível alto produzido por algumas versões bipolares do **NE555** pode ficar próximo do limite reconhecido pelo **CD4017** quando ambos operam em 5V. Muitas montagens funcionam, mas isso não é garantido para todas as combinações de fabricantes. Se o pino 3 do 555 oscilar e o 4017 não contar, confira as folhas de dados e prefira um 555 CMOS compatível, como **TLC555**, **LMC555** ou **ICM7555**, ou utilize uma interface lógica adequada.

### Desligue a fonte antes de alterar fios

Uma ligação feita na fileira errada pode aplicar VCC a um pino destinado ao GND. Faça alterações somente com a alimentação desligada.

---

## 9. Resumo rápido

### CI 555

* **Alimentação:** pinos 8 (VCC) e 1 (GND).
* **Saída de pulsos:** pino 3.
* **Rede temporizadora:** pinos 2, 6 e 7.
* **RESET:** pino 4, ativo em nível baixo.
* **Controle interno:** pino 5.

### CI 4017

* **Alimentação:** pinos 16 (VCC) e 8 (GND).
* **Entrada de clock:** pino 14.
* **Liberação/bloqueio do clock:** pino 13.
* **RESET:** pino 15, ativo em nível alto.
* **Saídas sequenciais:** Q0–Q9.
* **CARRY OUT:** pino 12; pode ficar vazio quando não for utilizado.

### Ligação principal entre os dois

`Pino 3 do CI 555 → pino 14 do CI 4017`

Essa ligação transforma os pulsos gerados pelo 555 em uma sequência de dez estados no 4017.
