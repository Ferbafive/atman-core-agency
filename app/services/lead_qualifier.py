import logging

logger = logging.getLogger(__name__)

class LeadQualifier:
    def __init__(self):
        pass

    def evaluate(self, data: dict) -> tuple[int, bool]:
        """
        Evalúa los datos extraídos de la empresa, calcula un score de calidad
        y determina si es apto para outreach comercial.
        """
        score = 50
        company_name = data.get("company_name", "Empresa Desconocida")
        email = data.get("contact_email")
        phone = data.get("phone")

        # Sumar puntuación según la calidad de los datos
        if company_name and company_name != "Empresa Desconocida" and not company_name.startswith("🥇"):
            score += 20
        if email:
            score += 20
        if phone:
            score += 10

        # Criterio de aptitud: Score mínimo de 70 y presencia de correo electrónico válido
        is_qualified = score >= 70 and email is not None

        return score, is_qualified