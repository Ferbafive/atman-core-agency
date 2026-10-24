import csv
import logging
from app.database.models import Lead

logger = logging.getLogger(__name__)

class LeadExporter:
    def __init__(self, db_session):
        self.db = db_session

    def export_to_csv(self, filename="qualified_leads.csv"):
        try:
            leads = self.db.query(Lead).all()
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Escribir cabecera
                writer.writerow(["ID", "Empresa", "URL", "Email", "Teléfono", "Score", "Cualificado"])
                
                # Escribir datos
                for lead in leads:
                    writer.writerow([
                        lead.id,
                        lead.company_name,
                        lead.url,
                        lead.contact_email,
                        lead.phone,
                        lead.score,
                        lead.is_qualified
                    ])
            logger.info(f"📁 Exportación exitosa: {filename}")
        except Exception as e:
            logger.error(f"❌ Error al exportar a CSV: {e}")