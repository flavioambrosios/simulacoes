---
name: chat-context-recap
description: 'Identifica qual e este chat e resume a ultima interacao do usuario na conversa atual. Use quando precisar recuperar contexto recente, explicar o objetivo em andamento, apontar o arquivo ativo, o workspace atual e o pedido mais recente do usuario.'
argument-hint: 'Pergunta sobre o contexto atual do chat ou a ultima interacao do usuario'
user-invocable: true
disable-model-invocation: false
---

# Chat Context Recap

## O que esta skill faz

Esta skill ajuda a responder perguntas como:

- Que chat e este?
- Qual foi a minha ultima interacao?
- Em que arquivo ou projeto estamos trabalhando?
- Qual tarefa esta em andamento agora?

Ela deve usar apenas o contexto realmente disponivel na conversa atual e no workspace aberto. Se nao houver historico suficiente, deve dizer isso explicitamente em vez de inventar informacoes.

## Quando usar

Use esta skill quando o usuario pedir para:

- identificar o chat atual;
- resumir a conversa corrente;
- recuperar a ultima mensagem enviada pelo usuario;
- explicar o contexto do arquivo ou workspace ativo;
- retomar o trabalho depois de uma interrupcao.

## Procedimento

1. Leia a conversa atual e identifique o pedido mais recente do usuario.
2. Identifique o arquivo ativo, o workspace aberto e qualquer contexto de ambiente disponivel.
3. Resuma em linguagem simples qual tarefa esta sendo feita neste chat.
4. Informe qual foi a ultima interacao do usuario dentro da conversa atual.
5. Se o usuario perguntar por um chat anterior ou historico fora desta conversa, explique a limitacao claramente.
6. Se houver ambiguidade, responda com as informacoes confirmadas e destaque o que nao pode ser verificado.

## Regras de decisao

- Se a pergunta for "que chat e este?": descreva o contexto atual da conversa, incluindo workspace, arquivo ativo e objetivo em andamento.
- Se a pergunta for "qual foi a minha ultima interacao?": cite e resuma a ultima mensagem do usuario nesta conversa atual.
- Se o usuario parecer perguntar sobre outra sessao ou outro chat: deixe claro que a resposta vale apenas para o historico disponivel nesta conversa.
- Se nao houver contexto suficiente: informe a falta de contexto e peça ao usuario que cole a parte relevante.

## Criterios de qualidade

- Nao inventar historico ausente.
- Distinguir fatos observaveis de inferencias.
- Responder de forma curta, clara e verificavel.
- Priorizar o pedido mais recente do usuario.

## Formato sugerido de resposta

Use este formato quando fizer sentido:

1. Este chat: resumo do objetivo atual.
2. Workspace atual: pasta e arquivo ativo, se disponiveis.
3. Sua ultima interacao: ultima mensagem enviada pelo usuario nesta conversa.
4. Limites: o que nao pode ser confirmado fora do historico atual.