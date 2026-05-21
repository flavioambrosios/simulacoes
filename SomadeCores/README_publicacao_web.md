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
1. Confira se os campos estao assim:

```text
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: gunicorn app_web:server
```

1. Clique em Create Web Service.
1. Espere o primeiro deploy terminar.
1. Abra o link publico gerado pelo Render.

## Observacao importante

- Um HTML estatico simples nao consegue manter a logica interativa completa deste simulador, porque a otimizacao e os calculos dependem de Python.
- Por isso, a solucao correta para publicar online e uma aplicacao web interativa, nao apenas um arquivo .html isolado.
