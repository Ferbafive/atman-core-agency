import sys
import os

# Agrega el directorio actual al path por seguridad para encontrar los módulos internos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.init_db import get_db, init_db
from app.database.models import Lead

def main():
    """
    Función principal que ejecuta todo el pipeline de prospección y producción de Atman Core Agency.
    """
    print("🚀 [Atman Core] Iniciando pipeline de producción...")
    
    try:
        # ==========================================
        # Inicializar base de datos
        # ==========================================
        print("📦 [Atman Core] Inicializando base de datos...")
        init_db()
        
        # ==========================================
        # Obtener sesión de base de datos
        # ==========================================
        print("🔗 [Atman Core] Conectando a base de datos...")
        db_session = get_db()
        
        # ==========================================
        # Crear y guardar 3 leads de prueba
        # ==========================================
        print("📝 [Atman Core] Creando leads de prueba...")
        
        # Lead 1: Clínica dental
        lead1 = Lead(
            company_name="Clínica Dental Sonrisas",
            url="https://www.clinica-dental.com",
            contact_email="contacto@clinica-dental.com",
            phone="+34 612 345 678",
            score=85,
            is_qualified=True
        )
        db_session.add(lead1)
        
        # Lead 2: Centro médico
        lead2 = Lead(
            company_name="Centro Médico Salud Total",
            url="https://www.centro-medico.com",
            contact_email="info@centro-medico.com",
            phone="+34 91 234 5678",
            score=72,
            is_qualified=True
        )
        db_session.add(lead2)
        
        # Lead 3: Consultorio de fisioterapia
        lead3 = Lead(
            company_name="Fisioterapia Express",
            url="https://www.fisioterapia-express.com",
            contact_email="contacto@fisioterapia-express.com",
            phone="+34 655 789 012",
            score=45,
            is_qualified=False
        )
        db_session.add(lead3)
        
        # Confirmar los cambios en la base de datos
        db_session.commit()
        
        # ==========================================
        # Verificación final
        # ==========================================
        print("✅ [Atman Core] Pipeline de producción ejecutado con éxito.")
        print(f"📊 [Atman Core] {len(db_session.query(Lead).all())} leads guardados en la base de datos.")
        
        # Limpiar la sesión
        db_session.close()
        
    except Exception as e:
        print(f"❌ [Atman Core] Error crítico durante la ejecución del pipeline: {e}")
        raise e

if __name__ == "__main__":
    main()
