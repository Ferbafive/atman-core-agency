import logging
import time
from ddgs import DDGS

logger = logging.getLogger(__name__)

class KeywordSearcher:
    def __init__(self):
        pass

    def search_urls(self, keyword: str, max_results: int = 5) -> list[str]:
        """
        Busca URLs reales utilizando la librería DuckDuckGo Search (DDGS).
        """
        logger.info(f"🔍 Buscando URLs reales en vivo para: '{keyword}'")
        urls = []
        try:
            time.sleep(1) # Pausa estratégica para evitar bloqueos por tasa de peticiones
            with DDGS() as ddgs:
                results = list(ddgs.text(keyword, max_results=max_results))
                for r in results:
                    href = r.get("href") or r.get("link")
                    if href:
                        urls.append(href)
            
            logger.info(f"✅ Se han encontrado {len(urls)} URLs para '{keyword}'")
        except Exception as e:
            logger.error(f"⚠️ Error durante la búsqueda en vivo para '{keyword}': {e}")

        return urls