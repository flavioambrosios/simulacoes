# Versao web do simulador

O arquivo principal para navegador e publicacao online e [app_web.py](app_web.py).

## O que mudou

- O programa original em Matplotlib abria varias janelas do desktop.
- Na web, essas janelas foram preservadas como abas da pagina: Simulador, Fourier Antes, Fourier Depois, Hilbert e Lab RGB.
- Isso permite uso online sem depender de janelas nativas do sistema operacional.

## Como executar localmente

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

1. Inicie a aplicacao:

```bash
python app_web.py
```

1. Abra no navegador:

```text
http://127.0.0.1:8050
```

## Como publicar online no Render

1. Envie esta pasta para um repositorio no GitHub.
1. No Render, crie um novo Web Service a partir do repositorio.
1. Use estas configuracoes:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app_web:server
```

1. Depois do deploy, o Render vai gerar um link publico.

## Envio para a planilha Notas CEAN 2026

O app agora pode registrar cada envio da aba Exercicios em uma planilha do Google Sheets.

### O que o app envia

- Data e hora do envio.
- Nome do estudante e turma ou codigo informados na tela.
- Identificacao do exercicio, tipo, dificuldade, resultado e pontuacao.
- Resumo da metrica numerica.
- Texto da conclusao do estudante.
- Dados da tabela de amplitudes e historico da otimizacao em formato JSON.

### Variaveis de ambiente

No Render, abra o servico e cadastre estas variaveis em Environment.

```text
GOOGLE_SERVICE_ACCOUNT_JSON=JSON_COMPLETO_DA_CONTA_DE_SERVICO
GOOGLE_SHEETS_SPREADSHEET_NAME=Notas CEAN 2026
GOOGLE_SHEETS_WORKSHEET_NAME=app web
```

Opcionalmente, voce pode usar o identificador da planilha em vez do nome:

```text
GOOGLE_SHEETS_SPREADSHEET_ID=ID_DA_PLANILHA
```

Tambem e possivel usar um arquivo de credenciais no lugar do JSON em variavel:

```text
GOOGLE_SERVICE_ACCOUNT_FILE=/caminho/para/service-account.json
```

### Como preparar a planilha

1. Crie ou abra a planilha Notas CEAN 2026 no Google Sheets.
1. Crie uma conta de servico no Google Cloud com acesso ao Google Sheets e ao Google Drive.
1. Compartilhe a planilha com o email da conta de servico, com permissao de editor.
1. No app, a aba configurada por GOOGLE_SHEETS_WORKSHEET_NAME sera criada automaticamente se ainda nao existir.

Sem essas variaveis, o app continua funcionando normalmente, mas o feedback do exercicio vai informar que a integracao com a planilha nao esta configurada.

## Consolidar notas por turma

O script [consolidar_notas_turmas.py](consolidar_notas_turmas.py) le os registros brutos da aba app web e monta um resumo por turma.

### Regra usada na consolidacao

- O script agora le a aba app web resultados, onde cada envio final da sessao guarda todas as etapas resolvidas.
- Para cada estudante, o script calcula a media das notas das etapas registradas em detalhes_exercicios.
- Se houver mais de um envio final do mesmo estudante, o script guarda o melhor envio com base nessa media das etapas.
- final_score_100 e a media das etapas na escala de 0 a 100.
- final_grade_10 converte final_score_100 para a escala de 0 a 10.
- O resumo tambem informa trilha, bimestre, acertos e o horario do melhor envio.

### Exemplos de uso

Exportar CSVs de todas as turmas detectadas:

```bash
python consolidar_notas_turmas.py
```

Exportar apenas uma turma:

```bash
python consolidar_notas_turmas.py --group 2A
```

Exportar e atualizar as abas das turmas na mesma planilha:

```bash
python consolidar_notas_turmas.py --write-sheets
```

Criar abas com prefixo, por exemplo Turma 2A, Turma 2B:

```bash
python consolidar_notas_turmas.py --write-sheets --worksheet-prefix "Turma "
```

Os CSVs sao gerados por padrao na pasta exports_turmas.

## Comandos de Git para enviar ao GitHub

Se esta pasta ainda nao estiver conectada ao seu repositorio remoto no GitHub, voce pode usar a sequencia abaixo dentro da pasta do projeto.

```bash
git add app_web.py requirements.txt Procfile runtime.txt .gitignore README_publicacao_web.md
git commit -m "Adiciona versao web para publicacao online"
git push
```

Se o repositorio remoto ainda nao estiver configurado, primeiro conecte com:

```bash
git remote -v
git remote add origin URL_DO_SEU_REPOSITORIO
git branch -M main
git push -u origin main
```

## Passo a passo no site do Render

1. Entre em [https://render.com](https://render.com) e faca login.
1. Clique em New +.
1. Escolha Web Service.
1. Conecte sua conta do GitHub, se o Render pedir.
1. Selecione o repositorio deste projeto.
1. Como a aplicacao esta dentro da pasta SomadeCores, preencha o campo Root Directory com SomadeCores, se o Render mostrar esse campo.
1. Confira se os campos estao assim:

```text
Environment: Python
Root Directory: SomadeCores
Build Command: pip install -r requirements.txt
Start Command: gunicorn app_web:server
```

1. Clique em Create Web Service.
1. Espere o primeiro deploy terminar.
1. Abra o link publico gerado pelo Render.

## Opcao mais automatica

Na raiz do repositorio agora existe o arquivo [render.yaml](../render.yaml). Em muitos casos, o Render consegue ler esse arquivo automaticamente e preencher os dados do servico com a pasta correta.

## Observacao importante

- Um HTML estatico simples nao consegue manter a logica interativa completa deste simulador, porque a otimizacao e os calculos dependem de Python.
- Por isso, a solucao correta para publicar online e uma aplicacao web interativa, nao apenas um arquivo .html isolado.
