import streamlit as st
import pandas as pd
import io
from funciones import upload_to_gcs, transform_dataframe, get_player_images
import numpy as np  # Asegúrate de importar numpy para los ejemplos de gráficos

# Configuración de la página
st.set_page_config(
    page_title="VCF Forecasting Scouting Model",
    page_icon="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png",
    layout="wide"
)

# Sidebar: Mantener la configuración actual
with st.sidebar:
    st.markdown(
        """
        <style>
        .sidebar-logo {
            display: flex;
            justify-content: center;
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .sidebar-logo img {
            width: 100px;
        }
        </style>
        <div class="sidebar-logo">
            <img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png" alt="Valencia CF Logo">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.header("VCF Forecasting Scouting Model")
    st.divider()
    st.subheader("Settings")
    uploaded_file = st.file_uploader("Choose a XLSX file", type="xlsx")
    upload_button = st.button('Upload')
    run_button = st.button('Run Predictions')

    # Agregar barra de progreso en la barra lateral
    progress_bar = st.progress(0)

# Layout de la página principal
st.title("Listado de Búsqueda")

# Crear tres columnas: una para la imagen, otra para la información del jugador
col1, col2 = st.columns([1, 2])

# Columna 1: Espacio para la imagen del jugador
with col1:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png", 
        caption="Foto del Jugador", 
        width=150
    )

# Columna 2: Información del jugador
with col2:
    st.subheader("Datos del Jugador")
    
    st.markdown("""
    - **$ Valor Predicho**: $XXX,XXX
    - **País**: España
    - **Posición**: Delantero
    - **Stats**: 10 goles, 5 asistencias, 20 partidos
    """)
    
    # Ejemplo de visualización de métricas
    st.metric(label="Valor Predicho", value="$XXX,XXX")
    st.metric(label="Posición", value="Delantero")
    st.metric(label="País", value="España")
    st.metric(label="Goles", value="10")
    st.metric(label="Asistencias", value="5")
    st.metric(label="Partidos Jugados", value="20")

# Footer (si hay que agregar algo más en la parte inferior)
st.write("© 2024 VCF Forecasting Scouting Model")