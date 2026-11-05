import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

import main


class RefractionTutorTest(unittest.TestCase):
    def test_refraction_uses_existing_optics_key_and_guidance(self):
        response_from_provider = MagicMock()
        response_from_provider.json.return_value = {
            'choices': [{'message': {'content': 'Como o índice se relaciona com a velocidade?'}}]
        }
        provider_client = AsyncMock()
        provider_client.post.return_value = response_from_provider
        provider_context = AsyncMock()
        provider_context.__aenter__.return_value = provider_client

        with TestClient(main.app) as client:
            with patch.object(main, 'DEEPSEEK_API_KEY', 'test-key'):
                with patch.object(main.httpx, 'AsyncClient', return_value=provider_context):
                    response = client.post('/api/tutor', json={
                        'simulation_key': 'optica-geometrica',
                        'exercise_question': 'Como a luz se desvia ao passar do ar para o vidro?',
                        'message': 'Por onde começo?',
                    })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['reply'], 'Como o índice se relaciona com a velocidade?')
        messages = provider_client.post.call_args.kwargs['json']['messages']
        self.assertIn('Para refração', messages[0]['content'])
        self.assertIn('n1 sen θ1 = n2 sen θ2', messages[0]['content'])
        self.assertIn('equação de Gauss', messages[0]['content'])
        self.assertIn('ar para o vidro', messages[1]['content'])


if __name__ == '__main__':
    unittest.main()
