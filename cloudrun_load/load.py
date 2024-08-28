from flask import Flask, request
import pandas as pd
from google.cloud import storage, bigquery
import os
import io
import json
import base64
from datetime import datetime
import logging
import hashlib

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configurar valores específicos
BUCKET_NAME = 'tfm_vcf_bucket'  # Nombre del bucket
BQ_DATASET = 'tfm_vcf_dataset'  # Nombre del dataset en BigQuery
BQ_TABLE = 'tfm_vcf_table1'      # Nombre de la tabla en BigQuery
PROJECT_ID = 'tfm-vcf'          # ID del proyecto

# Verificar que los valores están configurados correctamente
logging.info(f"BUCKET_NAME: {BUCKET_NAME}")
logging.info(f"BQ_DATASET: {BQ_DATASET}")
logging.info(f"BQ_TABLE: {BQ_TABLE}")
logging.info(f"PROJECT_ID: {PROJECT_ID}")

# Inicializar el cliente de Google Cloud Storage
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)

# Inicializar el cliente de BigQuery con el PROJECT_ID correcto
bq_client = bigquery.Client(project=PROJECT_ID)

@app.route('/', methods=['POST'])
def index():
    logging.info("Solicitud POST recibida")
    try:
        # Obtener el evento de Pub/Sub
        envelope = request.get_json()
        if not envelope:
            logging.error("No se recibió ningún mensaje de Pub/Sub")
            return 'Bad Request: no Pub/Sub message received', 400
        if 'message' not in envelope:
            logging.error("Formato de mensaje de Pub/Sub inválido")
            return 'Bad Request: invalid Pub/Sub message format', 400

        pubsub_message = envelope['message']
        if 'data' not in pubsub_message:
            logging.error("No hay datos en el mensaje de Pub/Sub")
            return 'Bad Request: no data in Pub/Sub message', 400

        # Decodificar el mensaje de Pub/Sub
        data = base64.b64decode(pubsub_message['data']).decode('utf-8')
        event = json.loads(data)

        try:
            # Procesar el archivo subido
            file_name = event['name']
            logging.info(f"Procesando el archivo: {file_name}")
            blob = bucket.blob(file_name)
            content = blob.download_as_text()
            df = pd.read_csv(io.StringIO(content))

            # Mostrar los primeros registros del DataFrame para verificar
            logging.info(f"Primeros registros del DataFrame: {df.head()}")

            # Generar hash del contenido del archivo
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            logging.info(f"Hash del archivo: {file_hash}")

            # Agregar una columna de ID de subida con la fecha y hora actual
            df['upload_id'] = datetime.now().isoformat()
            df['file_hash'] = file_hash

            # Definir la referencia a la tabla de BigQuery
            table_id = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"
            job = bq_client.load_table_from_dataframe(df, table_id)

            # Esperar a que el trabajo de carga se complete
            job.result()
            logging.info(f"Datos cargados en BigQuery correctamente: {table_id}")

        except Exception as e:
            logging.error(f"Error procesando el archivo {file_name}: {e}")
            return f'Error procesando el archivo {file_name}: {e}', 500

    except Exception as e:
        logging.error(f"Error en el procesamiento del mensaje de Pub/Sub: {e}")
        return f'Error en el procesamiento del mensaje de Pub/Sub: {e}', 500

    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
