@"
import os
from app.scrapers.business_scraper import BusinessScraper
from app.services.lead_qualifier import LeadQualifier
from app.services.exporter import LeadExporter
from app.database.models import Business, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def run_production_pipeline():
    print("🚀 Iniciando pipeline completo de prospección con exportación...")
    
    # 1. Configurar Base de Datos SQLite
    engine = create_engine('sqlite:///leads.db')
    Base.metadata.create_all(engine)
    
    # 2. Instanciar componentes del sistema
    scraper = BusinessScraper()
    criteria = {
        'min_score': 40,
        'max_score': 100,
        'required_fields': ['company_name', 'contact_email'],
        'weights': {
            'employees': 50,
            'revenue': 50
        }
    }
    qualifier = LeadQualifier(criteria=criteria)
    exporter = LeadExporter(engine)
    
    # 3. Cargar URLs objetivo desde targets.txt
    targets_file = 'targets.txt'
    if not os.path.exists(targets_file):
        with open(targets_file, 'w', encoding='utf-8') as f:
            f.write("https://example.com\nhttps://example.org\nhttps://example.net\n")
    
    with open(targets_file, 'r', encoding='utf-8') as f:
        target_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"📋 URLs cargadas para análisis: {len(target_urls)}")
    
    # 4. Procesar lote y persistir en BD
    Session = sessionmaker(bind=engine)
    session = Session()
    total_saved = 0
    
    try:
        for url in target_urls:
            print(f"\n🔍 Procesando: {url}")
            results = scraper.scrape_business_data(url)
            
            for item in results:
                qualification_result = qualifier.qualify_lead(item)
                print(f"   ⭐ {item.get('company_name')} | Estado: {qualification_result['status'].upper()} (Score: {qualification_result['score']})")
                
                business = Business(
                    url=item.get('url'),
                    company_name=item.get('company_name'),
                    industry=item.get('industry'),
                    employees=item.get('employees'),
                    revenue=item.get('revenue'),
                    contact_email=item.get('contact_email'),
                    phone=item.get('phone'),
                    city=item.get('city'),
                    country=item.get('country'),
                    website=item.get('website')
                )
                session.add(business)
                total_saved += 1
        
        session.commit()
        print(f"\n✅ ¡Base de datos actualizada! Se guardaron {total_saved} leads.")
        
        # 5. Exportar automáticamente a CSV
        print("\n📊 Generando reporte comercial en CSV...")
        exporter.export_to_csv("qualified_leads.csv")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error crítico en el pipeline: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_production_pipeline()
"@ | Out-File -Encoding utf8 test_run.py