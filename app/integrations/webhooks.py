import json
class WebhookHandler:
    """
    Clase para manejar webhooks de integración.
    """
    
    def __init__(self, endpoint_url=None, timeout=30):
        """
        Inicializa el WebhookHandler con configuración de endpoint.
        
        Args:
            endpoint_url (str): URL del endpoint para recibir webhooks
            timeout (int): Tiempo de espera en segundos
        """
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.handlers = {}
    
    def register_handler(self, event_type, handler_func):
        """
        Registra un manejador para un tipo de evento específico.
        
        Args:
            event_type (str): Tipo de evento
            handler_func (callable): Función para manejar el evento
        """
        self.handlers[event_type] = handler_func
    
    def __init__(self, endpoint_url=None, timeout=30):
        """
        Inicializa el WebhookHandler con configuración de endpoint.
        
        Args:
            endpoint_url (str): URL del endpoint para recibir webhooks
            timeout (int): Tiempo de espera en segundos
        """
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.handlers = {}
        self.session = init_db()
    
    def handle_webhook(self, webhook_data):
        """
        Maneja un webhook recibido.
        
        Args:
            webhook_data (dict): Datos del webhook
            
        Returns:
            dict: Resultado del procesamiento
        """
        event_type = webhook_data.get('type', 'unknown')
        payload = webhook_data.get('payload', {})
        
        # Verificar si hay un manejador registrado
        if event_type in self.handlers:
            try:
                result = self.handlers[event_type](payload)
                self.save_lead(payload)
                return {
                    'status': 'success',
                    'event_type': event_type,
                    'result': result
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'event_type': event_type,
                    'error': str(e)
                }
        else:
            self.save_lead(payload)
            return {
                'status': 'no_handler',
                'event_type': event_type,
                'message': f'No hay manejador registrado para el evento: {event_type}'
            }
    
    def save_lead(self, payload):
        """
        Guarda un lead en la base de datos.
        
        Args:
            payload (dict): Datos del lead
        """
        from app.database.models import Lead
        from app.services.lead_qualifier import LeadQualifier
        try:
            lead = Lead(
                nombre=payload.get('name', ''),
                email=payload.get('email', ''),
                score=payload.get('score', 0.0),
                qualified=payload.get('qualified', False),
                status=payload.get('status', '')
            )
            self.session.add(lead)
            self.session.commit()
        except Exception as e:
            print(f"Error al guardar el lead: {str(e)}")
    
    def send_webhook(self, event_type, payload):
        """
        Envía un webhook a un endpoint.
        
        Args:
            event_type (str): Tipo de evento
            payload (dict): Datos del evento
            
        Returns:
            dict: Resultado del envío
        """
        import requests
        import json
        
        try:
            response = requests.post(
                self.endpoint_url,
                json=json.dumps(payload),
                timeout=self.timeout
            )
            return {
                'status': 'sent',
                'event_type': event_type,
                'response_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'failed',
                'event_type': event_type,
                'error': str(e)
            }
