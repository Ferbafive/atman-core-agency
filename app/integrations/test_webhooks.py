import unittest
from app.integrations.webhooks import WebhookHandler


class TestWebhookHandler(unittest.TestCase):
    """
    Pruebas unitarias para WebhookHandler.
    """
    
    def setUp(self):
        """Configura el entorno de prueba antes de cada prueba."""
        self.handler = WebhookHandler()
    
    def test_register_handler(self):
        """Prueba la registro de manejadores de eventos."""
        def test_handler(payload):
            return {'processed': True}
        
        self.handler.register_handler('test_event', test_handler)
        
        self.assertIn('test_event', self.handler.handlers)
        self.assertEqual(self.handler.handlers['test_event'], test_handler)
    
    def test_handle_webhook_with_handler(self):
        """Prueba el manejo de webhook con manejador registrado."""
        def test_handler(payload):
            return {'processed': True}
        
        self.handler.register_handler('test_event', test_handler)
        
        webhook_data = {
            'type': 'test_event',
            'payload': {'data': 'test'}
        }
        
        result = self.handler.handle_webhook(webhook_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['event_type'], 'test_event')
        self.assertEqual(result['result']['processed'], True)
    
    def test_handle_webhook_without_handler(self):
        """Prueba el manejo de webhook sin manejador registrado."""
        webhook_data = {
            'type': 'unknown_event',
            'payload': {'data': 'test'}
        }
        
        result = self.handler.handle_webhook(webhook_data)
        
        self.assertEqual(result['status'], 'no_handler')
        self.assertEqual(result['event_type'], 'unknown_event')
        self.assertIn('message', result)
    
    def test_handle_webhook_with_error(self):
        """Prueba el manejo de webhook con error en el manejador."""
        def failing_handler(payload):
            raise ValueError('Error de prueba')
        
        self.handler.register_handler('error_event', failing_handler)
        
        webhook_data = {
            'type': 'error_event',
            'payload': {'data': 'test'}
        }
        
        result = self.handler.handle_webhook(webhook_data)
        
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['event_type'], 'error_event')
        self.assertIn('error', result)
    
    def test_handle_empty_webhook(self):
        """Prueba el manejo de webhook vacío."""
        webhook_data = {}
        
        result = self.handler.handle_webhook(webhook_data)
        
        self.assertEqual(result['status'], 'no_handler')
        self.assertEqual(result['event_type'], 'unknown')
    
    def test_send_webhook_success(self):
        """Prueba el envío de webhook exitoso (mock)."""
        # Simular endpoint que acepta
        self.handler.endpoint_url = 'http://test.com/webhook'
        
        result = self.handler.send_webhook('test_event', {'data': 'test'})
        
        self.assertEqual(result['status'], 'sent')
        self.assertEqual(result['event_type'], 'test_event')
    
    def test_send_webhook_failure(self):
        """Prueba el envío de webhook fallido."""
        # Simular endpoint que falla
        self.handler.endpoint_url = 'http://invalid.com/webhook'
        
        result = self.handler.send_webhook('test_event', {'data': 'test'})
        
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['event_type'], 'test_event')
    
    def test_get_qualification_report_integration(self):
        """Prueba integración con LeadQualifier."""
        from app.services.lead_qualifier import LeadQualifier
        
        qualifier = LeadQualifier()
        leads = [
            {'id': 1, 'name': 'Lead 1', 'email': 'test1@test.com'},
            {'id': 2, 'name': 'Lead 2', 'email': 'test2@test.com'},
        ]
        
        report = qualifier.get_qualification_report(leads)
        
        self.assertEqual(len(report), 2)
        self.assertIn('lead_id', report[0])
        self.assertIn('score', report[0])
        self.assertIn('status', report[0])
        self.assertIn('qualified', report[0])
        self.assertIn('criteria_met', report[0])


if __name__ == '__main__':
    unittest.main()
