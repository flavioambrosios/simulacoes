# Checklist para solicitar uma nova simulacao

Use este roteiro sempre que for pedir a criacao de uma nova simulacao de Fisica.

## 1. Informacoes que devo fornecer

- [ ] Nome da simulacao:
- [ ] Tema de Fisica:
- [ ] Serie ou ano escolar:
- [ ] Objetivo de aprendizagem:
- [ ] Habilidades da BNCC, ENEM ou PAS, se aplicavel:
- [ ] Conceitos e formulas que devem aparecer:
- [ ] Tipo de simulacao:
  - [ ] PhET incorporado em iframe
  - [ ] Autoral, construida integralmente em HTML, CSS e JavaScript
- [ ] Controles que o estudante devera utilizar:
- [ ] Grandezas que deverao ser exibidas:
- [ ] Tipo de exercicios desejado:
- [ ] Necessidade de funcionamento offline:
- [ ] Necessidade de adaptacao para estudantes com necessidades especificas:
- [ ] Observacoes sobre o visual ou sobre uma simulacao existente que servira de referencia:

## 2. Comando pronto para copiar

```text
Crie uma nova simulacao interativa de Fisica para o repositorio
C:\Users\flavi\OneDrive\simulacoes.

Tema: [INFORME O TEMA]
Nome da simulacao: [INFORME O NOME]
Publico: estudantes do [ANO/SERIE] do Ensino Medio.
Objetivo de aprendizagem: [INFORME O OBJETIVO]
Habilidades relacionadas: [INFORME A BNCC, ENEM OU PAS, SE HOUVER]

Tipo de implementacao:
[ESCOLHA UMA OPCAO]
1. PhET incorporado por iframe, usando como referencia a estrutura de
   LeiDeCoulomb\LeiDeCoulomb.html.
2. Simulacao autoral, construida integralmente por mim, usando como
   referencia a estrutura de MaquinadeCarnot\CiclodeCarnot.html.

Requisitos pedagogicos:
- Explique o objetivo da atividade em linguagem clara.
- Apresente a teoria essencial sem excesso de texto.
- Mostre as formulas necessarias e identifique todas as grandezas.
- Inclua controles interativos coerentes com o fenomeno fisico.
- Mostre os valores calculados em tempo real quando isso for pedagogicamente util.
- Inclua exercicios formativos com parametros variados.
- Embaralhe as alternativas quando houver questoes de multipla escolha.
- Informe imediatamente se a resposta esta correta ou incorreta.
- Permita tentar novamente e pular uma questao quando isso fizer sentido.
- Mostre o resultado final, os acertos, as questoes puladas e a nota.
- Inclua um campo para conclusao escrita do estudante.
- Inclua exercicios resolvidos com explicacao passo a passo.

Requisitos tecnicos:
- Crie uma pasta propria para a simulacao.
- Preserve os padroes visuais e pedagogicos do repositorio.
- Use HTML, CSS e JavaScript simples e bem organizados.
- Para uma simulacao autoral, prefira Canvas 2D quando a visualizacao for bidimensional.
- Use requestAnimationFrame para animacoes continuas.
- Para uma simulacao PhET, nao tente recriar a fisica do PhET: incorpore a simulacao oficial e construa o contexto pedagogico ao redor dela.
- Configure o ../_shared/simulation-enhancer.js ao final da pagina.
- Use uma chave de armazenamento exclusiva para a simulacao.
- Nao exponha dados pessoais de estudantes no codigo.
- Mantenha compatibilidade com telas pequenas e computadores.
- Inclua labels, foco visivel, textos alternativos ou aria-label quando necessario.
- Evite dependencias externas desnecessarias.
- Nao use texto ou descricao copiados de outra simulacao.

Antes de editar:
1. Leia os dois modelos de referencia.
2. Verifique se ja existe uma simulacao semelhante no repositorio.
3. Apresente uma breve hipotese sobre a melhor arquitetura e um plano curto.
4. Se houver uma decisao importante sobre o conteudo ou a tecnologia, pergunte antes de prosseguir.

Depois de implementar:
1. Verifique se todos os controles funcionam.
2. Verifique se a animacao inicia, pausa e reinicia corretamente, quando aplicavel.
3. Teste os calculos com valores conhecidos.
4. Teste exercicios, tentativas, pulo, resultado e conclusao.
5. Verifique a responsividade em tela pequena.
6. Confira se nao existem erros no console ou referencias quebradas.
7. Execute uma validacao apropriada e informe o resultado.
8. Apresente os arquivos criados ou modificados e explique como abrir a simulacao.

Nao altere simulacoes existentes sem minha autorizacao. Nao faca refatoracoes
nao relacionadas ao pedido.
```

## 3. Conferencia antes de enviar o pedido

- [ ] Escolhi claramente entre PhET e simulacao autoral.
- [ ] Defini um objetivo de aprendizagem observavel.
- [ ] Informei a serie dos estudantes.
- [ ] Indiquei as grandezas e formulas principais.
- [ ] Expliquei quais controles serao necessarios.
- [ ] Informei se a simulacao precisa funcionar offline.
- [ ] Indiquei se desejo exercicios numericos, conceituais ou ambos.
- [ ] Informei se preciso de uma versao adaptada.

## 4. Criterio para escolher o modelo

Use o modelo PhET quando ja existir uma simulacao oficial adequada e o objetivo
principal for organizar a atividade, os exercicios, o feedback e a coleta
pedagogica.

Use o modelo autoral quando for necessario controlar completamente a fisica,
a animacao, os graficos, os controles ou o funcionamento offline.

## 5. Resultado esperado

Ao final, a nova simulacao devera ser uma atividade completa, e nao apenas uma
animacao: deve apresentar um objetivo claro, permitir exploracao, oferecer
feedback, propor exercicios e registrar uma conclusao do estudante.
