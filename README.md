# Simulações Interativas de Física

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14860563.svg)](https://doi.org/10.5281/zenodo.14860563)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/hosted%20on-GitHub%20Pages-blue)](https://flavioambrosios.github.io/simulacoes/)

Um conjunto de simulações interativas para o ensino de Física no Ensino Médio, desenvolvidas para uso em sala de aula com estudantes do **CEAN - Centro de Ensino Médio Asa Norte** (Brasília-DF). As simulações combinam visualizações em Canvas/Three.js com exercícios formativos, narração por síntese de voz e análise automatizada de conclusões escritas.

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

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14860563.svg)](https://doi.org/10.5281/zenodo.14860563)

Este conjunto de simulações está registrado no **Zenodo** com DOI: [10.5281/zenodo.14860563](https://doi.org/10.5281/zenodo.14860563). O registro assegura a **autoria e data de criação** do trabalho, servindo como referência permanente para citações acadêmicas.

### Créditos

- **Simulações PhET Interactive Simulations** ([University of Colorado Boulder](https://phet.colorado.edu/)) — utilizadas sob licença CC-BY 4.0 em algumas simulações (Corpo Negro, Efeito Fotoelétrico, Lei de Faraday)
- **Three.js** — biblioteca 3D utilizada em algumas simulações (Espectrômetro de Massa, Estrelas, Força Magnética, entre outras)
- **Google Apps Script** — para coleta e armazenamento de dados dos alunos

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
Zenodo. https://doi.org/10.5281/zenodo.14860563
```
