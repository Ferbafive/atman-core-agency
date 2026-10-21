import unittest
from app.integrations.webhooks import WebhookHandler

class TestWebhooks(unittest.TestCase):
    def test_handle_webhook(self):
        webhook_handler = WebhookHandler()
        webhook_data = {
            'type': 'lead_created',
            'payload': {
                'name': 'Juan',
                'email': 'juan@example.com'
            }
        }
        result = webhook_handler.handle_webhook(webhook_data)
        self.assertEqual(result['status'], 'success')

if __name__ == '__main__':
    unittest.main()
