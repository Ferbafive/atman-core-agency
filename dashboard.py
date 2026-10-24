import os
import sys
import pandas as pd
import streamlit as st
from app.database.init_db import get_db, init_db
from app.database.models import Lead

# Importamos la función principal de tu script de producción directamente
try:
    from run_production import main as run_pipeline
except ImportError:
    run_pipeline = None

# Configuración de la página web
st.set_page_config(
    page_title="Atman Core Agency - Control Panel",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Atman Core Agency - Dashboard B2B")
st.markdown("---")

# Función para cargar datos desde la base de datos de manera segura
def load_data():
    try:
        init_db()  # Asegura que las tablas estén creadas en SQLite
        db = next(get_db())
        leads = db.query(Lead).all()
        
        if not leads:
            return pd.DataFrame()
        
        data = []
        for l in leads:
            data.append({
                "ID": l.id,
                "Empresa": l.company_name,
                "URL": l.url,
                "Email": l.contact_email if l.contact_email else "Sin email",
                "Teléfono": l.phone if l.phone else "Sin teléfono",
                "Score": l.score,
                "Cualificado": "✅ Sí" if l.is_qualified else "❌ No"
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame()

# Panel Lateral de Control
st.sidebar.header("🕹️ Centro de Control")

# Botón para ejecutar el pipeline desde la web
if st.sidebar.button("🔥 Ejecutar Pipeline en Vivo"):
    st.sidebar.info("🚀 Lote de prospección iniciado... espera unos segundos.")
    try:
        if run_pipeline is not None:
            # Ejecución directa en Python sin usar subprocess
            run_pipeline()
            st.sidebar.success("✅ ¡Pipeline ejecutado con éxito!")
            st.rerun()
        else:
            st.sidebar.error("❌ No se encontró la función principal en 'run_production.py'.")
    except Exception as e:
        st.sidebar.error(f"❌ Error durante la ejecución: {e}")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros")

df = load_data()

if df.empty:
    st.warning("⚠️ La base de datos está vacía. Haz clic en 'Ejecutar Pipeline en Vivo' en el menú lateral o ejecuta 'run_production.py'.")
else:
    # 1. Métricas Principales (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    total_leads = len(df)
    qualified_leads = len(df[df["Cualificado"] == "✅ Sí"])
    emails_found = len(df[df["Email"] != "Sin email"])
    avg_score = round(df["Score"].mean(), 1)

    col1.metric("Total Leads", total_leads)
    col2.metric("Leads Cualificados", qualified_leads)
    col3.metric("Emails Capturados", emails_found)
    col4.metric("Score Promedio", f"{avg_score} pts")

    st.markdown("---")

    # 2. Aplicación de Filtros
    filter_qualified = st.sidebar.selectbox("Estado de Cualificación", ["Todos", "Solo Cualificados", "No Cualificados"])
    
    filtered_df = df.copy()
    if filter_qualified == "Solo Cualificados":
        filtered_df = filtered_df[filtered_df["Cualificado"] == "✅ Sí"]
    elif filter_qualified == "No Cualificados":
        filtered_df = filtered_df[filtered_df["Cualificado"] == "❌ No"]

    search_term = st.sidebar.text_input("Buscar empresa o email:")
    if search_term:
        filtered_df = filtered_df[
            filtered_df["Empresa"].str.contains(search_term, case=False, na=False) |
            filtered_df["Email"].str.contains(search_term, case=False, na=False)
        ]

    # 3. Visualización de Datos
    st.subheader(f"📋 Lista de Leads Capturados ({len(filtered_df)})")
    st.dataframe(filtered_df, use_container_width=True)

    # 4. Descargar Selección
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Leads Seleccionados (CSV)",
        data=csv,
        file_name='leads_filtrados.csv',
        mime='text/csv',
    )