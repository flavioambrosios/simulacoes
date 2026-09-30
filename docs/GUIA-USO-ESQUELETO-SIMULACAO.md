# Guia Rápido: Uso do Esqueleto de Simulação

## Onde está o esqueleto
Pasta:
- [templates/simulacao-esqueleto](../templates/simulacao-esqueleto)

Arquivos principais:
- [templates/simulacao-esqueleto/SimulacaoModelo.html](../templates/simulacao-esqueleto/SimulacaoModelo.html)
- [templates/simulacao-esqueleto/exercicios-modelo.js](../templates/simulacao-esqueleto/exercicios-modelo.js)
- [templates/simulacao-esqueleto/README.md](../templates/simulacao-esqueleto/README.md)

## Fluxo de criação para professor colaborador
1. Copiar a pasta simulacao-esqueleto para a raiz do projeto.
2. Renomear a pasta para o tema (exemplo: LeiDeGauss).
3. Renomear SimulacaoModelo.html.
4. Editar:
- titulo e objetivo da atividade;
- variaveis e visualizacao;
- texto de teoria;
- exercicios-modelo.js.
5. Ajustar em SIMULATION_ENHANCER_CONFIG:
- simulationName
- storageKey
6. Configurar no HTML as URLs:
- APPS_SCRIPT_URL
- EMAIL_SCRIPT_URL
7. Testar abertura local no navegador.
7. Revisar pedagogia e publicar.

## Critérios mínimos para liberar uma nova simulação
- Objetivo claro em linguagem de aluno.
- Interação principal funcional.
- Pelo menos 3 exercícios com feedback.
- 2 exercícios resolvidos com passo a passo.
- Conclusão final do estudante ativa.
- Fluxo de envio testado em ambiente de validação.
- Persistência do progresso validada (fechar e reabrir modal de exercícios).

## Sugestão para oficina com colegas (30 minutos)
1. 10 min: copiar e renomear o esqueleto.
2. 10 min: editar teoria e exercícios.
3. 10 min: testar e coletar dúvidas.
