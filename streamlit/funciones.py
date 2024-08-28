# Configurar las credenciales y el cliente de Google Cloud Storage
import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import unidecode
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

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


        # Eliminar la columna 'c/vm' si existe
        df.drop(columns=['c/vm'], inplace=True, errors='ignore')

        # Reemplazar "-" con NaN y convertir a float para columnas numéricas
        numeric_columns = ['elo_eo', 'elo_co', 'partidos', 'vm_tm', 'goles', 'asistencias', 'goles_concedidos', 'rdt']
        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column].replace("-", "0"), errors='coerce')

        # Asegurarse de que las columnas numéricas tengan el tipo de dato correcto
        df[numeric_columns] = df[numeric_columns].astype(float)

        return df

    except Exception as e:
        st.error(f'Error durante la transformación del archivo: {e}')
        return None


# Función para obtener imagenes de jugadores
def get_player_images(input_df, players_csv):
  
    def get_player_image_url(player_name):
        # Verificar si el nombre contiene una inicial seguida de un punto
        if '.' in player_name.split()[0]:
            # Si es así, solo usamos el apellido para la búsqueda
            player_name = player_name.split()[-1]
        else:
            # Reemplaza los espacios en el nombre del jugador con '+'
            player_name = player_name.replace(" ", "+")
        
        # URL de búsqueda en Transfermarkt
        search_url = f"https://www.transfermarkt.es/schnellsuche/ergebnis/schnellsuche?query={player_name}"
        
        # Añade una cabecera de usuario para que la solicitud parezca provenir de un navegador real
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Realizar la solicitud HTTP
        response = requests.get(search_url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error al acceder a la página de {player_name}")
            return None
        
        # Analizar la respuesta HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            # Utilizar selectores CSS para encontrar el <img> dentro del <a>
            img_element = soup.select_one('div.responsive-table table.items tbody tr td a img.bilderrahmen-fixed')
            
            if img_element:
                # Extraer el src del elemento img
                img_src = img_element.get('src')
                # Reemplazar 'small' por 'big' en la URL
                img_src = img_src.replace('small', 'big')
                return img_src
            else:
                print(f"No se encontró la imagen para {player_name}")
                return None
        except Exception as e:
            print(f"Error al procesar la página para {player_name}: {e}")
            return None

    def process_players(df, csv_file):
        # Leer el CSV existente que contiene las URLs de las imágenes
        try:
            existing_df = pd.read_csv(csv_file)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=['jugador', 'img_player'])  # Si no existe, crea un DataFrame vacío
        
        # Crear una nueva columna para las URLs de las imágenes con barra de progreso
        tqdm.pandas(desc="Procesando jugadores")
        
        def find_or_scrape_image(player_name):
            # Buscar si el jugador ya está en el CSV existente
            if player_name in existing_df['jugador'].values:
                # Si está, devolver la URL existente
                return existing_df[existing_df['jugador'] == player_name]['img_player'].values[0]
            else:
                # Si no está, realizar la búsqueda con el scraper
                return get_player_image_url(player_name)
        
        # Aplicar la función a cada jugador en el DataFrame
        df['img_player'] = df['jugador'].progress_apply(find_or_scrape_image)
        
        # Retornar el DataFrame original con la nueva columna añadida
        return df

    # Procesar los jugadores para obtener las URLs de las imágenes
    df_processed = process_players(input_df, players_csv)
    # Retornar el DataFrame con todos los datos y la nueva columna 'img_player'
    return df_processed
