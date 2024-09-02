import streamlit as st
import pandas as pd
import io
from google.cloud import bigquery
from google.oauth2 import service_account
from funciones import upload_to_gcs, transform_dataframe, get_player_images
import requests
import time  # Importar time para simular el progreso

# Configuración de la página
st.set_page_config(
    page_title="VCF Forecasting Scouting Model",
    page_icon="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png",
    layout="wide"
)

# Ruta a imágenes de jugadores
players_csv = 'D:/Dropbox/Facu/EDEM/GitHub/GitHub_Repositorios/TFM_VCF/streamlit/img_players.csv'

# Configuración de BigQuery y del modelo
BQ_DATASET = 'tfm_vcf_dataset'
BQ_TABLE = 'tfm_vcf_table'
PROJECT_ID = 'tfm-vcf'

# Configuración de las credenciales para BigQuery
credentials = service_account.Credentials.from_service_account_file('tfm-vcf-1f05acc80f94.json')
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

# Sidebar
with st.sidebar:
    # Logo centrado en el sidebar
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
            width: 100px; /* Ajusta el tamaño del logo según sea necesario */
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
    uploaded_file = st.file_uploader("Choose a xlsx file", type="xlsx")
    upload_button = st.button('Upload')
    run_button = st.button('Run Predictions')
    
    # Agregar barra de progreso en la barra lateral
    progress_bar = st.progress(0)  # Inicializar la barra de progreso

# Placeholder for messages in the sidebar
status_placeholder = st.sidebar.empty()

# Variable de estado para mostrar el contenido
show_content = st.session_state.get('show_content', False)

if uploaded_file is not None:
    try:
        # Leer el archivo CSV
        df = pd.read_excel(uploaded_file)
        
        # Transformar el DataFrame
        df_transformed = transform_dataframe(df)
        
        # Obtener URLs de imágenes de jugadores y agregar al DataFrame
        df_with_images = get_player_images(df_transformed, players_csv)

        # Reordenar las columnas para que 'img_player' esté primero
        columns_order = ['img_player'] + [col for col in df_with_images.columns if col != 'img_player']
        df_with_images = df_with_images[columns_order]

        if upload_button:
            # Acción del botón de carga
            try:
                progress_bar.progress(25)  # Actualizar la barra de progreso al 25%
                # Guardar el DataFrame transformado en un buffer de memoria y subirlo a GCS
                buffer = io.StringIO()
                df_transformed.to_csv(buffer, index=False)
                buffer.seek(0)
                file_name = uploaded_file.name.replace('.xlsx', '.csv')
                upload_to_gcs('tfm_vcf_bucket', file_name, io.BytesIO(buffer.getvalue().encode('utf-8')))
                
                # Mostrar mensaje de éxito en el sidebar
                status_placeholder.success(f'File uploaded to tfm_vcf_bucket/{file_name}')
                # Mostrar contenido después de la carga exitosa
                show_content = True
                st.session_state.show_content = True
                
                # Finalizar la barra de progreso
                progress_bar.progress(100)
                
            except Exception as e:
                # Mostrar error en el sidebar
                status_placeholder.error(f'Error al subir el archivo a GCS: {e}')
                progress_bar.progress(0)
    
    except Exception as e:
        # Mostrar error en el sidebar
        status_placeholder.error(f'Error al leer el archivo CSV: {e}')
        progress_bar.progress(0)

if show_content:
    # Mostrar el DataFrame transformado en la columna izquierda
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Mostrar el subheader antes del DataFrame
        st.subheader("Preview")
        st.data_editor(
            df_with_images,
            column_config={
                "img_player": st.column_config.ImageColumn(
                    "Image_player", help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
        )

    # Mostrar las métricas en la columna derecha
    with col2:
        st.subheader("Metrics")

        # Calcular las métricas
        avg_assists = df_with_images['asistencias'].mean()
        avg_goals = df_with_images['goles'].mean()
        avg_matches = df_with_images['partidos'].mean()
        avg_age = df_with_images['edad'].mean()
        
        # Fila superior de métricas
        col2_metric1, col2_metric2 = st.columns(2)
        with col2_metric1:
            st.metric(label="Promedio Asistencias", value=f"{avg_assists:.2f}")
        with col2_metric2:
            st.metric(label="Promedio Goles", value=f"{avg_goals:.2f}")

        # Espacio entre las métricas
        st.divider()

        # Fila inferior de métricas
        col2_metric3, col2_metric4 = st.columns(2)
        with col2_metric3:
            st.metric(label="Promedio Partidos", value=f"{avg_matches:.2f}")
        with col2_metric4:
            st.metric(label="Promedio Edad", value=f"{avg_age:.2f}")

if run_button and show_content:
    try:
        # Llamar al servicio de Cloud Run
        progress_bar.progress(50)  # Actualizar la barra de progreso al 50%
        url = 'https://cloud-run-juan-3-161031452234.europe-west1.run.app'
        response = requests.get(url)
        
        if response.status_code == 200:
            # Cloud Run ejecutado exitosamente, ahora consultar BigQuery
            progress_bar.progress(75)  # Actualizar la barra de progreso al 75%

            # Consultar BigQuery
            query = f"""
                SELECT img_player, jugador, prediccion
                FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
                WHERE upload_id = (
                    SELECT MAX(upload_id) FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
                )
                    """
            df_predictions = client.query(query).to_dataframe()

            # Mostrar el DataFrame de predicciones
            st.subheader("Predictions")
            st.data_editor(
                df_predictions,
                column_config={
                    "img_player": st.column_config.ImageColumn(
                        "Image_player", help="Streamlit app prediction images"
                    )
                },
                hide_index=True,
            )
            # Finalizar la barra de progreso
            progress_bar.progress(100)
        else:
            st.error(f'Error {response.status_code}: {response.text}')
            progress_bar.progress(0)
    except Exception as e:
        st.error(f'Error al realizar la predicción: {e}')
        progress_bar.progress(0)
