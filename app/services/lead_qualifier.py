import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class LeadQualifier:
    def __init__(self):
        pass

    def evaluate(self, data: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Evalúa los datos extraídos de la empresa, calcula un score de calidad
        y determina si es apto para outreach comercial.
        
        Parámetros:
            data: Diccionario con los datos extraídos de la empresa
                 Puede contener: company_name, url, email, phone, address
        
        Retorna:
            Tuple[int, bool]: (score, is_qualified)
        """
        score = 50  # Puntuación base por tener datos extraídos
        
        company_name = data.get("company_name", "Empresa Desconocida")
        email = data.get("contact_email") or data.get("email")
        phone = data.get("phone")
        url = data.get("url") or data.get("website")
        address = data.get("address")

        # Sumar puntuación según la calidad de los datos
        if company_name and company_name != "Empresa Desconocida" and not company_name.startswith("🥇"):
            score += 20
        
        if email and "@" in email and "." in email:
            score += 20
        
        if phone and len(phone) >= 5:
            score += 10
        
        if url and "http" in url:
            score += 10
        
        if address and len(address) > 10:
            score += 5

        # Criterio de aptitud: Score mínimo de 70 y presencia de correo electrónico válido
        is_qualified = score >= 70 and email is not None

        logger.debug(f"Lead calificado: {company_name} - Score: {score}, Calificado: {is_qualified}")

        return score, is_qualified
