# Sistema de Notas do Professor

## Folha de rosto da implantação

Professor responsável: ______________________________________

Componente curricular: ______________________________________

Turmas atendidas: __________________________________________

Data de início: ____/____/________

Objetivo do ciclo:
- Implantar um fluxo simples e seguro de registro de notas das simulações.
- Garantir rastreabilidade por turma e histórico de envios.
- Evoluir para envio de confirmação por e-mail após validação inicial.

Arquivos de referência:
- [docs/GUIA-CRIAR-SISTEMA-NOTAS-PROPRIO.md](GUIA-CRIAR-SISTEMA-NOTAS-PROPRIO.md)
- [templates/simulacao-esqueleto/SimulacaoModelo.html](../templates/simulacao-esqueleto/SimulacaoModelo.html)
- [AvaliacaoBimestralEducacaoDigital/google-apps-script.gs](../AvaliacaoBimestralEducacaoDigital/google-apps-script.gs)

---

## Checklist de 1 página

## Etapa 1: Planilha
- [ ] Criei a planilha Google do professor.
- [ ] Criei abas de turmas (exemplo: 1o ano A, 2o ano B).
- [ ] Criei a aba Historico Avaliacoes.
- [ ] Estruturei bySheet, bySerieTurma e byTrilha (se usar lista protegida).

## Etapa 2: Apps Script
- [ ] Colei o script base em Apps Script.
- [ ] Configurei SPREADSHEET_ID.
- [ ] Configurei HISTORY_SHEET_NAME.
- [ ] Configurei DEFAULT_SCORE_HEADER.
- [ ] Configurei ACCESS_TOKEN_HASH.
- [ ] Deixei EMAIL_CONFIRMATION_ENABLED em false para a fase inicial.

## Etapa 3: Deploy
- [ ] Publiquei como Aplicativo da Web.
- [ ] Executei como eu mesmo.
- [ ] Liberei acesso para qualquer pessoa com o link.
- [ ] Copiei a URL final com /exec.

## Etapa 4: Integração na simulação
- [ ] Atualizei APPS_SCRIPT_URL no template.
- [ ] Atualizei EMAIL_SCRIPT_URL (se aplicável).
- [ ] Mantive compatibilidade com enhancer e persistência.

## Etapa 5: Teste de validação
- [ ] Respondi exercícios até o resumo final.
- [ ] Enviei resultado com nome, série e turma.
- [ ] Confirmei nota na aba da turma.
- [ ] Confirmei registro na aba Historico Avaliacoes.
- [ ] Testei fechamento e reabertura do modal com persistência de progresso.

## Etapa 6: E-mail de confirmação
- [ ] Ativei EMAIL_CONFIRMATION_ENABLED somente após validação da planilha.
- [ ] Autorizei MailApp no Apps Script.
- [ ] Executei teste de envio de e-mail.
- [ ] Validei mensagem recebida pelo estudante.

## Etapa 7: LGPD e publicação
- [ ] Não publiquei lista nominal em arquivo público.
- [ ] Não compartilhei hash/token em apresentação.
- [ ] Revisei anonimização antes de divulgar resultados.
- [ ] Apliquei o checklist de publicação.

Referência:
- [docs/CHECKLIST-ANONIMIZACAO-E-PUBLICACAO.md](CHECKLIST-ANONIMIZACAO-E-PUBLICACAO.md)

---

## Critérios para considerar implantação concluída
- [ ] O envio da simulação grava na planilha em todas as turmas-alvo.
- [ ] O histórico registra data, estudante, turma e nota.
- [ ] O professor consegue repetir o processo sem apoio técnico externo.
- [ ] A rotina quinzenal de revisão está agendada.

Assinatura do professor: _____________________________________

Data de conclusão: ____/____/________
