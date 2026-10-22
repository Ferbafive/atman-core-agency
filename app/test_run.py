"""
Script para ejecutar pruebas del BusinessScraper y exportar resultados a CSV.
"""

from app.scrapers.business_scraper import BusinessScraper
import os

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
        # Exportar a CSV
        output_filename = "app/data/exports/prueba_export.csv"
        print(f"Exportando resultados a: {output_filename}")
        scraper.export_to_csv(data, output_filename)
        
        print("Prueba completada con éxito.")
        print(f"Se encontraron {len(data)} empresas.")
    else:
        print("No se encontraron datos para exportar.")
    
    # Limpiar exportaciones antiguas (opcional)
    # scraper.cleanup_old_exports(days=7)

if __name__ == '__main__':
    main()
