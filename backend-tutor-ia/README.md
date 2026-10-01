# Tutor Socrático de Física

Backend independente para o tutor de IA nas simulações piloto da Lei de Coulomb, Molas, Lançamento de Projéteis, Energia na Pista de Skate, Laboratório de Colisões, Circuitos Elétricos DC, Lei de Ohm, Resistência Elétrica, Lei de Ampère, Lei de Faraday, Solenoide, Transformadores, Termologia, Dilatação Térmica, Escalas Termométricas, Calorimetria, Fluxo de Calor, Comportamento dos Gases, Experiência de Joule, Ciclo de Carnot, Força Magnética, Ondas 1D, Ondas 2D, Radiação de Corpo Negro e Fotossíntese Solar. A chave da DeepSeek fica no servidor, nunca no HTML ou no JavaScript.

## Executar localmente

1. Instale Python 3.11 ou superior.
2. Abra o PowerShell nesta pasta e crie o ambiente:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Abra `.env` e preencha `DEEPSEEK_API_KEY` com a chave da sua conta DeepSeek. Não envie a chave pelo chat e não a publique no GitHub.
4. Inicie o serviço:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

5. Confira `http://127.0.0.1:8000/`; deve aparecer `{"status":"ok","service":"tutor-socratico"}`.

## Configurar a simulação

Em `LeiDeCoulomb.html`, `AI_TUTOR_CONFIG.apiUrl` fica vazio até existir um endereço público para este backend. Para um teste local, use `http://127.0.0.1:8000/api/tutor`. Para publicar a simulação, substitua pelo endereço HTTPS do serviço implantado. Não publique a página com endereço local.

O backend aceita somente a origem do GitHub Pages do projeto e origens locais previstas em `ALLOWED_ORIGINS`. Se usar outro domínio, ajuste essa variável no ambiente do servidor.

## Publicar o backend no Render

Crie um serviço Web independente apontando para este repositório:

- Root Directory: `backend-tutor-ia`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Variáveis de ambiente: `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, `ALLOWED_ORIGINS` e, opcionalmente, `REQUESTS_PER_MINUTE`.

Configure a chave diretamente no painel do serviço, como segredo. Não a grave no repositório. Só depois do deploy copie a URL HTTPS gerada para `AI_TUTOR_CONFIG.apiUrl` na página.

## Limites e privacidade

- O navegador envia apenas o enunciado atual, a dúvida digitada e até oito mensagens recentes da conversa; não envia nome, e-mail, turma ou nota.
- As mensagens não são salvas pelo backend deste protótipo.
- Há limites de tamanho de entrada, quantidade de tokens da resposta e requisições por endereço de cliente. O limite em memória é uma proteção inicial, não substitui controles de uso e orçamento no provedor.
- CORS restringe navegadores, mas não autentica o serviço. Antes de ampliar o piloto, monitore o uso e configure limites de gastos na conta da API.
- A instrução socrática orienta o modelo, mas não garante que ele nunca revele uma resposta. Revise as conversas de teste antes de ampliar para outras turmas.