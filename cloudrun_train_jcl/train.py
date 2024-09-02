from flask import Flask, jsonify
from google.cloud import storage, bigquery
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import joblib
import os

app = Flask(__name__)

# Configura el proyecto de BigQuery
project_id = 'tfm-vcf'

def cargar_datos_bigquery():
    query = """
    SELECT *
    FROM `tfm-vcf.tfm_vcf_dataset.tfm_vcf_table`
    """
    df = pd.read_gbq(query, project_id=project_id, dialect='standard')
    return df

def adaptacion_columnas(df_football):
    df_football['fecha'] = pd.to_datetime(df_football['fecha']).map(pd.Timestamp.toordinal)
    df_football.drop(columns=['equipo_origen', 'equipo_destino', 'competicion_origen', 'competicion_destino','upload_id','file_hash','img_player'], inplace=True)
    columnas_a_convertir = ['jugador', 'posicion', 'nacionalidad', 'temporada']
    df_football[columnas_a_convertir] = df_football[columnas_a_convertir].astype('string')
    return df_football

def embedding(df_football):
    le_position = LabelEncoder()
    le_nationality = LabelEncoder()
    df_football['posicion'] = le_position.fit_transform(df_football['posicion'])
    df_football['nacionalidad'] = le_nationality.fit_transform(df_football['nacionalidad'])

    categorical_columns = ['posicion', 'nacionalidad']
    embedding_size = 5

    for col in categorical_columns:
        unique_values = df_football[col].nunique()
        np.random.seed(42)
        embedding_matrix = np.random.rand(unique_values, embedding_size)

        for i in range(embedding_size):
            df_football[f"{col}_emb_{i}"] = df_football[col].apply(lambda x: embedding_matrix[x][i])

    embedding_columns = [f"{col}_emb_{i}" for col in categorical_columns for i in range(embedding_size)]

    numeric_columns = ['edad', 'coste','fecha', 'vm_tm', 'elo_eo', 'elo_ed', 'elo_co', 'elo_cd', 'partidos', 'goles', 'asistencias', 'goles_concedidos', 'rdt','edad']
    numeric_columns += embedding_columns

    df_football.drop(columns=['posicion', 'nacionalidad'], inplace=True)
    scaler = MinMaxScaler()
    df_football[numeric_columns] = scaler.fit_transform(df_football[numeric_columns])

    return df_football

def load_latest_model_from_gcs():
    bucket_name = 'tfm_vcf_models'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    latest_blob = None
    for blob in blobs:
        if latest_blob is None or blob.updated > latest_blob.updated:
            latest_blob = blob

    if latest_blob:
        blob.download_to_filename('/tmp/model.pkl')
        model = joblib.load('/tmp/model.pkl')
        return model
    else:
        raise FileNotFoundError("No se encontró ningún modelo en el bucket.")

def ejecutar_prediccion(df):
    jugadores = df['jugador'].copy()
    X_new = df.drop(columns=['jugador', 'coste', 'temporada', 'prediccion'])
    model = load_latest_model_from_gcs()
    predicciones = model.predict(X_new)
    df['prediccion'] = predicciones
    df['jugador'] = jugadores
    df = df[['jugador', 'prediccion'] + [col for col in df.columns if col not in ['jugador', 'prediccion']]]
    return df

def actualizar_predicciones_bigquery(df, project_id, dataset_id, table_id):
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    for index, row in df.iterrows():
        jugador = row['jugador']
        prediccion = row['prediccion']
        temporada =row['temporada']

        query = f"""
        UPDATE `{table_ref}`
        SET prediccion = @prediccion
        WHERE jugador = @jugador
        AND temporada = @temporada
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("prediccion", "INT64", int(prediccion)),
                bigquery.ScalarQueryParameter("jugador", "STRING", str(jugador)),
                bigquery.ScalarQueryParameter("temporada", "STRING", str(temporada))
            ]
        )

        query_job = client.query(query, job_config=job_config)
        query_job.result()

@app.route('/predicciones', methods=['POST'])
def predicciones():
    try:
        df = cargar_datos_bigquery()
        df = adaptacion_columnas(df)
        df = embedding(df)
        df = ejecutar_prediccion(df)
        actualizar_predicciones_bigquery(df, project_id, 'tfm_vcf_dataset', 'tfm_vcf_table')
        return jsonify({"message": "Predicciones actualizadas en BigQuery con éxito!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)