import requests
import logging

logger = logging.getLogger(__name__)

class WebhookNotifier:
    def __init__(self, webhook_url: str = None):
        # Configuración del webhook (modo simulación activo si no se provee URL)
        self.webhook_url = webhook_url

    def send_alert(self, lead_data: dict, score: float):
        """
        Envía una notificación al canal de Webhook configurado.
        """
        if not self.webhook_url:
            logger.info(f"🔔 [Modo Simulación Alerta] Lead Cualificado detectado: {lead_data.get('company_name')} (Score: {score})")
            return True

        payload = {
            "content": f"🚨 **¡Nuevo Lead Cualificado Detectado!**\n"
                       f"🏢 **Empresa:** {lead_data.get('company_name')}\n"
                       f"⭐ **Score:** {score}\n"
                       f"📧 **Email:** {lead_data.get('contact_email')}\n"
                       f"🌍 **Web:** {lead_data.get('website')}"
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            if response.status_code in [200, 204]:
                print(f"🚀 Alerta de webhook enviada para {lead_data.get('company_name')}")
                return True
            else:
                print(f"⚠️ Error al enviar webhook: Código {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Excepción al conectar con el webhook: {e}")
            return False