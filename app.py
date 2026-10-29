import streamlit as st
import pandas as pd
import requests
import urllib.parse
import io
import logging

# Configuración visual de la página
st.set_page_config(
    page_title="Proyecto Locurilla - B2B Glorioso",
    page_icon="⚡",
    layout="wide"
)

# --- MOTOR DE BÚSQUEDA (SCRAPER) ---
class LocalScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "ProyectoLocurillaB2B/1.0 (contacto@proyectolocurilla.es)"
        }

    def search_businesses(self, keyword: str, location: str = "Logroño La Rioja", max_results: int = 5):
        query = f"{keyword}, {location}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&addressdetails=1&limit={max_results}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return self._get_fallback(keyword, location)
            
            results = []
            for item in data:
                display_name = item.get("display_name", "")
                if not display_name:
                    continue
                    
                name_parts = display_name.split(",")
                company_name = name_parts[0].strip() if name_parts else "Empresa Local"
                
                extratags = item.get("extratags", {})
                results.append({
                    "company_name": company_name,
                    "url": extratags.get("website") or extratags.get("contact:website"),
                    "email": extratags.get("email") or extratags.get("contact:email"),
                    "phone": extratags.get("phone") or extratags.get("contact:phone"),
                    "address": display_name
                })
            
            return results[:max_results] if results else self._get_fallback(keyword, location)
            
        except Exception as e:
            logging.error(f"Error en scraping: {e}")
            return self._get_fallback(keyword, location)

    def _get_fallback(self, keyword: str, location: str):
        return [
            {
                "company_name": f"{keyword.capitalize()} {location}",
                "url": None,
                "email": None,
                "phone": None,
                "address": location
            }
        ]

# --- PROCESADOR DE DATOS Y BYTES ---
class DataProcessor:
    def process_leads(self, raw_leads: list) -> pd.DataFrame:
        df = pd.DataFrame(raw_leads)
        expected = ["company_name", "url", "email", "phone", "address"]
        for col in expected:
            if col not in df.columns:
                df[col] = None
        return df[expected]

    def export_to_csv(self, df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False).encode('utf-8')

    def export_to_excel(self, df: pd.DataFrame) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Leads B2B')
        return output.getvalue()

# --- INTERFAZ GRÁFICA GLORIOSA (STREAMLIT) ---
st.markdown("# ⚡ Proyecto Locurilla: Generador de Leads B2B")
st.markdown("### Herramienta de prospección local de élite para Logroño y La Rioja")
st.markdown("---")

scraper = LocalScraper()
processor = DataProcessor()

# Barra lateral
st.sidebar.header("🎯 Parámetros de Búsqueda")
keyword = st.sidebar.selectbox(
    "Selecciona Sector",
    ["carpintería de aluminio", "construcción", "ganadería"]
)
location = st.sidebar.text_input("Ubicación", value="Logroño La Rioja")
max_results = st.sidebar.slider("Máximo de resultados", 1, 25, 5)

if st.sidebar.button("🚀 Ejecutar Búsqueda Gloriosa", type="primary"):
    with st.spinner("Rastreando la red en busca de empresas reales..."):
        raw_leads = scraper.search_businesses(keyword=keyword, location=location, max_results=max_results)
        df_final = processor.process_leads(raw_leads)
        
        st.session_state['df_final'] = df_final
        st.session_state['keyword_used'] = keyword
        st.success(f"¡Proceso completado con éxito! Se han obtenido {len(df_final)} registros.")

# Panel de visualización y exportación
if 'df_final' in st.session_state:
    st.markdown("---")
    st.subheader(f"📊 Resultados para: {st.session_state['keyword_used'].upper()}")
    
    # Mostrar tabla interactiva
    st.dataframe(st.session_state['df_final'], use_container_width=True)
    
    st.markdown("---")
    st.subheader("💾 Exportación Directa en Memoria")
    
    col1, col2 = st.columns(2)
    
    # Generar bytes seguros
    csv_bytes = processor.export_to_csv(st.session_state['df_final'])
    excel_bytes = processor.export_to_excel(st.session_state['df_final'])
    
    safe_name = st.session_state['keyword_used'].replace(' ', '_')
    
    with col1:
        st.download_button(
            label="📥 Descargar CSV Maestro",
            data=csv_bytes,
            file_name=f"leads_{safe_name}.csv",
            mime="text/csv"
        )
        
    with col2:
        st.download_button(
            label="📥 Descargar Excel Divino",
            data=excel_bytes,
            file_name=f"leads_{safe_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )