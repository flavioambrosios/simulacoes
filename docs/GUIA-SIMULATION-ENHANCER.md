# Guia do simulation-enhancer.js para professores

## Objetivo deste documento

Este guia explica, em linguagem não técnica, o que o arquivo
`_shared/simulation-enhancer.js` faz nas simulações do repositório.

O objetivo é facilitar o diálogo entre o professor e a Inteligência Artificial
na criação, revisão e evolução das simulações interativas de Física.

## O que é o simulation-enhancer.js

O `simulation-enhancer.js` é um módulo compartilhado. Ele funciona como uma
camada comum adicionada ao final das páginas das simulações.

Em vez de programar novamente os mesmos recursos em cada atividade, o enhancer
pode acrescentar automaticamente:

- salvamento do progresso;
- retomada dos exercícios;
- narração por voz;
- seleção de voz;
- leitura dos exercícios resolvidos;
- anotações de estudo;
- orientação para escrever a conclusão;
- análise automática preliminar da conclusão;
- cálculo de nota combinada;
- identificação da turma e do estudante;
- envio dos resultados para planilhas;
- lançamento de nota bimestral;
- envio de cópia por e-mail;
- controle de acesso do estudante;
- adaptação de páginas antigas ao padrão mais recente.

## Como uma simulação ativa o enhancer

A simulação deve informar seu nome e sua chave de armazenamento:

```html
<script>
window.SIMULATION_ENHANCER_CONFIG = {
    simulationName: 'Nome da Simulação',
    storageKey: 'nome-da-simulacao'
};
</script>

<script src="../_shared/simulation-enhancer.js"></script>
```

### `simulationName`

É o nome que aparece nos registros e nos envios. Ele identifica a atividade em:

- planilhas;
- mensagens;
- relatórios;
- avaliações;
- registros bimestrais.

### `storageKey`

É uma chave exclusiva usada para salvar o progresso daquela simulação.

Por exemplo, a Lei de Coulomb e o lançamento de projéteis devem ter chaves
diferentes para que o progresso de uma atividade não apareça em outra.

## Principais funções

### 1. Evita o carregamento duplicado

O enhancer verifica se já foi carregado. Assim, evita duplicar botões,
interfaces e eventos quando a página tentar incluir o arquivo mais de uma vez.

### 2. Acrescenta estilos

O arquivo cria estilos para os recursos que injeta na página, incluindo:

- barra de áudio;
- seleção de voz;
- cartão da análise da conclusão;
- botão de reinício;
- aviso de progresso salvo;
- bloco de anotações;
- guia de conclusão;
- formulário do estudante;
- mensagens de sucesso e erro;
- adaptação para telas pequenas.

### 3. Cria anotações de estudo

O enhancer acrescenta um bloco chamado **Anotações de estudo** dentro da área
de exercícios.

O estudante pode registrar:

- contas;
- observações;
- dúvidas;
- hipóteses;
- relações entre variáveis;
- conclusões parciais.

As anotações:

- ficam salvas no navegador;
- podem ser recuperadas posteriormente;
- são incluídas nos dados enviados;
- podem ajudar na elaboração da conclusão final.

O limite configurado atualmente é de 6.000 caracteres.

### 4. Mostra o aviso de progresso salvo

Quando o sistema salva o andamento, mostra uma mensagem semelhante a:

> Progresso salvo. O ponto atual dos exercícios foi guardado.

Esse aviso informa ao estudante que suas respostas não foram perdidas.

### 5. Salva automaticamente os exercícios

O enhancer pode acompanhar e salvar:

- questão atual;
- alternativa escolhida;
- respostas corretas;
- tentativas;
- questões puladas;
- conclusão;
- anotações;
- turma;
- nome;
- bimestre;
- críticas;
- sugestões.

O salvamento ocorre quando o estudante:

- escolhe uma alternativa;
- responde uma questão;
- pula uma questão;
- tenta novamente;
- escreve uma conclusão;
- escreve uma anotação;
- preenche o formulário;
- fecha a janela de exercícios;
- muda de tela.

### 6. Permite continuar de onde o estudante parou

Se houver progresso salvo, o botão principal pode mudar de **Iniciar
exercícios** para **Continuar exercícios**.

O sistema tenta recuperar:

- lista de exercícios;
- questão atual;
- respostas;
- conclusão;
- anotações;
- dados do formulário;
- tela em que o estudante estava.

Esse recurso é útil quando a aula termina antes da atividade ou quando o
estudante precisa continuar depois de uma interrupção.

### 7. Permite reiniciar os exercícios

O enhancer cria um botão **Reiniciar** e solicita confirmação antes de apagar
o progresso.

Ao reiniciar, podem ser apagados:

- respostas;
- tentativas;
- questões puladas;
- conclusão;
- anotações;
- análise automática;
- informações salvas do formulário.

### 8. Evita repetir exatamente a mesma questão

Quando a simulação permite gerar uma nova questão do mesmo tipo, o enhancer
compara a questão nova com a anterior.

Ele compara:

- tipo;
- enunciado;
- resposta;
- alternativas.

Se a questão for idêntica, tenta gerar outra dentro de um limite definido.

### 9. Cria controles de narração

O enhancer cria uma barra com:

- voltar trecho;
- iniciar ou pausar;
- avançar trecho;
- contador de trechos;
- escolha da voz.

A simulação pode fornecer textos próprios usando uma lista chamada `tracks`:

```javascript
const tracks = [
    'Primeiro trecho explicativo.',
    'Segundo trecho explicativo.',
    'Terceiro trecho explicativo.'
];
```

Se a simulação não fornecer textos, o enhancer tenta montar uma narração a
partir do conteúdo encontrado na própria página.

### 10. Usa a síntese de voz do navegador

A narração usa as vozes disponíveis no navegador.

O sistema:

- procura vozes em português;
- prioriza vozes brasileiras quando disponíveis;
- permite selecionar uma voz;
- salva a voz escolhida;
- permite pausar;
- permite retomar;
- permite avançar;
- permite voltar;
- interrompe a fala quando a página fica oculta.

### 11. Narra exercícios resolvidos

O enhancer acrescenta botões como **Ouvir resolução** aos exercícios resolvidos.

A narração pode vir de:

1. um texto preparado pelo professor;
2. o próprio texto do exercício resolvido.

Para controlar a explicação, a simulação pode definir:

```javascript
const exampleNarrations = {
    '1': 'Explicação detalhada do primeiro exemplo.',
    '2': 'Explicação detalhada do segundo exemplo.'
};
```

### 12. Adapta páginas antigas

O enhancer consegue conversar com funções já existentes em simulações antigas.

Ele pode acompanhar funções como:

- mostrar exercício;
- verificar resposta;
- pular exercício;
- mostrar conclusão;
- mostrar resultado;
- abrir exercícios;
- reiniciar exercícios;
- enviar resultados.

Assim, uma página antiga pode receber melhorias sem ser totalmente reconstruída.

### 13. Mostra a resposta correta após um erro

Quando o estudante erra uma questão, o enhancer pode acrescentar uma mensagem
como:

> Resposta correta: ...

Isso oferece um feedback mais útil do que apenas informar que a resposta está
incorreta.

### 14. Compara respostas numéricas

O sistema tenta reconhecer algumas respostas equivalentes, como:

- `10`;
- `10 N`;
- `10,0`;
- `10.0`.

Isso é útil em questões de Física, nas quais a unidade pode aparecer junto do
valor numérico.

## Formulário do estudante

### 15. Reconstrói o formulário de resultados

Quando encontra a área de resultados da simulação, o enhancer pode substituir o
formulário antigo por uma versão mais completa.

O formulário pode incluir:

- modo estudante;
- senha de acesso;
- turma ou aba da planilha;
- nome do estudante;
- opção para nome não encontrado;
- e-mail para cópia;
- bimestre;
- críticas;
- sugestões;
- conclusão final;
- orientação para escrever uma boa conclusão.

### 16. Controla o acesso do estudante

O formulário apresenta a opção:

> Sou estudante (liberar por senha)

O estudante informa uma senha antes de carregar turmas e nomes.

A senha é transformada em um código antes da comparação. A autorização fica
armazenada na sessão do navegador conforme a configuração do projeto.

A configuração atual normalmente não mantém a autorização depois do fim da
sessão.

### 17. Carrega turmas de modo protegido

O sistema pode buscar as turmas por uma API protegida.

Há três modos possíveis:

- `google-only`;
- `local-only`;
- `merge`.

O padrão atual é `google-only`, que evita usar listas locais antigas quando a
fonte protegida está disponível.

### 18. Carrega os nomes dos estudantes

Depois que a turma é escolhida, o enhancer pode carregar os nomes correspondentes.

O estudante pode:

- selecionar o próprio nome;
- informar manualmente o nome se ele não estiver na lista.

O sistema também tenta identificar automaticamente:

- série;
- turma;
- trilha;
- nome da aba.

### 19. Mantém cache temporário

As turmas e os nomes consultados podem ficar temporariamente em memória. Isso
reduz consultas repetidas enquanto o estudante preenche o formulário.

Existe também um botão para buscar as turmas novamente e atualizar a consulta.

## Conclusão e avaliação

### 20. Orienta a escrita da conclusão

O enhancer acrescenta um guia com perguntas como:

- O que você entendeu melhor?
- Quais conceitos foram estudados?
- Qual relação de causa e efeito foi observada?
- O que os cálculos revelaram?
- Qual aplicação prática pode ser citada?
- Qual é a síntese final do aprendizado?

