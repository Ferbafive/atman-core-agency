class WhatsAppBot:
    """
    Clase para manejar interacciones con WhatsApp Bot de Atman Core Agency.
    """
    
    def __init__(self):
        self.agency_name = "Atman Core Agency"
        self.prices = {
            'basic': 5000,
            'standard': 10000,
            'premium': 20000
        }
        self.appointment_slots = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    def responder_mensaje(self, mensaje):
        """
        Método principal para responder mensajes del WhatsApp Bot.
        Maneja consultas sobre citas, precios y presupuestos.
        
        Args:
            mensaje (str): El mensaje recibido del cliente
            
        Returns:
            str: La respuesta adecuada al mensaje
        """
        mensaje = mensaje.lower().strip()
        
        # Detectar si el mensaje es sobre precios
        if any(keyword in mensaje for keyword in ['precio', 'costo', 'cuanto', 'tarifa']):
            return self._responder_precios()
        
        # Detectar si el mensaje es sobre citas
        if any(keyword in mensaje for keyword in ['cita', 'cita', 'reserva', 'agendar', 'horario']):
            return self._responder_citas()
        
        # Detectar si el mensaje es sobre presupuesto
        if any(keyword in mensaje for keyword in ['presupuesto', 'cotización', 'oferta']):
            return self._responder_presupuesto()
        
        # Mensaje genérico de bienvenida
        return self._responder_generico(mensaje)
    
    def _responder_precios(self):
        """Responder sobre precios de los servicios."""
        respuesta = f"""
        ¡Hola! En {self.agency_name} ofrecemos los siguientes planes:
        
        📦 Plan Básico: ${self.prices['basic']}
        📦 Plan Estándar: ${self.prices['standard']}
        📦 Plan Premium: ${self.prices['premium']}
        
        ¿Te gustaría saber más sobre algún plan en particular?
        """
        return respuesta
    
    def _responder_citas(self):
        """Responder sobre agendamiento de citas."""
        respuesta = f"""
        ¡Hola! En {self.agency_name} podemos agendar citas los siguientes días:
        
        📅 Días disponibles: {', '.join(self.appointment_slots)}
        
        ¿En qué día te gustaría agendar tu cita?
        """
        return respuesta
    
    def _responder_presupuesto(self):
        """Responder sobre presupuestos y cotizaciones."""
        respuesta = f"""
        ¡Hola! En {self.agency_name} podemos ofrecerte un presupuesto personalizado.
        
        Para darte la mejor cotización, necesito saber:
        1. ¿Qué servicio necesitas?
        2. ¿Cuántos proyectos tienes?
        3. ¿Tienes un plazo específico?
        
        ¡Te responderé lo antes posible!
        """
        return respuesta
    
    def _responder_generico(self, mensaje):
        """Responder a mensajes genéricos o de bienvenida."""
        if 'hola' in mensaje or 'buenos días' in mensaje or 'buenas tardes' in mensaje or 'buenas noches' in mensaje:
            return f"¡Hola! Bienvenido a {self.agency_name}. ¿En qué puedo ayudarte hoy?"
        elif 'gracias' in mensaje:
            return "¡De nada! ¿Hay algo más en lo que pueda ayudarte?"
        else:
            return f"¡Hola! Gracias por contactarnos en {self.agency_name}. ¿En qué puedo ayudarte hoy?"
