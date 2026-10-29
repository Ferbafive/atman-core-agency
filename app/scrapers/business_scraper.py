import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Dominios que nunca queremos procesar como leads
BLACKLIST_DOMAINS = [
    "chollometro.com", "bing.com", "google.com", "agenciatributaria.gob.es",
    "renfe.com", "facebook.com", "instagram.com", "linkedin.com", "youtube.com",
    "wikipedia.org", "grokipedia.com"
]

class BusinessScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

    def _clean_company_name(self, raw_title: str) -> str:
        """Limpia slogans, guiones, rankings y texto secundario del título."""
        if not raw_title:
            return "Empresa Desconocida"
        
        # 1. Eliminar frases típicas de listas/rankings al inicio (ej: "Las 10 mejores...")
        title = re.sub(r'^(Las|Los)?\s*\d+\+?\s*(Mejores|mejores)?\s*', '', raw_title, flags=re.IGNORECASE).strip()
        
        # 2. Separar por guiones, barras o separadores comunes y coger las partes
        parts = re.split(r'[-–—|:|»⇒]', title)
        clean_name = parts[0].strip()
        
        # 3. Si la primera parte es un texto genérico o directorio, probar la segunda parte si existe
        if clean_name.lower().startswith(('mejores', 'agencia inmobiliaria', 'inicio', 'home', 'directorio')) and len(parts) > 1:
            clean_name = parts[1].strip()

        # 4. Eliminar prefijos sobrantes
        clean_name = re.sub(r'^(Inicio|Home|Bienvenido a|Página principal de)\s*', '', clean_name, flags=re.IGNORECASE).strip()
        
        return clean_name if clean_name else "Empresa Desconocida"

    def scrape(self, url: str) -> dict:
        """
        Extrae información de contacto de una empresa desde su sitio web.
        Devuelve un diccionario con company_name, contact_email, phone.
        """
        domain = urlparse(url).netloc.lower()
        
        # Comprobar si el dominio está en la lista negra
        if any(blacked in domain for blacked in BLACKLIST_DOMAINS):
            logger.info(f"🚫 Dominio en lista negra ignorado: {domain}")
            return {
                "company_name": "Empresa Ignorada",
                "contact_email": None,
                "phone": None
            }

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                logger.warning(f"Estado HTTP {response.status_code} para {url}")
                return {
                    "company_name": "Empresa Desconocida",
                    "contact_email": None,
                    "phone": None
                }

            soup = BeautifulSoup(response.text, "html.parser")

            # 1. Extraer y limpiar nombre de la empresa
            raw_title = soup.title.string.strip() if soup.title and soup.title.string else "Empresa Desconocida"
            company_name = self._clean_company_name(raw_title)

            # 2. Extraer Email mediante Regex
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
            contact_email = email_match.group(0) if email_match else None

            # 3. Extraer Teléfono mediante Regex (formato español)
            phone_match = re.search(r"(\+34|0034)?\s*([679]\d{2}[\s.-]?\d{3}[\s.-]?\d{3})", response.text)
            phone = phone_match.group(0).strip() if phone_match else None

            return {
                "company_name": company_name,
                "contact_email": contact_email,
                "phone": phone
            }

        except Exception as e:
            logger.error(f"❌ Error escaneando {url}: {e}")
            return {
                "company_name": "Empresa Desconocida",
                "contact_email": None,
                "phone": None
            }
