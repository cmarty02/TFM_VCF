from flask import Flask, jsonify
import pandas as pd
import pickle
from google.cloud import bigquery
import os
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configuración de BigQuery y del modelo
BQ_DATASET = 'tfm_vcf_dataset'
BQ_TABLE = 'tfm_vcf_table'
PROJECT_ID = 'tfm-vcf'
MODEL_PATH = 'random_forest_grid_search_best_setup.pkl'

# Cargar el modelo una vez al inicio
try:
    with open(MODEL_PATH, 'rb') as model_file:
        model = pickle.load(model_file)
    logging.info('Modelo cargado exitosamente.')
except Exception as e:
    logging.error(f'Error al cargar el modelo: {e}')
    model = None

@app.route('/predict', methods=['GET'])
def predict():
    if model is None:
        return jsonify({'error': 'Modelo no disponible'}), 500

    try:
        # Crear cliente de BigQuery
        client = bigquery.Client()

        # Consulta a BigQuery
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
        WHERE upload_id = (
            SELECT MAX(upload_id)
            FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
        )
        """
        query_job = client.query(query)
        results = query_job.result()
        df = results.to_dataframe()

        # Preparar los datos para predicción
        df_selected_test = df[['jugador', 'edad', 'partidos']]
        predictions = model.predict(df_selected_test[['edad', 'partidos']])
        df_selected_test['goles_predichos'] = predictions

        # Convertir DataFrame a JSON
        result = df_selected_test.to_json(orient='records')
        return result

    except Exception as e:
        logging.error(f'Error durante la predicción: {e}')
        return jsonify({'error': 'Error en la predicción'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
