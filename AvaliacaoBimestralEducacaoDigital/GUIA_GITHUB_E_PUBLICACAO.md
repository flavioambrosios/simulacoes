# Guia de GitHub e Publicação Online

## 1. O que já está pronto

- A avaliação é um site estático em HTML, CSS e JavaScript.
- O lançamento das notas é feito pelo Apps Script publicado como Web App.
- Isso significa que a parte online da prova pode ficar no GitHub Pages e a gravação das notas continua no Google Apps Script.

## 2. Como atualizar o GitHub

No terminal, dentro da pasta do projeto:

```powershell
cd "C:\Users\flavi\OneDrive\simulacoes\AvaliacaoBimestralEducacaoDigital"
git init
git add .
git commit -m "Atualiza avaliação bimestral"
```

Depois, crie um repositório no GitHub e conecte o projeto:

```powershell
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
git push -u origin main
```

Se o repositório já existir:

```powershell
cd "C:\Users\flavi\OneDrive\simulacoes\AvaliacaoBimestralEducacaoDigital"
git add .
git commit -m "Atualiza avaliação bimestral"
git push
```

## 3. Como publicar a avaliação online

Opção mais simples: GitHub Pages.

### Passos

1. Abra o repositório no GitHub.
2. Vá em Settings.
3. Vá em Pages.
4. Em Source, escolha Deploy from a branch.
5. Selecione a branch main.
6. Selecione a pasta /(root).
7. Salve.

Depois de alguns minutos, a avaliação ficará online em um endereço parecido com este:

```text
https://SEU_USUARIO.github.io/NOME_DO_REPOSITORIO/
```

## 4. O que continua funcionando online

- A avaliação abre normalmente no navegador.
- A correção continua local no JavaScript.
- O envio da nota continua indo para o Apps Script.
- O Apps Script continua gravando na planilha Notas CEAN 2026.

## 5. Sobre o email de confirmação

O código local já foi preparado para aceitar email do estudante no formulário.

Para isso funcionar de verdade, você ainda precisa:

1. Colar a versão mais nova do arquivo google-apps-script.gs no projeto do Apps Script.
2. Salvar.
3. Fazer uma nova implantação da Web App.

Sem esse novo redeploy, a avaliação envia a nota para a planilha, mas o email de confirmação ainda não será disparado pelo Apps Script.

## 6. Sobre novos nomes e o arquivo alunos.js

Hoje existem três situações diferentes:

### Situação 1. Nome novo digitado na avaliação

- O Apps Script já consegue criar o estudante na planilha.
- A avaliação também passa a lembrar esse nome na lista durante a sessão atual.

### Situação 2. Atualizar o arquivo alunos.js de forma permanente

O arquivo alunos.js é estático. Ele não se altera sozinho só porque um nome foi incluído na planilha.

Então, para atualizar permanentemente, é preciso regenerar esse arquivo.

### Situação 3. Melhor solução futura

A melhor solução é deixar de depender do alunos.js como lista fixa e passar a ler a lista diretamente da planilha via Apps Script.

Assim, qualquer novo estudante adicionado na planilha apareceria automaticamente na avaliação depois de recarregar a página.

## 7. Jeito prático de manter alunos.js atualizado

Você pode usar este fluxo:

1. Acrescenta o estudante novo na planilha.
2. Atualiza a base local que gera o arquivo alunos.js.
3. Sobrescreve o arquivo alunos.js com a versão nova.
4. Faz commit e push no GitHub.

## 8. Fluxo recomendado para uso real

1. Corrigir ou cadastrar estudante na planilha.
2. Aplicar ou conferir a formatação das turmas.
3. Testar a URL do Apps Script.
4. Publicar a avaliação no GitHub Pages.
5. Fazer um teste real com um aluno.
6. Conferir a aba da turma e a aba de histórico.

## 9. Próximo passo recomendado

Se você quiser eliminar a manutenção manual do alunos.js, o próximo ajuste ideal é este:

- trocar a lista estática de estudantes por uma lista dinâmica vinda do Apps Script.

Isso deixará a avaliação online muito mais prática de manter.
