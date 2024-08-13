import streamlit as st
import pandas as pd
import io
from funciones import upload_to_gcs, transform_dataframe, get_player_images

# Configuración de la página
st.set_page_config(
    page_title="VCF Forecasting Scouting Model",
    page_icon="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png",
    layout="wide"
)

# Ruta a imágenes de jugadores
players_csv = 'D:/Dropbox/Facu/EDEM/GitHub/GitHub_Repositorios/TFM_VCF/streamlit/img_players.csv'

# Crear dos columnas
col1, col2 = st.columns([1, 1])  # Puedes ajustar los números para cambiar el tamaño de las columnas

with col1:
    st.header("Uploaded Data")
    st.divider()

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
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    upload_button = st.button('Upload')

# Placeholder for messages in the sidebar
status_placeholder = st.sidebar.empty()

if uploaded_file is not None:
    try:
        # Leer el archivo CSV
        df = pd.read_csv(uploaded_file)
        
        # Transformar el DataFrame
        df_transformed = transform_dataframe(df)
        
        # Obtener URLs de imágenes de jugadores y agregar al DataFrame
        df_with_images = get_player_images(df_transformed, players_csv)

        # Reordenar las columnas para que 'img_player' esté primero
        columns_order = ['img_player'] + [col for col in df_with_images.columns if col != 'img_player']
        df_with_images = df_with_images[columns_order]

        # Acción del botón de carga
        if upload_button:
            try:
                # Guardar el DataFrame transformado en un buffer de memoria y subirlo a GCS
                buffer = io.StringIO()
                df_transformed.to_csv(buffer, index=False)
                buffer.seek(0)
                file_name = uploaded_file.name
                upload_to_gcs('tfm_vcf_bucket', file_name, io.BytesIO(buffer.getvalue().encode('utf-8')))
                
                # Mostrar mensaje de éxito en el sidebar
                status_placeholder.success(f'File uploaded to tfm_vcf_bucket/{file_name}')
                
                # Mostrar el DataFrame transformado en la columna izquierda
                with col1:
                    st.data_editor(
                        df_with_images,
                        column_config={
                            "img_player": st.column_config.ImageColumn(
                                "Image_player", help="Streamlit app preview screenshots"
                            )
                        },
                        hide_index=True,
                    )
                
            except Exception as e:
                # Mostrar error en el sidebar
                status_placeholder.error(f'Error al subir el archivo a GCS: {e}')
    except Exception as e:
        # Mostrar error en el sidebar
        status_placeholder.error(f'Error al leer el archivo CSV: {e}')

# Mensaje en la columna derecha (por ahora solo un encabezado)
with col2:
    st.header("Metrics")
    st.divider()