A conclusão deixa de ser apenas um campo de preenchimento e passa a funcionar
como uma etapa de reflexão sobre a atividade.

### 21. Faz uma análise local da conclusão

O arquivo chama essa função de análise local por IA. Porém, é importante
compreender corretamente:

**não é uma IA generativa conectada ao ChatGPT, ao Copilot ou a outro modelo de
linguagem.**

A análise é feita no próprio navegador por regras simples.

Ela verifica:

- quantidade de palavras;
- quantidade de frases;
- termos relacionados ao tema;
- verbos de aprendizagem;
- conectores argumentativos;
- extensão do texto;
- presença de relações com o conteúdo da página.

Entre os termos procurados estão:

- aprendi;
- observei;
- percebi;
- concluí;
- compreendi;
- comparei;
- analisei;
- calculei;
- expliquei.

Também são procurados conectores como:

- porque;
- portanto;
- assim;
- logo;
- por isso;
- dessa forma.

### 22. Calcula indicadores da conclusão

A análise gera indicadores de:

- extensão;
- coerência temática;
- aprendizagem evidenciada;
- nota final da conclusão.

Esses indicadores devem ser tratados como uma avaliação automática preliminar.
Eles não substituem a leitura pedagógica do professor.

### 23. Calcula uma nota combinada

A configuração atual combina:

- exercícios: 50%;
- conclusão: 50%.

A fórmula é:

$$
\text{Nota final} = 0{,}5 \times \text{Nota dos exercícios}
+ 0{,}5 \times \text{Nota da conclusão}
$$

Essa proporção é uma decisão pedagógica do projeto e pode ser modificada.

### 24. Mostra a análise antes do envio

Antes de enviar, o estudante pode visualizar:

- nota da conclusão;
- extensão;
- coerência temática;
- aprendizagem evidenciada;
- nota final combinada.

## Envio e armazenamento dos resultados

### 25. Monta os dados do envio

O enhancer reúne dados como:

- nome da simulação;
- série;
- turma;
- trilha;
- bimestre;
- nome do estudante;
- acertos;
- total de questões;
- questões puladas;
- nota;
- conclusão;
- anotações;
- análise automática;
- críticas;
- sugestões;
- e-mail informado.

### 26. Envia para a planilha principal

O envio principal é feito para o endpoint configurado no arquivo. Os dados
podem alimentar registros da atividade, da turma e da avaliação.

### 27. Envia para o controle bimestral

O enhancer também pode preparar um envio específico para o lançamento da nota
bimestral.

O mapeamento configurado atualmente associa:

- 1º bimestre à coluna J;
- 2º bimestre à coluna N;
- 3º bimestre à coluna R;
- 4º bimestre à coluna V.

### 28. Mantém um backup

Além do envio principal, existe um destino de backup. Isso reduz o risco de
perder o registro caso um dos destinos falhe.

### 29. Envia cópia ao estudante

Se o estudante informar um e-mail, o enhancer pode enviar uma cópia contendo:

- identificação da atividade;
- acertos;
- nota;
- conclusão;
- nota da conclusão;
- nota combinada;
- data de envio.

### 30. Tenta novamente em caso de falha temporária

Em alguns erros temporários, o sistema pode tentar novamente o envio de e-mail.
Isso pode ocorrer em casos de:

- limite de requisições;
- cota excedida;
- timeout;
- erro de rede;
- erro temporário do serviço;
- respostas 502 ou 503.

### 31. Informa o resultado do envio

A página pode informar se:

- o destino principal confirmou o recebimento;
- o backup foi enviado;
- o lançamento bimestral foi confirmado;
- a cópia por e-mail foi confirmada;
- houve falha em algum destino.

### 32. Limpa o progresso após o envio

Depois de um envio aceito, o sistema pode:

- fechar a janela de exercícios;
- reiniciar a atividade;
- apagar o progresso salvo;
- apagar a análise salva;
- retirar o aviso de progresso.

Isso evita que o próximo estudante encontre a atividade anterior aberta no mesmo
navegador.

## O que o enhancer não faz

O enhancer não:

- cria a física da simulação;
- cria automaticamente uma animação;
- corrige fórmulas físicas;
- substitui a revisão pedagógica;
- compreende profundamente qualquer conclusão;
- garante sozinho que a planilha recebeu o dado;
- transforma uma simulação desorganizada em uma boa simulação;
- funciona completamente sem internet;
- controla o conteúdo interno do PhET incorporado.

Ele é uma camada de organização, acompanhamento e integração.

## Cuidados importantes

### A análise local não é uma IA generativa

A análise automática não deve ser apresentada como uma correção inteligente
completa. Ela utiliza contagem de palavras e procura de padrões.

A descrição mais precisa é:

> análise automática preliminar da conclusão.

### O navegador guarda dados locais

