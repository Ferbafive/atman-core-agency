import sys
import os

# Agrega el directorio actual al path por seguridad para encontrar los módulos internos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Función principal que ejecuta todo el pipeline de prospección y producción de Atman Core Agency.
    """
    print("🚀 [Atman Core] Iniciando pipeline de producción...")
    
    try:
        # ==========================================
        # TODO: Coloca aquí la lógica de tu pipeline
        # ==========================================
        # Ejemplo:
        # from app.scrapers.prospecting import run_scraper
        # from app.ai.qualifier import qualify_leads
        # 
        # run_scraper()
        # qualify_leads()
        
        print("✅ [Atman Core] Pipeline de producción ejecutado con éxito.")
        
    except Exception as e:
        print(f"❌ [Atman Core] Error crítico durante la ejecución del pipeline: {e}")
        raise e

if __name__ == "__main__":
    main()