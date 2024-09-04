from flask import Flask, request, jsonify
import requests
from google.cloud import bigquery
from google.auth import default
import os
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configuración de BigQuery
BQ_DATASET = 'tfm_vcf_dataset'
BQ_TABLE = 'tfm_vcf_table'
PROJECT_ID = 'tfm-vcf'

# Usar las credenciales predeterminadas del entorno de ejecución
credentials, project = default()
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

@app.route('/run', methods=['GET', 'POST'])
def run_predictions():
    try:
        # Activar Cloud Run
        url = 'https://predict-161031452234.us-central1.run.app/predicciones'
        response = requests.get(url)
        
        if response.status_code != 200:
            return jsonify({'error': f'Error {response.status_code}: {response.text}'}), response.status_code
        
        # Consultar BigQuery
        query = f"""
            SELECT img_player, jugador, prediccion
            FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
            WHERE upload_id = (
                SELECT MAX(upload_id) FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
            )
        """
        df_predictions = client.query(query).to_dataframe()
        
        # Convertir DataFrame a JSON
        predictions_json = df_predictions.to_dict(orient='records')
        
        return jsonify(predictions_json)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
