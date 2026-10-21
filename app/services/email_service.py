import smtplib
from email.mime.text import MIMEText

def send_welcome_email(email, name):
    """
    Envía un correo electrónico de bienvenida a un cliente.
    
    Args:
        email (str): Dirección de correo electrónico del cliente
        name (str): Nombre del cliente
    """
    try:
        msg = MIMEText(f"Hola {name}, gracias por registrarte en nuestro sitio web.", _charset='utf-8')
        msg['Subject'] = "Bienvenido a nuestro sitio web"
        msg['From'] = "tu_correo_electronico@example.com"
        msg['To'] = email
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("tu_correo_electronico@example.com", "tu_contraseña")
        server.sendmail("tu_correo_electronico@example.com", email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error al enviar el correo electrónico: {str(e)}")
