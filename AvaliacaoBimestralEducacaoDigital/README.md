# Avaliação Bimestral - Educação Digital

Aplicação local em HTML para aplicar uma prova de 100 questões do tipo certo ou errado, organizadas em 50 pares contraditórios.

## O que já está pronto

- Tela inicial com série, turma, trilha e nome do estudante.
- Lista de nomes preparada para ser carregada a partir da planilha.
- Prova com 100 itens interligando IA, trabalho na adolescência e juventude, saúde mental e redes sociais.
- Cálculo da nota em escala de 0 a 10 considerando a regra dos pares.
- Script do Google Apps Script para registrar a coluna prova e criar um histórico detalhado.
- Campo opcional de email para confirmação ao estudante.
- Sincronizador local para atualizar o arquivo alunos.js a partir da planilha online.

## Como usar

1. Abra o arquivo index.html no navegador.
2. Selecione série, turma, trilha e o nome do estudante.
3. Responda às 100 questões.
4. Ao finalizar, a nota aparece na tela.

## Como ligar à planilha

1. Importe o arquivo Excel para o Google Planilhas ou confirme qual planilha online será usada como base.
2. Abra Extensões > Apps Script nessa planilha.
3. Copie o conteúdo de google-apps-script.gs.
4. Substitua COLE_AQUI_O_ID_DA_PLANILHA pelo ID da planilha.
5. Implante como aplicativo da web com acesso para qualquer pessoa com o link.
6. Copie a URL publicada e cole na constante APPS_SCRIPT_URL em app.js.

## Observação importante

Um arquivo HTML aberto no navegador não consegue gravar diretamente em um .xlsx local do computador. Por isso, a gravação foi preparada pelo mesmo modelo já usado nas simulações: navegador + Google Apps Script + planilha online.

## Email de confirmação

O campo de email do estudante já existe na avaliação.

Para o email ser enviado de verdade, o Apps Script precisa estar com a versão mais nova do arquivo google-apps-script.gs e ser publicado novamente como aplicativo da web.

## Como atualizar o arquivo alunos.js

Depois que um estudante novo for incluído na planilha, rode este comando na pasta do projeto:

```powershell
py -3 .\sync_alunos_js.py
```

O script vai:

1. ler a URL do Apps Script em app.js;
2. pedir ao Apps Script a base atual de estudantes;
3. sobrescrever o arquivo alunos.js com a base nova.

Se quiser informar a URL manualmente:

```powershell
py -3 .\sync_alunos_js.py --url "SUA_URL_DO_APPS_SCRIPT"
```
