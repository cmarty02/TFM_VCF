# Configurar las credenciales y el cliente de Google Cloud Storage
import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import pandas as pd
import io
from sklearn.preprocessing import MinMaxScaler
import unidecode

# Ruta al archivo de credenciales JSON
CREDENTIALS_JSON_PATH = 'tfm-vcf-1f05acc80f94.json'

def get_gcs_client(json_credentials_path):
    credentials = service_account.Credentials.from_service_account_file(json_credentials_path)
    client = storage.Client(credentials=credentials)
    return client

def upload_to_gcs(bucket_name, destination_blob_name, file):
    client = get_gcs_client(CREDENTIALS_JSON_PATH)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)
    st.success(f'File uploaded to {bucket_name}/{destination_blob_name}')

# Función para transformar el DataFrame
def transform_dataframe(df):
    try:
        # Renombrar las columnas: quitar acentos, convertir a minúsculas y reemplazar espacios con guiones bajos
        df.columns = [unidecode.unidecode(col).lower().replace(' ', '_').replace('(', '').replace(')', '') for col in df.columns]

        # Verificar columnas requeridas
        required_columns = [
            'jugador', 'posicion', 'edad', 'nacionalidad', 'temporada', 'fecha', 
            'coste', 'vm_tm', 'equipo_origen', 'elo_eo', 'equipo_destino', 
            'elo_ed', 'competicion_origen', 'elo_co', 'competicion_destino', 
            'elo_cd', 'partidos', 'goles', 'asistencias', 'goles_concedidos', 
            'rdt'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f'Faltan las siguientes columnas en el archivo: {", ".join(missing_columns)}')
            return None

        # Convertir las fechas a números ordinales
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').map(pd.Timestamp.toordinal)

        # Eliminar la columna 'c/vm' si existe
        df.drop(columns=['c/vm'], inplace=True, errors='ignore')

        # Reemplazar "-" con NaN y convertir a float para columnas numéricas
        numeric_columns = ['elo_eo', 'elo_co', 'partidos', 'vm_tm', 'goles', 'asistencias', 'goles_concedidos', 'rdt']
        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column].replace("-", "0"), errors='coerce')

        # Asegurarse de que las columnas numéricas tengan el tipo de dato correcto
        df[numeric_columns] = df[numeric_columns].astype(float)

        # Definir los bins y las etiquetas para la clasificación
        bins = [0, 5, 10, 15, 20, 25, 35, 50, 70, float('inf')]
        labels = [9, 8, 7, 6, 5, 4, 3, 2, 1]

        # Crear la columna 'clasificacion' usando pd.cut()
        if 'coste' in df.columns:
            df['clasificacion'] = pd.cut(df['coste'], bins=bins, labels=labels, right=False)

        # Normalizar características numéricas
        scaler = MinMaxScaler()
        df[numeric_columns] = scaler.fit_transform(df[numeric_columns])

        # Reordenar columnas para que coincidan con el formato requerido
        required_columns_with_clasificacion = required_columns + ['clasificacion']
        df = df[required_columns_with_clasificacion]

        # Convertir la columna 'clasificacion' a tipo 'category'
        df['clasificacion'] = df['clasificacion'].astype('category')

        return df

    except Exception as e:
        st.error(f'Error durante la transformación del archivo: {e}')
        return None