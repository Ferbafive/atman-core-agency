import os
import pandas as pd
import streamlit as st
from app.database.init_db import get_db
from app.database.models import Lead

# Configuración inicial de la página web
st.set_page_config(
    page_title="Atman Core Agency - Control Panel",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Atman Core Agency - Dashboard de Prospección B2B")
st.markdown("---")

# Función para extraer datos desde SQLite a un DataFrame de Pandas
def load_data():
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
            "Cualificado": "✅ Sí" if l.is_qualified else "❌ No",
            "Fecha": l.created_at.strftime("%Y-%m-%d %H:%M") if l.created_at else "N/A"
        })
    return pd.DataFrame(data)

df = load_data()

if df.empty:
    st.warning("⚠️ La base de datos está vacía. Ejecuta 'run_production.py' para capturar los primeros leads.")
else:
    # 1. Métricas Principales (Kpis)
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

    # 2. Panel de Filtros Laterales
    st.sidebar.header("🔍 Filtros de Búsqueda")
    filter_qualified = st.sidebar.selectbox("Estado de Cualificación", ["Todos", "Solo Cualificados", "No Cualificados"])
    
    filtered_df = df.copy()
    if filter_qualified == "Solo Cualificados":
        filtered_df = filtered_df[filtered_df["Cualificado"] == "✅ Sí"]
    elif filter_qualified == "No Cualificados":
        filtered_df = filtered_df[filtered_df["Cualificado"] == "❌ No"]

    # Buscador por palabra clave o email
    search_term = st.sidebar.text_input("Buscar empresa o email:")
    if search_term:
        filtered_df = filtered_df[
            filtered_df["Empresa"].str.contains(search_term, case=False, na=False) |
            filtered_df["Email"].str.contains(search_term, case=False, na=False)
        ]

    # 3. Tabla Interactiva de Datos
    st.subheader(f"📋 Lista de Leads Capturados ({len(filtered_df)})")
    st.dataframe(filtered_df, use_container_width=True)

    # 4. Botón de Exportación en vivo
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Selección a CSV",
        data=csv,
        file_name='leads_filtrados.csv',
        mime='text/csv',
    )