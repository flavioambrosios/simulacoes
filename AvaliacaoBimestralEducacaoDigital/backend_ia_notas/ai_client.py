from __future__ import annotations

import json
import re
from typing import Any

import requests

from config import Settings


class AIClientError(RuntimeError):
    pass


class AIClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def evaluate_conclusion(self, conclusion: str, context: dict[str, str]) -> dict[str, Any]:
        if not self.settings.api_key:
            raise AIClientError(
                'Chave de API não encontrada. Preencha AI_API_KEY no arquivo .env dentro da pasta backend_ia_notas.'
            )

        prompt = self._build_prompt(conclusion, context)
        if self.settings.provider == 'openai':
            raw_text = self._call_openai(prompt)
        elif self.settings.provider == 'gemini':
            raw_text = self._call_gemini(prompt)
        else:
            raise AIClientError('AI_PROVIDER deve ser openai ou gemini.')

        payload = self._extract_json(raw_text)
        return {
            'coerencia': clamp_score(payload.get('coerencia', 0)),
            'significancia': clamp_score(payload.get('significancia', 0)),
            'comentario': str(payload.get('comentario', '')).strip()
        }

    def _build_prompt(self, conclusion: str, context: dict[str, str]) -> str:
        return f'''Você é um avaliador de conclusões de estudantes do ensino médio.
Avalie apenas o texto do estudante em português do Brasil.

Contexto:
- Estudante: {context.get("estudante", "")}
- Turma: {context.get("turma", "")}
- Simulação: {context.get("simulacao", "")}
- Nota da simulação: {context.get("nota", "")}

Texto do estudante:
"""
{conclusion}
"""

Retorne apenas um JSON válido, sem markdown, com este formato:
{{
  "coerencia": numero_de_0_a_10,
  "significancia": numero_de_0_a_10,
  "comentario": "comentário curto em 1 frase"
}}

Critérios:
- coerencia: clareza, sequência lógica e consistência das ideias.
- significancia: nível de compreensão conceitual demonstrado pelo estudante.
- Use notas com uma casa decimal quando necessário.
'''

    def _call_openai(self, prompt: str) -> str:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {self.settings.api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': self.settings.model,
                'temperature': 0.2,
                'messages': [
                    {'role': 'system', 'content': 'Responda somente com JSON válido.'},
                    {'role': 'user', 'content': prompt}
                ]
            },
            timeout=self.settings.request_timeout
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    def _call_gemini(self, prompt: str) -> str:
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/{self.settings.model}:generateContent?key={self.settings.api_key}',
            headers={'Content-Type': 'application/json'},
            json={
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {
                    'temperature': 0.2,
                    'responseMimeType': 'application/json'
                }
            },
            timeout=self.settings.request_timeout
        )
        response.raise_for_status()
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']

    def _extract_json(self, raw_text: str) -> dict[str, Any]:
        text = raw_text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'```$', '', text).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', text, flags=re.DOTALL)
            if not match:
                raise AIClientError(f'Não foi possível interpretar a resposta da IA: {raw_text}')
            return json.loads(match.group(0))


def clamp_score(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return round(max(0.0, min(10.0, numeric)), 1)