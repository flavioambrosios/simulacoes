# Guia: Criar Seu Próprio Sistema de Notas (Professor)

Este guia foi feito para professor iniciante que quer montar seu próprio fluxo de notas, sem depender de programação avançada.

## Objetivo
Você vai configurar:
1. planilha de notas no Google;
2. Apps Script para receber dados das simulações;
3. início do envio de e-mail de confirmação;
4. integração com o template de simulação.

---

## 1) Arquitetura mínima do sistema

```text
Simulação (HTML + enhancer)
        |
        | envia JSON (POST)
        v
Apps Script (Web App)
        |
        | grava
        v
Google Planilhas (abas por turma + histórico)
        |
        | opcional
        v
Envio de e-mail de confirmação
```

---

## 2) Estrutura da planilha

Crie uma planilha Google com estas abas:

1. Aba de cada turma
- Exemplo: 1o ano A, 2o ano B, 3o ano C.
- Linha 1: cabeçalhos.
- Coluna A: nome do estudante.
- Coluna de nota: por padrão, use um cabeçalho como prova.

2. Aba de histórico
- Nome sugerido: Historico Avaliacoes.
- Essa aba guarda cada envio com data/hora, nome, turma, nota, conclusão e observações.

3. Abas de apoio para lista de alunos (opcional, recomendado)
- bySheet
- bySerieTurma
- byTrilha

Formato:
- Coluna A: chave.
- Coluna B em diante: nomes.

---

## 3) Configurar o Apps Script

Use como base:
- [AvaliacaoBimestralEducacaoDigital/google-apps-script.gs](../AvaliacaoBimestralEducacaoDigital/google-apps-script.gs)

Passos:
1. Na planilha, clique em Extensões > Apps Script.
2. Cole o script-base.
3. Ajuste constantes principais:
- SPREADSHEET_ID
- HISTORY_SHEET_NAME
- DEFAULT_SCORE_HEADER
- ACCESS_TOKEN_HASH
- EMAIL_CONFIRMATION_ENABLED

Dica prática:
- Para começar simples, deixe EMAIL_CONFIRMATION_ENABLED como false e valide primeiro a gravação na planilha.

---

## 4) Publicar como Web App

1. Clique em Implantar > Nova implantação.
2. Tipo: Aplicativo da Web.
3. Executar como: você.
4. Acesso: qualquer pessoa com o link.
5. Copie a URL final terminando em /exec.

Guarde essa URL. Ela será usada na simulação como endpoint de notas.

---

## 5) Payload mínimo aceito pelo sistema

Seu frontend deve enviar, no mínimo:
- estudante
- serie
- turma
- nota

Exemplo completo (recomendado):

```json
{
  "avaliacao": "Simulação - Modelo",
  "simulacao": "Nome da Simulação",
  "estudante": "NOME DO ALUNO",
  "serie": "2o ano",
  "turma": "A",
  "nota": 8.5,
  "acertosIndividuais": 7,
  "totalQuestoes": 10,
  "questoes_puladas": 1,
  "conclusao": "Aprendi que...",
  "criticas": "...",
  "sugestoes": "...",
  "email": "aluno@email.com",
  "respostas": []
}
```

---

## 6) Integrar com a simulação

No template:
- [templates/simulacao-esqueleto/SimulacaoModelo.html](../templates/simulacao-esqueleto/SimulacaoModelo.html)

Atualize:
1. APPS_SCRIPT_URL com a URL do seu Web App.
2. EMAIL_SCRIPT_URL (se usar endpoint separado para e-mail).

Se for usar apenas um endpoint único (script principal), você pode manter o envio de e-mail no próprio Apps Script principal.

---

## 7) Primeiro teste (roteiro de 10 minutos)

1. Abrir simulação.
2. Responder exercícios até o resumo final.
3. Preencher nome, série e turma.
4. Clicar em Enviar resultados.
5. Verificar:
- nota na aba da turma;
- registro na aba Historico Avaliacoes.

Se falhar:
- revisar URL /exec;
- revisar SPREADSHEET_ID;
- revisar permissões do deploy;
- abrir o endpoint no navegador para ver mensagem do script ativo.

---

## 8) Subir de nível: e-mail de confirmação

Quando a gravação já estiver estável:
1. Ative EMAIL_CONFIRMATION_ENABLED no script.
2. Faça a autorização do MailApp na conta Google.
3. Rode a função de teste de e-mail no menu do script.
4. Só depois habilite para estudantes.

---

## 9) Segurança e LGPD (mínimo obrigatório)

1. Não publicar lista nominal em arquivos públicos.
2. Evitar compartilhar token/hash em slide ou vídeo.
3. Trabalhar com dados agregados em apresentações externas.
4. Revisar antes de publicar com:
- [docs/CHECKLIST-ANONIMIZACAO-E-PUBLICACAO.md](CHECKLIST-ANONIMIZACAO-E-PUBLICACAO.md)

---

## 10) Plano recomendado para professores colaboradores

Semana 1:
- montar planilha e publicar Web App.

Semana 2:
- integrar 1 simulação piloto e validar envios.

Semana 3:
- ativar e-mail de confirmação.

Semana 4:
- revisar dados e consolidar rotina.

Com isso, cada professor passa a ter autonomia para seu próprio sistema de notas, mantendo compatibilidade com o hub.
