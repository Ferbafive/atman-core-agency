import pandas as pd
import io

class DataProcessor:
    """
    Procesa y limpia los datos de los leads, generando bytes seguros para CSV y Excel.
    """
    def process_leads(self, raw_leads: list) -> pd.DataFrame:
        df = pd.DataFrame(raw_leads)
        expected_columns = ["company_name", "url", "email", "phone", "address"]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None
        return df[expected_columns]

    def export_to_csv(self, df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False).encode('utf-8')

    def export_to_excel(self, df: pd.DataFrame) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads B2B')
        return output.getvalue()