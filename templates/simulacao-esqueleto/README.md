# Esqueleto de Simulação

Este pacote foi criado para iniciar uma nova simulação sem precisar começar do zero.

## O que vem pronto
- Estrutura HTML base da simulação.
- Área visual da simulação (canvas + painel de métricas).
- Botões de teoria, exercícios e resolvidos.
- Modais com ids compatíveis com o enhancer.
- Integração com [_shared/simulation-enhancer.js](../../_shared/simulation-enhancer.js).
- Lógica de exercícios compatível com persistência do enhancer.
- Indicação de acerto/erro, botão tentar novamente e variação da mesma questão.
- Início de integração para envio de dados à planilha e solicitação de e-mail de confirmação.
- Arquivo separado para rascunho de exercícios.

## Como usar
1. Copie esta pasta para a raiz do projeto com o nome da nova simulação.
2. Renomeie o arquivo SimulacaoModelo.html para o nome final.
3. Ajuste no HTML:
- simulationName
- storageKey
- título da página
- textos de teoria
4. Edite [exercicios-modelo.js](exercicios-modelo.js) com os exercícios do tema.
5. Configure as URLs de envio no HTML (APPS_SCRIPT_URL e EMAIL_SCRIPT_URL).
5. Teste abrindo o HTML no navegador.

## Convenções recomendadas
- Nome da pasta: sem espaços e sem acentos, por exemplo: LeiDeGauss.
- storageKey: em minúsculas com hífen, por exemplo: lei-de-gauss.
- Um objetivo principal por simulação e de 3 a 8 exercícios formativos.

## Checklist mínimo antes de publicar
- Objetivos de aprendizagem explícitos.
- Pelo menos 1 exemplo guiado e 1 exercício aplicado.
- Texto de conclusão final do estudante habilitado.
- Fluxo de envio de resultados validado.
- Revisão de anonimização dos dados.
