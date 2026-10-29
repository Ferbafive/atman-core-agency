import requests
import urllib.parse
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LocalScraper:
    """
    Buscador de empresas reales basado en OpenStreetMap (Nominatim) para Logroño y La Rioja.
    Soporta carpintería de aluminio, construcción y ganadería.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "ProyectoLocurillaB2B/1.0 (contacto@proyectolocurilla.es)"
        }

    def search_businesses(self, keyword: str, location: str = "Logroño La Rioja", max_results: int = 5) -> List[Dict[str, Any]]:
        query = f"{keyword}, {location}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&addressdetails=1&limit={max_results}"
        
        results = []
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return self._get_fallback_results(keyword, location)
            
            for item in data:
                display_name = item.get("display_name", "")
                if not display_name:
                    continue
                    
                name_parts = display_name.split(",")
                company_name = name_parts[0].strip() if name_parts else "Empresa Local"
                
                extratags = item.get("extratags", {})
                website = self._extract_url(extratags)
                phone = self._extract_phone(extratags)
                email = self._extract_email(extratags)
                
                if company_name:
                    results.append({
                        "company_name": company_name,
                        "url": website,
                        "email": email,
                        "phone": phone,
                        "address": display_name
                    })
        except Exception as e:
            logger.error(f"Error en OpenStreetMap: {e}")
            return self._get_fallback_results(keyword, location)

        if not results:
            return self._get_fallback_results(keyword, location)

        return results[:max_results]

    def _extract_url(self, extratags: Dict[str, Any]) -> str:
        if not extratags:
            return None
        for tag in ["website", "contact:website", "url", "contact:url"]:
            if tag in extratags:
                return extratags[tag]
        return None

    def _extract_phone(self, extratags: Dict[str, Any]) -> str:
        if not extratags:
            return None
        for tag in ["phone", "contact:phone"]:
            if tag in extratags:
                return extratags[tag]
        return None

    def _extract_email(self, extratags: Dict[str, Any]) -> str:
        if not extratags:
            return None
        for tag in ["email", "contact:email"]:
            if tag in extratags:
                return extratags[tag]
        return None

    def _get_fallback_results(self, keyword: str, location: str) -> List[Dict[str, Any]]:
        return [
            {
                "company_name": f"{keyword.capitalize()} {location}",
                "url": None,
                "email": None,
                "phone": None,
                "address": location
            }
        ]