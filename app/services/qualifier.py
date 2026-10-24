import logging

logger = logging.getLogger(__name__)

class LeadQualifier:
    def qualify(self, raw_data: dict) -> tuple[int, bool]:
        """
        Evalúa los datos extraídos de la web y calcula una puntuación (0-100)
        para determinar si el lead es apto para prospección comercial.
        """
        score = 50  # Puntuación base por tener web operativa
        
        company_name = raw_data.get("company_name")
        contact_email = raw_data.get("contact_email")
        phone = raw_data.get("phone")

        # Bonificaciones de calidad comercial
        if company_name and company_name != "Empresa Desconocida":
            score += 20
        if contact_email:
            score += 20
        if phone:
            score += 10

        # Umbral de cualificación: si tiene 60 puntos o más, va directo al outreach
        is_qualified = score >= 60

        logger.info(f"📊 Lead cualificado: {company_name} | Score: {score} | ¿Apto?: {is_qualified}")
        return score, is_qualified