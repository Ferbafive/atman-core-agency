"""
Script para ejecutar pruebas del BusinessScraper y exportar resultados a CSV.
"""

import sys
import os

# Añadir la ruta raíz del proyecto a sys.path para evitar errores de importación
def get_project_root():
    """Obtener la ruta raíz del proyecto."""
    # Intentar obtener el directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Subir un nivel para llegar al directorio del proyecto
    project_root = os.path.dirname(script_dir)
    return project_root

# Añadir la ruta raíz al sys.path
project_root = get_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.scrapers.business_scraper import BusinessScraper

def main():
    # Inicializar el scraper
    scraper = BusinessScraper()
    
    # Asegurar directorio de salida
    scraper.ensure_output_dir()
    
    # Simular datos de empresas para prueba
    test_urls = [
        "https://ejemplo1.com",
        "https://ejemplo2.com",
        "https://ejemplo3.com"
    ]
    
    # Ejecutar scraping de datos
    print("Iniciando scraping de datos...")
    data = scraper.scrape_multiple_businesses(test_urls)
    
    if data:
        # Buscar empresas por keyword y ubicación
        keyword = "tecnología"
        location = "Madrid"
        
        print(f"Buscando empresas con keyword '{keyword}' en ubicación '{location}'...")
        results = scraper.search_by_keyword_and_location(keyword, location, data)
        
        if results:
            # Exportar resultados a CSV
            output_filename = "busqueda_keyword_location.csv"
            print(f"Exportando resultados a: {output_filename}")
            scraper.export_to_csv(results, output_filename)
            
            print("Prueba completada con éxito.")
            print(f"Se encontraron {len(results)} empresas.")
        else:
            print("No se encontraron empresas que coincidan con los criterios.")
    else:
        print("No se encontraron datos para exportar.")
    
    # Limpiar exportaciones antiguas (opcional)
    # scraper.cleanup_old_exports(days=7)

if __name__ == '__main__':
    main()
