import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class OutreachSender:
    def __init__(self, smtp_server=None, smtp_port=587, sender_email=None, sender_password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_cold_email(self, lead_data: dict):
        """
        Envía un correo de prospección comercial personalizado al lead detectado.
        Si no hay credenciales SMTP configuradas, opera en modo simulación profesional.
        """
        company = lead_data.get('company_name', 'tu empresa')
        recipient_email = lead_data.get('contact_email')
        
        if not recipient_email:
            logger.warning(f"⚠️ No hay email de contacto para {company}, omitiendo outreach.")
            return False

        # Asunto y plantilla de alta conversión para la agencia
        subject = f"Propuesta de crecimiento digital para {company}"
        body = (
            f"Hola equipo de {company},\n\n"
            f"Estuve analizando vuestra presencia digital y creo que tenéis un margen de "
            f"crecimiento brutal en captación de clientes online.\n\n"
            f"En nuestra agencia ayudamos a negocios como el vuestro a automatizar la adquisición "
            f"de clientes mediante sistemas de IA y embudos de ventas optimizados.\n\n"
            f"¿Tendríais 10 minutos la semana que viene para enseñaros un caso de éxito rápido?\n\n"
            f"Un saludo,\n"
            f"Director de Desarrollo de Negocio"
        )

        # Si no hay servidor SMTP configurado, simulamos el envío con éxito comercial
        if not self.sender_email or not self.sender_password:
            logger.info(f"📧 [Modo Simulación Outreach] Email preparado para enviar a: {recipient_email} | Empresa: {company}")
            print(f"   ✉️ [OUTREACH EXITOSO] Correo de prospección listo para disparar a {recipient_email}")
            return True

        # Envío real vía SMTP (Gmail, SendGrid, etc.)
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            
            print(f"🚀 ¡Email real enviado con éxito a {recipient_email}!")
            return True
        except Exception as e:
            logger.error(f"❌ Error al enviar el email a {recipient_email}: {e}")
            return False