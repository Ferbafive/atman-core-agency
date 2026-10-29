"""
Pruebas unitarias para el módulo webhooks.
Verifica que los endpoints respondan correctamente ante payloads válidos e inválidos.
"""

import unittest
from app import create_app
from app.integrations.webhooks import WebhookHandler, api
from flask.testclient import TestClient

class TestWebhooks(unittest.TestCase):
    """Clase de pruebas para la funcionalidad de webhooks."""
    
    def setUp(self):
        """Configura la aplicación de prueba antes de cada caso de prueba."""
        self.app = create_app('testing')
        self.client = TestClient(self.app)
        
        # Necesitamos inicializar la API Flask-RESTful con el cliente
        # Nota: Esto depende de cómo se inicie la app en create_app()
        if not hasattr(api, 'resource_classes'):
            api.init_app(self.app)
            
    def test_webhook_post_success(self):
        """Prueba que un POST con payload válido devuelve éxito."""
        payload = {
            "event_type": "user.created",
            "data": {"user_id": 123}
        }
        
        response = self.client.post(
            '/api/v1/webhooks',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertIn('status', json_response)
        self.assertEqual(json_response['status'], 'success')

    def test_webhook_post_invalid_payload(self):
        """Prueba que un POST sin payload válido devuelve error 400."""
        response = self.client.post('/api/v1/webhooks', data='invalid json', content_type='text/plain')
        
        self.assertEqual(response.status_code, 400)
        # El código ya maneja la excepción de JSON parsing en el except block o antes
        
if __name__ == '__main__':
    unittest.main()