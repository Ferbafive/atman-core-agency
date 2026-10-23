import csv
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BusinessScraper:
    """
    Clase para realizar scraping de datos de empresas y exportar a CSV.
    """
    
    def __init__(self, output_dir: str = 'app/data/exports'):
        """
        Inicializa el BusinessScraper.
        
        Args:
            output_dir (str): Directorio donde se guardarán los archivos CSV
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Asegura que el directorio de salida exista."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Directorio creado: {self.output_dir}")
    
    def scrape_business_data(self, url: str, headers: Optional[Dict] = None) -> List[Dict]:
        """
        Scrapa datos de una empresa desde una URL.
        
        Args:
            url (str): URL de la empresa a scrapear
            headers (dict): Cabeceras HTTP opcionales
            
        Returns:
            list: Lista de datos scrapeados
        """
        logger.info(f"Iniciando scraping de: {url}")
        
        # Aquí se implementaría la lógica de scraping real
        # Por ahora, simulamos datos de ejemplo
        return [
            {
                'url': url,
                'company_name': 'Ejemplo de Empresa',
                'industry': 'Tecnología',
                'employees': 150,
                'revenue': 5000000,
                'contact_email': 'info@ejemplo.com',
                'phone': '+1234567890',
                'website': url,
                'scraped_at': datetime.now().isoformat()
            }
        ]
    
    def scrape_multiple_businesses(self, urls: List[str], headers: Optional[Dict] = None) -> List[Dict]:
        """
        Scrapa datos de múltiples empresas.
        
        Args:
            urls (list): Lista de URLs a scrapear
            headers (dict): Cabeceras HTTP opcionales
            
        Returns:
            list: Lista combinada de todos los datos scrapeados
        """
        all_data = []
        for url in urls:
            try:
                data = self.scrape_business_data(url, headers)
                all_data.extend(data)
                logger.info(f"Scrapeado completado para: {url}")
            except Exception as e:
                logger.error(f"Error al scrapear {url}: {str(e)}")
        
        return all_data
    
    def export_to_csv(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """
        Exporta datos a archivo CSV.
        
        Args:
            data (list): Lista de datos a exportar
            filename (str): Nombre del archivo CSV (opcional)
            
        Returns:
            str: Ruta completa del archivo CSV creado
        """
        if not data:
            logger.warning("No hay datos para exportar")
            return None
        
        # Generar nombre de archivo con timestamp si no se proporciona
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"business_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Determinar campos únicos para exportar
        fields = list(data[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Datos exportados a: {filepath}")
        return filepath
    
    def export_to_csv_with_filters(self, data: List[Dict], 
                                   min_revenue: Optional[int] = None,
                                   max_employees: Optional[int] = None) -> str:
        """
        Exporta datos filtrados a archivo CSV.
        
        Args:
            data (list): Lista de datos a exportar
            min_revenue (int): Mínimo de ingresos para filtrar
            max_employees (int): Máximo de empleados para filtrar
            
        Returns:
            str: Ruta completa del archivo CSV creado
        """
        filtered_data = []
        
        for record in data:
            # Aplicar filtros
            if min_revenue is not None and record.get('revenue', 0) < min_revenue:
                continue
            if max_employees is not None and record.get('employees', 0) > max_employees:
                continue
            
            filtered_data.append(record)
        
        return self.export_to_csv(filtered_data)
    
    def search_by_keyword(self, keyword: str, data: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Busca empresas por término/palabra clave.
        
        Args:
            keyword (str): Palabra clave para buscar
            data (list): Lista de datos a buscar (opcional, si no se proporciona se usa scrape_multiple_businesses)
            
        Returns:
            list: Lista de empresas que coinciden con la palabra clave
        """
        if not data:
            logger.warning("No se proporcionaron datos para buscar. Se usará scraping básico.")
            # Simulación de búsqueda en datos de ejemplo
            return []
        
        results = []
        keyword_lower = keyword.lower()
        
        for record in data:
            # Buscar en múltiples campos
            if (keyword_lower in record.get('company_name', '').lower() or
                keyword_lower in record.get('industry', '').lower() or
                keyword_lower in record.get('website', '').lower()):
                results.append(record)
                logger.info(f"Empresa encontrada: {record.get('company_name')}")
        
        return results
    
    def search_by_location(self, location: str, data: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Busca empresas por ubicación.
        
        Args:
            location (str): Ubicación para buscar
            data (list): Lista de datos a buscar (opcional, si no se proporciona se usa scrape_multiple_businesses)
            
        Returns:
            list: Lista de empresas que coinciden con la ubicación
        """
        if not data:
            logger.warning("No se proporcionaron datos para buscar por ubicación.")
            # Simulación de búsqueda en datos de ejemplo
            return []
        
        results = []
        location_lower = location.lower()
        
        for record in data:
            # Buscar en campos de ubicación
            if (location_lower in record.get('city', '').lower() or
                location_lower in record.get('country', '').lower() or
                location_lower in record.get('address', '').lower()):
                results.append(record)
                logger.info(f"Empresa encontrada en {location}: {record.get('company_name')}")
        
        return results
    
    def search_by_keyword_and_location(self, keyword: str, location: str, 
                                       data: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Busca empresas combinando palabra clave y ubicación.
        
        Args:
            keyword (str): Palabra clave para buscar
            location (str): Ubicación para buscar
            data (list): Lista de datos a buscar (opcional, si no se proporciona se usa scrape_multiple_businesses)
            
        Returns:
            list: Lista de empresas que coinciden con ambos criterios
        """
        if not data:
            logger.warning("No se proporcionaron datos para buscar combinada.")
            # Simulación de búsqueda en datos de ejemplo
            return []
        
        results = []
        keyword_lower = keyword.lower()
        location_lower = location.lower()
        
        for record in data:
            # Verificar coincidencia en ambos criterios
            matches_keyword = (keyword_lower in record.get('company_name', '').lower() or
                             keyword_lower in record.get('industry', '').lower() or
                             keyword_lower in record.get('website', '').lower())
            
            matches_location = (location_lower in record.get('city', '').lower() or
                              location_lower in record.get('country', '').lower() or
                              location_lower in record.get('address', '').lower())
            
            if matches_keyword and matches_location:
                results.append(record)
                logger.info(f"Empresa encontrada: {record.get('company_name')} en {location}")
        
        return results
    
    def save_business_to_database(self, business_data: Dict, session=None):
        """
        Guarda datos de empresa en base de datos.
        
        Args:
            business_data (dict): Datos de la empresa
            session: Sesión de SQLAlchemy (opcional)
        """
        logger.info(f"Guardando empresa: {business_data.get('company_name')}")
        # Aquí se implementaría la lógica de persistencia en base de datos
        pass
    
    def cleanup_old_exports(self, days: int = 30):
        """
        Limpia archivos de exportación antiguos.
        
        Args:
            days (int): Número de días de retención
        """
        import glob
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                if file_time < cutoff_time:
                    os.remove(filepath)
                    logger.info(f"Archivo eliminado: {filename}")
        
        logger.info(f"Limpieza completada. Archivos eliminados: {days} días")
