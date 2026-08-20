# Guia para criação de repositórios educacionais

## Apresentação

Este guia foi elaborado a partir da experiência de criação e organização de um
repositório de simulações interativas de Física.

O objetivo é ajudar professores de outras áreas a criar seus próprios
repositórios educacionais digitais, com atividades interativas, exercícios,
registro de resultados, versões adaptadas e documentação.

A proposta é que, futuramente, diferentes repositórios possam ser integrados em
um **Hub de Ciências**.

A ideia central é:

> O professor define o que o estudante deve aprender. A tecnologia e a
> Inteligência Artificial ajudam a construir, testar, organizar e registrar a
> atividade.

## O caminho já iniciado

A preparação inicial inclui:

- instalação do Visual Studio Code;
- criação de uma conta no GitHub;
- instalação do GitHub Desktop;
- criação de um repositório próprio;
- organização das atividades em pastas;
- publicação das páginas na internet;
- uso de uma planilha para receber os resultados.

As próximas etapas principais são:

1. criar a planilha de resultados;
2. iniciar o padrão das atividades;
3. organizar os recursos compartilhados;
4. testar com estudantes;
5. documentar o processo;
6. preparar a integração futura com o Hub de Ciências.

## 1. Criar a planilha pedagógica

Antes de programar, o professor deve decidir quais informações realmente
precisa receber.

### Campos recomendados

- atividade;
- data e horário;
- área do conhecimento;
- disciplina;
- série;
- turma;
- estudante;
- acertos;
- total de questões;
- questões puladas;
- nota;
- conclusão escrita;
- críticas;
- sugestões;
- bimestre ou período;
- versão da atividade.

### Organização recomendada

É melhor separar a planilha em três partes:

#### Dados brutos

Recebe os registros enviados pelas atividades. Essa área deve ser alterada o
mínimo possível.

#### Análises

Contém fórmulas, gráficos e indicadores como:

- número de participantes;
- média da turma;
- percentual de conclusão;
- média de acertos;
- questões com maior dificuldade;
- comparação entre atividades;
- distribuição das notas.

#### Configuração

Pode conter:

- turmas;
- séries;
- períodos;
- atividades;
- pesos de avaliação;
- nomes de abas;
- parâmetros de integração.

### Cuidados com dados pessoais

O professor deve definir antes:

- quem terá acesso aos dados;
- quais dados são realmente necessários;
- por quanto tempo serão mantidos;
- como serão anonimizados para divulgação;
- como um registro poderá ser corrigido ou removido.

A regra geral é:

> Não coletar um dado pessoal apenas porque é tecnicamente possível coletá-lo.

## 2. Criar a estrutura do repositório

Uma estrutura inicial pode ser:

```text
meu-repositorio/
|-- index.html
|-- README.md
|-- docs/
|-- _shared/
|   |-- simulation-enhancer.js
|   |-- index-thumbs/
|-- NomeDaAtividade/
|   |-- NomeDaAtividade.html
|   |-- NomeDaAtividade_AdaptadaN2.html
|   `-- ...
```

### Função de cada parte

- `index.html`: catálogo das atividades;
- `README.md`: apresentação e instruções do repositório;
- `docs/`: guias, checklists, planejamentos e políticas;
- `_shared/`: recursos usados por várias atividades;
- pasta da atividade: arquivos específicos daquela atividade;
- `index-thumbs/`: miniaturas para o catálogo.

## 3. Criar um padrão mínimo de atividade

Cada atividade deveria conter:

- título claro;
- objetivo de aprendizagem;
- público ou série indicada;
- teoria essencial;
- simulação ou visualização;
- controles coerentes com o fenômeno;
- fórmulas necessárias;
- roteiro de exploração;
- exercícios formativos;
- exercícios resolvidos;
- feedback imediato;
- conclusão escrita;
- registro dos resultados;
- versão adaptada quando necessário.

A atividade não deve ser apenas uma animação. Ela deve formar uma sequência:

```text
Objetivo -> Exploração -> Observação -> Exercícios -> Conclusão -> Registro
```

## 4. Escolher a tecnologia

### PhET incorporado

Use essa opção quando já existir uma simulação PhET adequada.

Vantagens:

- simulação física já desenvolvida;
- controles confiáveis;
- menor tempo de desenvolvimento;
- possibilidade de concentrar o trabalho na mediação pedagógica.

A página ao redor do PhET deve fornecer:

- objetivo;
- roteiro;
- teoria;
- exercícios;
- exercícios resolvidos;
- conclusão;
- registro dos resultados.

### Simulação autoral

Use essa opção quando for necessário controlar completamente:

- a física;
- a animação;
- os gráficos;
- os controles;
- o funcionamento offline;
- a sequência visual da atividade.

Para visualizações bidimensionais, o Canvas 2D costuma ser uma escolha
adequada. Para visualizações tridimensionais, pode ser necessário utilizar
Three.js ou outra tecnologia apropriada.

## 5. Utilizar o simulation-enhancer

O `simulation-enhancer.js` deve ser tratado como uma infraestrutura compartilhada.

Ele pode fornecer:

- salvamento automático do progresso;
- retomada dos exercícios;
- botão de reinício;
- anotações de estudo;
- narração por síntese de voz;
- áudio dos exercícios resolvidos;
- formulário padronizado;
- orientação para a conclusão;
- análise automática preliminar da conclusão;
- cálculo de nota combinada;
- identificação de turma e estudante;
- envio para planilhas;
- lançamento de nota por período;
- cópia por e-mail;
- controle de acesso;
- compatibilidade com versões antigas.

### Configuração mínima

```html
<script>
window.SIMULATION_ENHANCER_CONFIG = {
    simulationName: 'Nome da Atividade',
    storageKey: 'nome-da-atividade'
};
</script>

