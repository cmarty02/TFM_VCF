import streamlit as st
import pandas as pd
import io
from funciones import upload_to_gcs, transform_dataframe, get_player_images

#Ruta a imagenes de jugadores
players_csv = 'D:\Dropbox\Facu\EDEM\GitHub\GitHub_Repositorios\TFM_VCF\streamlit\img_players.csv'

# Interfaz de Streamlit
st.markdown(
    """
    <style>
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 150px;
        margin-bottom: -10px; /* Ajustar según sea necesario */
    }
    .center img {
        width: 100px; /* Ajustar el ancho según sea necesario */
    }
    </style>
    <div class="center">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/176px-Valenciacf.svg.png" alt="Valencia CF Logo">
    </div>
    """,
    unsafe_allow_html=True
)

st.title('VCF Forecasting Scouting Model')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Leer el archivo CSV
        df = pd.read_csv(uploaded_file)
        
        # Transformar el DataFrame
        df_transformed = transform_dataframe(df)
        
        # Obtener URLs de imágenes de jugadores y agregar al DataFrame
        df_with_images = get_player_images(df_transformed, players_csv)

        if df_transformed is not None:
            st.write("Transformed DataFrame:")
            st.write(df_transformed)

            # Guardar el DataFrame transformado en un buffer de memoria y subirlo a GCS
            if st.button('Upload to GCS'):
                try:
                    buffer = io.StringIO()
                    df_transformed.to_csv(buffer, index=False)
                    buffer.seek(0)
                    file_name = uploaded_file.name
                    upload_to_gcs('tfm_vcf_bucket', file_name, io.BytesIO(buffer.getvalue().encode('utf-8')))
                except Exception as e:
                    st.error(f'Error al subir el archivo a GCS: {e}')
        else:
            st.error('El DataFrame transformado es None. Verifica los errores anteriores.')

    except Exception as e:
        st.error(f'Error al leer el archivo CSV: {e}')