O `localStorage` pode conter:

- respostas;
- conclusão;
- anotações;
- nome;
- turma;
- e-mail;
- análise da atividade.

Se várias pessoas utilizarem o mesmo computador, pode haver dados anteriores
até que o envio ou a limpeza sejam concluídos.

### Existem configurações sensíveis no JavaScript

O arquivo contém configurações como:

- URLs de APIs;
- hashes de senha;
- token de acesso;
- e-mail do professor.

Como o JavaScript é entregue ao navegador, essas informações não devem ser
consideradas secretas em sentido absoluto.

Para maior segurança, o ideal é:

- manter a autenticação principal no servidor;
- evitar tokens permanentes no código público;
- limitar as permissões dos endpoints;
- revisar os acessos periodicamente;
- minimizar os dados pessoais armazenados.

### Existe dependência de internet

Para funcionar completamente, a atividade pode depender de:

- PhET online;
- Google Apps Script;
- planilhas;
- envio de e-mail;
- consulta de turmas;
- consulta de nomes.

O salvamento local pode funcionar sem internet, mas o envio dos resultados não.

### A codificação dos caracteres deve ser verificada

Se aparecerem textos como `ConclusÃ£o` ou `Edu��o`, há um problema de codificação.

Os arquivos devem ser salvos em UTF-8 para evitar erros em:

- nomes de turmas;
- mensagens;
- bimestres;
- textos enviados;
- filtros;
- planilhas.

## Como trabalhar com a IA

### O professor decide o conteúdo

O professor define:

- o que o estudante deve aprender;
- quais fenômenos serão estudados;
- quais perguntas serão feitas;
- qual peso terá a conclusão;
- quais dados são necessários;
- se a atividade precisa funcionar offline.

### O professor define a experiência pedagógica

O professor define:

- quais controles serão utilizados;
- quais grandezas aparecerão;
- qual sequência de exploração será seguida;
- quais mensagens serão mostradas;
- qual feedback será fornecido;
- como o estudante registrará sua conclusão.

### A IA pode cuidar da implementação

A IA pode ajudar com:

- HTML;
- CSS;
- JavaScript;
- integração com o enhancer;
- testes;
- correção de erros;
- responsividade;
- organização dos arquivos.

Uma orientação importante para usar nas solicitações é:

> A decisão pedagógica é minha. Implemente tecnicamente, preserve o padrão do repositório e me alerte quando houver uma decisão que dependa de escolha pedagógica.

## Comandos prontos para conversar com a IA

### Criar uma nova simulação

```text
Crie uma nova simulação usando o padrão do simulation-enhancer.js.
Antes de editar, explique o objetivo pedagógico, os elementos da página que
serão utilizados, os dados que serão coletados e como os exercícios serão
avaliados.
```

### Alterar o enhancer

```text
Altere apenas o arquivo _shared/simulation-enhancer.js.
Não modifique as simulações individuais.
Explique quais páginas serão afetadas, quais riscos existem e como a alteração
será testada.
```

### Alterar uma simulação

```text
Altere apenas a simulação indicada.
Preserve a estrutura do simulation-enhancer.js, a chave de armazenamento e o
fluxo de envio.
Não altere o funcionamento das outras simulações.
```

### Fazer uma análise de segurança

```text
Analise o simulation-enhancer.js procurando exposição de dados pessoais,
senhas, tokens, URLs sensíveis, armazenamento local e falhas no envio.
Não faça alterações ainda.
Apresente os riscos por ordem de prioridade e explique cada um em linguagem
para professor não programador.
```

### Fazer uma revisão pedagógica

```text
Analise a simulação como professor de Física do Ensino Médio.
Verifique se os controles, fórmulas, exercícios, feedback e conclusão estão
coerentes entre si.
Separe problemas conceituais, problemas de interface e problemas técnicos.
```

### Avaliar uma conclusão

```text
Não atribua uma nota apenas pelo tamanho do texto.
Analise se o estudante identificou o fenômeno, utilizou conceitos corretos,
relacionou causa e efeito e apresentou evidências observadas na simulação.
Informe também quais critérios foram atendidos ou não.
```

## Resumo final

O `simulation-enhancer.js` é o sistema comum de acompanhamento das atividades.
Ele:

1. adiciona recursos à página;
2. oferece narração;
3. salva o progresso;
4. permite continuar depois;
5. registra anotações;
6. orienta a conclusão;
7. faz uma análise automática preliminar;
8. combina exercícios e conclusão em uma nota;
9. identifica estudante e turma;
10. envia resultados;
11. registra o bimestre;
12. mantém destinos de backup.

A decisão sobre o que ensinar e como avaliar continua sendo do professor. A IA
pode ajudar a construir, testar e aperfeiçoar a parte técnica, mas a autoridade
pedagógica permanece com o professor.