<script src="../_shared/simulation-enhancer.js"></script>
```

### Regras importantes

- `simulationName` deve identificar corretamente a atividade;
- `storageKey` deve ser exclusiva;
- não reutilizar a chave de outra atividade;
- não alterar o enhancer sem avaliar quais páginas serão afetadas;
- testar atividades antigas depois de qualquer alteração;
- manter a lógica pedagógica separada da infraestrutura compartilhada.

### O que o enhancer não substitui

O enhancer não:

- define o objetivo pedagógico;
- corrige fórmulas físicas;
- cria uma boa animação sozinho;
- substitui a revisão do professor;
- compreende profundamente uma conclusão;
- garante sozinho o recebimento pela planilha.

A análise automática da conclusão deve ser apresentada como uma avaliação
preliminar, nunca como substituição da leitura docente.

## 6. Preparar áudio e acessibilidade

Desde o início, a atividade deve considerar diferentes formas de acesso.

Recomendações:

- usar linguagem direta;
- dividir instruções longas em etapas;
- acrescentar `label` aos campos;
- usar `title` descritivo nos iframes;
- manter contraste suficiente;
- permitir navegação por teclado;
- usar botões verdadeiros para ações;
- oferecer áudio inicial;
- oferecer áudio dos exercícios resolvidos;
- evitar depender apenas de cores;
- testar em telas pequenas.

## 7. Criar versões adaptadas

A versão adaptada não deve ser apenas uma cópia com outro título.

Ela pode conter:

- menos exercícios;
- enunciados mais curtos;
- instruções passo a passo;
- fórmulas essenciais destacadas;
- exemplos resolvidos mais diretos;
- maior apoio textual;
- áudio mais orientado;
- controles mais simples;
- conclusão guiada.

A versão principal e a versão adaptada devem manter a mesma ideia central, mas
podem ter diferentes níveis de apoio.

## 8. Trabalhar com Inteligência Artificial

### O professor decide

O professor define:

- o conteúdo;
- o objetivo de aprendizagem;
- a série;
- os fenômenos estudados;
- as fórmulas;
- as perguntas;
- os critérios de avaliação;
- os dados necessários;
- o nível de adaptação.

### A IA pode ajudar

A IA pode auxiliar em:

- criação de HTML, CSS e JavaScript;
- organização dos arquivos;
- criação de exercícios;
- elaboração de exemplos resolvidos;
- revisão da interface;
- correção de erros;
- testes de responsividade;
- integração com o enhancer;
- documentação;
- atualização do índice.

### Comando recomendado

```text
A decisão pedagógica é minha.
Implemente tecnicamente a atividade, preserve o padrão do repositório,
explique as decisões importantes e me alerte quando houver algum risco
conceitual, de acessibilidade, de segurança ou de coleta de dados.
Antes de editar, leia os modelos de referência e apresente uma hipótese curta
sobre a melhor arquitetura.
Depois de editar, valide os controles, os cálculos, os exercícios, o envio e a
responsividade.
```

## 9. Criar um template para colegas

Para encurtar o caminho, é recomendável criar um repositório-modelo com:

- `index.html` pronto;
- uma atividade principal;
- uma versão adaptada;
- planilha-modelo;
- `README.md` orientado ao professor;
- `simulation-enhancer.js`;
- miniatura de exemplo;
- checklist de publicação;
- checklist de testes;
- política básica de dados.

O professor que receber esse modelo deverá substituir principalmente:

- tema;
- textos;
- imagens;
- fórmulas;
- perguntas;
- respostas;
- controles;
- nome da atividade;
- chave de armazenamento.

## 10. Testar antes de publicar

### Teste técnico

- [ ] A página abre sem erro.
- [ ] A simulação carrega.
- [ ] Os iframes possuem títulos descritivos.
- [ ] Os controles funcionam.
- [ ] A animação inicia, pausa e reinicia quando aplicável.
- [ ] Os cálculos foram conferidos com valores conhecidos.
- [ ] As respostas corretas dos exercícios estão corretas.
- [ ] Tentar novamente funciona.
- [ ] Pular questão funciona quando previsto.
- [ ] Reiniciar apaga o progresso corretamente.
- [ ] A conclusão é salva.
- [ ] O áudio inicial funciona.
- [ ] O áudio dos exemplos resolvidos funciona.
- [ ] O envio apresenta uma mensagem clara.
- [ ] A página funciona em tela pequena.
- [ ] Os links do índice funcionam.

### Teste pedagógico

- [ ] O objetivo é observável.
- [ ] A teoria corresponde à simulação.
- [ ] Os controles correspondem aos conceitos estudados.
- [ ] Os exercícios podem ser respondidos a partir da exploração.
- [ ] Os exemplos resolvidos mostram o raciocínio.
- [ ] O feedback ajuda o estudante a aprender.
- [ ] A conclusão pede evidências da atividade.
- [ ] A nota não depende apenas do tamanho do texto.

### Teste de dados

- [ ] Foram coletados apenas os dados necessários.
- [ ] O formulário informa o objetivo da coleta.
- [ ] Os dados pessoais não estão expostos no código público.
- [ ] A planilha recebeu um teste controlado.
- [ ] O backup foi verificado.
- [ ] Os dados podem ser agregados para divulgação.

## 11. Organização do futuro Hub de Ciências

No início, é mais seguro manter repositórios separados por área:

- Física;
- Química;
- Biologia;
- Matemática;
- outras áreas interessadas.

O Hub pode começar como um catálogo integrado, apontando para as atividades de
cada repositório. Não é necessário juntar todos os códigos em um único
repositório logo no início.

### Metadados recomendados

Cada atividade pode possuir informações padronizadas:

```javascript
{
    titulo: 'Lei de Coulomb',
    area: 'Física',
    disciplina: 'Física',
    tema: 'Eletricidade',
    serie: '2º ano',
    tecnologia: 'PhET',
    tipo: 'simulação',
    url: '...',
    versaoAdaptada: '...',
    habilidades: ['...']
}
```

Com esses dados, o Hub poderá filtrar atividades por:

- área;
- disciplina;
- série;
- tema;
- habilidade;
- tecnologia;
- tipo de atividade;
- versão adaptada.

## 12. Estratégia de implantação

### Fase 1: atividade-piloto

Cada professor cria uma única atividade pequena.

### Fase 2: teste real

A atividade é aplicada a um grupo reduzido de estudantes.

### Fase 3: revisão

O professor analisa:

- dificuldades dos estudantes;
- questões mal compreendidas;
- problemas técnicos;
- qualidade das conclusões;
- funcionamento do envio.

### Fase 4: publicação

A atividade revisada é documentada e adicionada ao índice.

### Fase 5: integração

As atividades passam a ser catalogadas no Hub de Ciências.

## 13. Recomendação final

O caminho mais eficiente é começar pequeno, mas já seguir um padrão comum.

Cada professor deve criar:

1. um repositório organizado;
2. uma planilha simples e protegida;
3. uma atividade-piloto;
4. uma versão adaptada;
5. documentação curta;
6. um índice de atividades;
7. um checklist de testes.

A experiência acumulada com simulações, enhancer, planilhas, versões adaptadas
e catálogo pode se transformar em um modelo institucional de produção de
recursos educacionais digitais.

O futuro Hub de Ciências poderá ser construído sobre essa base comum, mantendo
a autonomia de cada professor e permitindo que as atividades sejam encontradas,
compartilhadas e reutilizadas por outras escolas.
