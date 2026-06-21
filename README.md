# Simulações Interativas de Física

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20737876.svg)](https://doi.org/10.5281/zenodo.20737876)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/hosted%20on-GitHub%20Pages-blue)](https://flavioambrosios.github.io/simulacoes/)

> **🧠 Nota sobre o desenvolvimento:** Este projeto foi **concebido e planejado integralmente pelo Prof. Flávio Ambrósio Campos**. Os códigos foram implementados com assistência de **ferramentas de Inteligência Artificial** (DeepSeek e ChatGPT), sob supervisão e curadoria humana. Veja a seção [Inteligência Artificial no Desenvolvimento](#-inteligência-artificial-no-desenvolvimento) para detalhes.

Um conjunto de simulações interativas para o ensino de Física no Ensino Médio, desenvolvidas e **testadas no dia a dia da sala de aula**. As simulações combinam visualizações em Canvas/Three.js com exercícios formativos, narração por síntese de voz e análise automatizada de conclusões escritas.

---

## 🧪 Simulações Disponíveis

| Simulação | Tópico | Tecnologia | Link |
|-----------|--------|------------|------|
| **Átomo de Hidrogênio** | Modelo atômico, espectros | Canvas | [Abrir](AtomodeHidrogenio/) |
| **Calorimetria** | Troca de calor, equilíbrio térmico | Canvas | [Abrir](Calorimetria/) |
| **Circuitos Elétricos DC** | Circuitos, resistores, leis de Kirchhoff | Canvas | [Abrir](CircuitosEletricosDC/) |
| **Cores** | Síntese aditiva/subtrativa, RGB | Canvas | [Abrir](Cores/) |
| **Corpo Negro** | Radiação térmica, Lei de Wien | PhET + Canvas | [Abrir](CorpoNegro/) |
| **Dilatação Térmica** | Dilatação linear, superficial, volumétrica | Canvas | [Abrir](DilatacaoTermica/) |
| **Efeito Fotoelétrico** | Einstein, fótons, função trabalho | PhET + Canvas | [Abrir](EfeitoFotoEletrico/) |
| **Escalas Termométricas** | Celsius, Fahrenheit, Kelvin | Canvas | [Abrir](EscalasTermométricas/) |
| **Espectrômetro de Massa** | Campos elétrico e magnético | Canvas + Three.js | [Abrir](EspectrometrodeMassa/) |
| **Estrelas (Diagrama HR)** | Evolução estelar, classificação | Three.js | [Abrir](ESTRELAS/) |
| **Fluxo de Calor** | Condução, convecção, radiação | Canvas | [Abrir](FluxoDeCalor/) |
| **Força Elétrica** | Lei de Coulomb | Canvas | [Abrir](ForcaEletrica/) |
| **Força Magnética** | Carga em campo magnético | Three.js | [Abrir](ForcaMagnetica/) |
| **Fotossíntese** | Física da fotossíntese, absorção de luz | Canvas | [Abrir](FotossinteseSolar/) |
| **LED e OLED** | Semicondutores, emissão de luz | Canvas | [Abrir](LEDeOLED/) |
| **Lei de Ampère** | Campo magnético em condutores | Three.js | [Abrir](LeideAmpere/) |
| **Lei de Coulomb** | Força entre cargas, campo elétrico | Canvas | [Abrir](LeiDeCoulomb/) |
| **Lei de Faraday** | Indução eletromagnética, geradores | PhET + Canvas | [Abrir](LeideFaraday/) |
| **Lei de Ohm** | Resistência, tensão, corrente | Canvas | [Abrir](LeideOhm/) |
| **Máquina de Carnot** | Ciclo termodinâmico, rendimento | Canvas | [Abrir](MaquinadeCarnot/) |
| **Momento Magnético** | Espira em campo magnético | Three.js | [Abrir](MomentoMagnetico/) |
| **Ondas 1D** | Ondas mecânicas, superposição | Canvas | [Abrir](Ondas/Ondas1D/) |
| **Óptica Geométrica** | Reflexão, refração, lentes | Canvas | [Abrir](OpticaGeometrica/) |
| **Radiação de Corpo Negro** | Espectro, Planck, Stefan-Boltzmann | PhET + Canvas | [Abrir](RadiacaodeCorpoNegro/) |
| **Relatividade Especial** | Dilatação do tempo, contração | Canvas | [Abrir](RelatividadeEspecial/) |
| **Resistência Elétrica** | Resistividade, geometria | Canvas | [Abrir](Resistencia/) |
| **Solenoide** | Campo magnético em solenoide | Three.js | [Abrir](Solenoide/) |
| **Soma de Cores** | Síntese de Fourier, análise espectral | Python + Canvas | [Abrir](SomadeCores/) |
| **Spin do Elétron** | Experimento de Stern-Gerlach | Three.js | [Abrir](SPINOR/) |
| **Transformadores** | Indução mútua, relação de espiras | Canvas | [Abrir](Transformadores/) |
| **Tunelamento Quântico** | Mecânica quântica, barreira de potencial | Canvas | [Abrir](TunelamentoQuantico/) |

---

## ✨ Funcionalidades Comuns

Todas as simulações compartilham um sistema unificado de funcionalidades pedagógicas:

### 🎮 Sistema de Exercícios
- **Exercícios formativos** gerados dinamicamente com parâmetros aleatórios
- **Múltipla escolha** com 5 opções, embaralhadas a cada tentativa
- **Feedback imediato** com correção e resposta correta
- **Opção de pular** exercícios (com confirmação)
- **Barra de progresso** visual com 6 etapas
- **Persistência de progresso**: o aluno pode fechar e retomar os exercícios depois

### 🎤 Narração por Síntese de Voz
- Faixas de áudio explicativas para cada simulação
- Controles de navegação (anterior/próximo/pausar/retomar)
- Seleção de voz (português brasileiro preferencial)
- Botões "Ouvir resolução" nos exercícios resolvidos
- As faixas são geradas automaticamente a partir do conteúdo da página ou podem ser personalizadas via vetor `tracks` no JavaScript local

### 📊 Coleta e Análise de Dados
- Envio de resultados para **planilha Google Sheets** via Apps Script
- **Análise automatizada** da conclusão escrita (extensão, coerência temática, evidências de aprendizagem)
- **Nota composta** combinando acertos nos exercícios (50%) e qualidade da conclusão (50%)
- Envio de e-mail de cópia para o professor e para o aluno (quando e-mail é fornecido)
- **Modo visitante**: checkbox que permite participação sem vínculo com série/turma

### 🧠 Aprimoramento Pedagógico
- **Exercícios resolvidos** com passo a passo para consulta
- **Modal de teoria** com explicações completas e fórmulas
- Controles interativos (sliders, seletores) vinculados à simulação visual
- Legendas com codificação de cores para grandezas físicas
- Painel de medições em tempo real

---

## 🏗️ Arquitetura

```
simulacoes/
├── _shared/
│   └── simulation-enhancer.js   ← Sistema compartilhado (exercícios, áudio, envio)
├── alunoscópio.js                ← Cadastro de alunos (opcional)
├── index.html                    ← Página inicial com lista de simulações
├── LICENSE                       ← MIT License
├── README.md                     ← Este arquivo
│
├── NomeDaSimulacao/
│   ├── index.html (ou NomeDaSimulacao.html)
│   └── ... (assets específicos)
│
└── ... (demais simulações)
```

### Para criar uma nova simulação

1. Crie uma pasta com o nome da simulação
2. Crie um arquivo HTML com a estrutura padrão (canvas/Three.js + controles + medições + modais)
3. No final do HTML, adicione a configuração do enhancer:

```javascript
<script>
window.SIMULATION_ENHANCER_CONFIG = {
    simulationName: 'Nome da Simulação',
    storageKey: 'nome-da-simulacao'
};
</script>
<script src="../_shared/simulation-enhancer.js"></script>
```

4. Opcionalmente, defina um vetor de faixas de narração personalizadas:

```javascript
const tracks = [
    'Primeira faixa explicativa...',
    'Segunda faixa...'
];

const exampleNarrations = {
    '1': 'Narração para o exemplo 1...',
    '2': 'Narração para o exemplo 2...'
};
```

---

## 🚀 Publicação

O repositório está configurado para publicação automática via **GitHub Pages** a partir da branch `main`. As simulações ficam disponíveis em:

```
https://flavioambrosios.github.io/simulacoes/
```

---

## 📜 Licença e Atribuição

Este projeto é distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para detalhes.

**Autor:** Prof. Flávio Ambrósio Campos  
**Instituição:** CEAN - Centro de Ensino Médio Asa Norte (Brasília-DF)  
**E-mail:** flavio.ambrosio@edu.se.df.gov.br

### DOI e Registro

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20737876.svg)](https://doi.org/10.5281/zenodo.20737876)

Este conjunto de simulações está registrado no **Zenodo** com DOI: [10.5281/zenodo.20737876](https://doi.org/10.5281/zenodo.20737876). O registro assegura a **autoria e data de criação** do trabalho, servindo como referência permanente para citações acadêmicas.

### Créditos

- **Simulações PhET Interactive Simulations** ([University of Colorado Boulder](https://phet.colorado.edu/)) — utilizadas sob licença CC-BY 4.0 em algumas simulações (Corpo Negro, Efeito Fotoelétrico, Lei de Faraday)
- **Three.js** — biblioteca 3D utilizada em algumas simulações (Espectrômetro de Massa, Estrelas, Força Magnética, entre outras)
- **Google Apps Script** — para coleta e armazenamento de dados dos alunos

### 💻 Processo de Desenvolvimento

Este projeto é construído em um **fluxo de trabalho híbrido** que combina concepção pedagógica humana com assistência intensiva de Inteligência Artificial na produção de código. Abaixo está a descrição detalhada de cada etapa do processo, que se mantém em **construção permanente**.

#### 👨‍🏫 1. Concepção e Planejamento (100% humano)

**Totalmente de minha autoria**, como professor da disciplina:
- Escolha dos tópicos de Física com base no **currículo do Ensino Médio** e nas dificuldades recorrentes dos alunos
- Definição da **estrutura pedagógica** de cada simulação (teoria → exemplos resolvidos → exercícios formativos → conclusão)
- Criação dos **enunciados, fórmulas e parâmetros** dos exercícios
- **Testes em sala de aula** com turmas reais, com observação direta do uso pelos alunos
- **Iterações de melhoria** a partir do feedback dos estudantes: ajustes na dificuldade, clareza dos enunciados, usabilidade da interface e sugestões de novos recursos
- Planejamento da **progressão conceitual** e da **linguagem pedagógica** utilizada nas narrações em áudio

#### 🤖 2. Ferramentas de IA Utilizadas

O código é **majoritariamente produzido por ferramentas de IA**, sob minha supervisão e curadoria:

| Ferramenta | Modelos/Ambiente | Papel no projeto |
|-----------|-----------------|------------------|
| **DeepSeek** (chat) | DeepSeek-V3 / R1 | Estruturação de lógicas de simulação, algoritmos de geração dinâmica de exercícios, criação de interfaces Canvas/Three.js, depuração e revisão de código |
| **ChatGPT** (chat) | GPT-4o / GPT-4.1 | Criação de conteúdo textual explicativo, documentação, sugestões de CSS/design e prototipagem de funcionalidades |
| **Continue.dev** (IDE) | DeepSeek Coder V2 / Qwen2.5-Coder | Assistência direta no editor VS Code para escrever, refatorar e depurar blocos de código durante o desenvolvimento, com modelos locais e remotos |
| **GitHub Copilot** (IDE) | Modelo proprietário Microsoft | Autocomplete de código e sugestões contextuais durante a escrita no VS Code |
| **GitHub** | — | Versionamento, armazenamento e **publicação automática via GitHub Pages** |

#### 🔄 3. Fluxo de Trabalho

1. **Eu descrevo o objetivo pedagógico** em linguagem natural para a IA (ex.: "Preciso de uma simulação de troca de calor onde o aluno possa variar as massas e temperaturas iniciais")
2. **A IA gera o código** (HTML, CSS, JavaScript) como ponto de partida
3. **Eu testo, reviso e adapto** cada funcionalidade, ajustando parâmetros, corrigindo comportamentos e refinando a experiência do usuário
4. **Levo para a sala de aula**, observo os alunos usando e identifico pontos de melhoria
5. **Volto com o feedback** para novas iterações com a IA, gerando novas versões

Esse ciclo se repete **dezenas de vezes para cada simulação**, ao longo de aproximadamente 12 meses (2024–2025).

#### 🧪 4. Testes em Sala de Aula e Iterações

As simulações são **testadas e validadas com turmas reais** do Ensino Médio no dia a dia da sala de aula. Esse processo revela:
- Necessidade de **ajustes na dificuldade** dos exercícios (muitos parâmetros são recalibrados)
- **Melhorias na interface** sugeridas pelos próprios alunos (posição de botões, tamanho de fontes, contraste)
- **Correções conceituais** apontadas durante as discussões em aula
- **Novos tipos de exercício** que são adicionados a partir de dúvidas recorrentes

Cada simulação reflete, portanto, não apenas o planejamento inicial, mas **um ciclo contínuo de aprimoramento** baseado na prática docente.

#### 📝 5. Sistema de Exercícios (fase atual)

Os exercícios formativos são propositalmente **simples e sem contextualização** — o foco nesta fase do projeto é a **aplicação direta de valores nas fórmulas**. São gerados **randomicamente** com parâmetros variáveis, permitindo que o estudante **refaça sempre com dados diferentes**, consolidando o domínio operacional dos conceitos.

Esta escolha é intencional: antes de avançar para problemas contextualizados, o aluno precisa **ganhar fluência no uso das equações**. A **próxima fase do projeto** prevê exatamente a criação de **exercícios contextualizados**, com situações-problema inspiradas no cotidiano e em fenômenos reais, seguindo a progressão: domínio técnico → aplicação contextualizada → análise crítica.

#### 📖 6. Material Teórico

Cada simulação inclui uma **contextualização inicial** do fenômeno físico e a **descrição detalhada das fórmulas** e grandezas envolvidas, acompanhadas de legendas interpretativas. A **teoria completa**, com deduções, demonstrações formais e aprofundamento conceitual, está disponível nas **referências bibliográficas** indicadas em cada simulação e nos materiais didáticos adotados em sala de aula.

#### 📝 7. Esclarecimento sobre a Autoria do Código

É importante ser transparente: **a maioria esmagadora do código é gerada por IAs**, a partir de minhas instruções em linguagem natural. Meu papel é:
- ✅ **Conceber** o que cada simulação deve fazer
- ✅ **Orientar** a IA com descrições precisas do resultado esperado
- ✅ **Revisar** cada bloco de código gerado, adaptando e corrigindo manualmente
- ✅ **Testar** exaustivamente em sala de aula
- ✅ **Iterar** com melhorias contínuas

O código final, portanto, é **fruto de um processo colaborativo humano-IA**, onde a direção pedagógica, a curadoria e a validação são **exclusivamente humanas**, e a produção do código é **majoritariamente assistida por IA**.

Nas simulações individuais, essa informação é registrada como comentário nos metadados do `<head>` de cada arquivo HTML.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Se você é educador, pesquisador ou desenvolvedor interessado em uso de **Tecnologias da Informação e Comunicação (TIC) na Educação**, sinta-se à vontade para:

- Relatar problemas ou sugerir melhorias através de [Issues](https://github.com/flavioambrosios/simulacoes/issues)
- Enviar *pull requests* com novas simulações ou aprimoramentos
- Adaptar o código para suas próprias salas de aula

---

## 📚 Uso em Pesquisa

Se você utilizar este material em pesquisas acadêmicas, por favor cite-o utilizando o DOI do Zenodo:

```
Ambrósio, F. (2026). Simulações Interativas de Física para o Ensino Médio. 
Zenodo. https://doi.org/10.5281/zenodo.20737876
```

