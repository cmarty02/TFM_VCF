import streamlit as st
import pandas as pd
import io
from google.cloud import bigquery
from google.oauth2 import service_account
from funciones import upload_to_gcs, transform_dataframe, get_player_images
import requests
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="VCF Forecasting Scouting Model",
    page_icon="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png",
    layout="wide"
)

# Ruta a imágenes de jugadores
players_csv = 'img_players.csv'

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
    uploaded_file = st.file_uploader("Choose a file", type="xlsx")
    run_button = st.button('Upload and Run')

    # Agregar barra de progreso en la barra lateral
    progress_bar = st.progress(0)  # Inicializar la barra de progreso

# Placeholder for messages in the sidebar
status_placeholder = st.sidebar.empty()

# Variable de estado para mostrar el contenido
show_content = st.session_state.get('show_content', False)
show_predictions = st.session_state.get('show_predictions', False)

if run_button:
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

            with st.spinner("Processing..."):
                try:
                    # Actualizar la barra de progreso
                    progress_bar.progress(10)  # 10% - Inicio del proceso
                    # Guardar el DataFrame transformado en un buffer de memoria
                    buffer = io.StringIO()
                    df_transformed.to_csv(buffer, index=False)
                    buffer.seek(0)
                    
                    progress_bar.progress(30)  # 30% - Buffer creado
                    file_name = uploaded_file.name.replace('.xlsx', '.csv')
                    upload_to_gcs('tfm_vcf_bucket', file_name, io.BytesIO(buffer.getvalue().encode('utf-8')))
                    
                    progress_bar.progress(60)  # 60% - Archivo subido
                    # Mostrar mensaje de éxito en el sidebar
                    status_placeholder.success(f'File uploaded to tfm_vcf_bucket/{file_name}')
                    # Mostrar contenido después de la carga exitosa
                    show_content = True
                    st.session_state.show_content = True
                    
                    # Ejecutar predicciones después de la carga
                    url = 'https://api-161031452234.us-central1.run.app/run'
                    response = requests.get(url)
                    
                    if response.status_code == 200:
                        # Decodificar el JSON de la respuesta
                        data = response.json()

                        # Verificar el contenido de `data` para asegurarse de que es una lista de diccionarios
                        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                            # Convertir el JSON a DataFrame
                            df_predictions = pd.DataFrame(data)
                            
                            progress_bar.progress(80)  # 80% - Predicciones procesadas
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
                            show_predictions = True
                            st.session_state.show_predictions = True
                        else:
                            st.error("Formato de datos inesperado en la respuesta de la API.")
                            progress_bar.progress(0)
                    else:
                        st.error(f'Error {response.status_code}: {response.text}')
                        progress_bar.progress(0)
                        
                except Exception as e:
                    # Mostrar error en el sidebar
                    status_placeholder.error(f'Error al subir el archivo a GCS: {e}')
                    progress_bar.progress(0)
                    
        except Exception as e:
            # Mostrar error en el sidebar
            status_placeholder.error(f'Error al leer el archivo CSV: {e}')
            progress_bar.progress(0)

if show_content:
    # Mostrar la tabla de vista previa en la parte superior, ocupando todo el ancho
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
    st.divider()  # Divisor debajo de la tabla de vista previa

    # Mostrar las métricas en una sola fila
    st.subheader("Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_assists = df_with_images['asistencias'].mean()
        st.metric(label="Promedio Asistencias", value=f"{avg_assists:.2f}")

    with col2:
        avg_goals = df_with_images['goles'].mean()
        st.metric(label="Promedio Goles", value=f"{avg_goals:.2f}")

    with col3:
        avg_matches = df_with_images['partidos'].mean()
        st.metric(label="Promedio Partidos", value=f"{avg_matches:.2f}")

    with col4:
        avg_age = df_with_images['edad'].mean()
        st.metric(label="Promedio Edad", value=f"{avg_age:.2f}")

    st.divider()  # Divisor debajo de las métricas

    # Crear dos columnas para organizar el contenido horizontalmente
    col1, col2 = st.columns([1, 1])  # La segunda columna será más ancha

    with col1:
        # Resumen Estadístico General
        st.subheader("General Statistical Summary")
        summary = pd.DataFrame({
            "Promedio": df_with_images[['coste', 'vm_tm', 'partidos', 'goles', 'asistencias']].mean(),
            "Desviación Estándar": df_with_images[['coste', 'vm_tm', 'partidos', 'goles', 'asistencias']].std()
        }).reset_index().rename(columns={"index": "Métrica"})
        st.dataframe(summary)
        st.divider()

        # Distribución de Goles y Asistencias por Posición
        st.subheader("Goals and Assists Distribution by Position")
        position_stats = df_with_images.groupby('posicion')[['goles', 'asistencias']].agg(['sum', 'mean']).reset_index()
        position_stats.columns = ['Posición', 'Goles Total', 'Asistencias Total', 'Promedio Goles', 'Promedio Asistencias']
        st.dataframe(position_stats)
        st.divider()

    with col2:
        # Visualización de Coste vs Valor de Mercado usando Plotly
        st.subheader("Cost vs Market Value")
        fig_cost_vs_value = px.scatter(df_with_images, x='coste', y='vm_tm', color='posicion', 
                                       title='Cost vs Market Value',
                                       labels={'coste': 'Coste', 'vm_tm': 'Valor de Mercado (VM)'},
                                       height=400)  # Ajustar altura para hacerlo más pequeño
        st.plotly_chart(fig_cost_vs_value, use_container_width=True)
        st.divider()

        # Distribución de Nacionalidades usando Plotly
        st.subheader("Nationality Distribution")
        nationality_counts = df_with_images['nacionalidad'].value_counts().reset_index()
        nationality_counts.columns = ['Nacionalidad', 'Número de Jugadores']
        fig_nationality_distribution = px.pie(nationality_counts, names='Nacionalidad', values='Número de Jugadores',
                                              title='Distribución de Nacionalidades',
                                              hole=0.4)  # Gráfico de anillos
        st.plotly_chart(fig_nationality_distribution, use_container_width=True)
        st.divider()

        # Gráfico de Sankey para equipo de origen y destino
        st.subheader("Sankey Diagram of Transfer Flows")
        sankey_data = df_with_images.groupby(['equipo_origen', 'equipo_destino'])['coste'].sum().reset_index()
        
        # Crear un DataFrame para el gráfico Sankey
        labels = list(pd.concat([sankey_data['equipo_origen'], sankey_data['equipo_destino']]).unique())
        source_indices = [labels.index(e) for e in sankey_data['equipo_origen']]
        target_indices = [labels.index(e) for e in sankey_data['equipo_destino']]
        
        fig_sankey = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=sankey_data['coste']
            )
        ))
        fig_sankey.update_layout(title_text="Sankey Diagram of Transfer Flows", height=500)
        st.plotly_chart(fig_sankey, use_container_width=True)
        st.divider()
