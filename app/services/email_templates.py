import logging

logger = logging.getLogger(__name__)

class EmailTemplateEngine:
    def __init__(self):
        self.templates = {
            "clinica": {
                "subject": "Propuesta de captación de pacientes para {company_name}",
                "body": (
                    "Hola,\n\n"
                    "He estado revisando la web de {company_name} ({url}) y veo que tenéis una gran oferta de servicios.\n\n"
                    "En Atman Core Agency ayudamos a clínicas a optimizar su flujo de nuevos pacientes mediante sistemas de prospección digital.\n\n"
                    "¿Tendríais 5 minutos esta semana para ver cómo podemos ayudaros a llenar vuestra agenda?\n\n"
                    "Un saludo,\n"
                    "Equipo de Atman Core Agency"
                )
            },
            "inmobiliaria": {
                "subject": "Captación de propiedades e inversores para {company_name}",
                "body": (
                    "Hola,\n\n"
                    "Analizando el mercado inmobiliario he dado con {company_name} ({url}).\n\n"
                    "Ayudamos a agencias inmobiliarias a conectar directamente con propietarios interesados en vender sin depender únicamente de portales tradicionales.\n\n"
                    "¿Os interesaría revisar un breve análisis de oportunidad para vuestra zona?\n\n"
                    "Un cordial saludo,\n"
                    "Equipo de Atman Core Agency"
                )
            },
            "default": {
                "subject": "Oportunidad de colaboración con {company_name}",
                "body": (
                    "Hola,\n\n"
                    "Os escribo tras revisar la propuesta de valor de {company_name} en {url}.\n\n"
                    "Especializamos a empresas de vuestro sector en la automatización de captación de clientes B2B.\n\n"
                    "¿Cuándo os vendría bien una breve llamada de 5 minutos para conocernos?\n\n"
                    "Un saludo,\n"
                    "Equipo de Atman Core Agency"
                )
            }
        }

    def render(self, company_name: str, url: str, keyword: str = "") -> dict:
        kw_lower = keyword.lower()
        if "clinic" in kw_lower or "dental" in kw_lower or "salud" in kw_lower:
            key = "clinica"
        elif "inmobiliari" in kw_lower or "finca" in kw_lower or "piso" in kw_lower:
            key = "inmobiliaria"
        else:
            key = "default"

        template = self.templates[key]
        
        return {
            "subject": template["subject"].format(company_name=company_name),
            "body": template["body"].format(company_name=company_name, url=url)
        }