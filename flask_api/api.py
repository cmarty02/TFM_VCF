from flask import Flask, request, jsonify
import pandas as pd
import joblib
from google.cloud import storage
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

app = Flask(__name__)

# Cargar el modelo más reciente desde Google Cloud Storage
def load_latest_model():
    client = storage.Client()
    bucket = client.get_bucket('tfm_vcf_models')
    blobs = bucket.list_blobs()

    latest_blob = None
    for blob in blobs:
        if latest_blob is None or blob.updated > latest_blob.updated:
            latest_blob = blob

    model = None
    if latest_blob:
        blob.download_to_filename('/tmp/model.pkl')
        model = joblib.load('/tmp/model.pkl')
    return model

model = load_latest_model()

# Preprocesar el DataFrame
def preprocesar(df_football):
    df_football['fecha'] = pd.to_datetime(df_football['fecha']).map(pd.Timestamp.toordinal)
    df_football.drop(columns=['equipo_origen','upload_id','file_hash','img_player','equipo_destino', 'competicion_origen', 'competicion_destino'], inplace=True)
    
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
        df_football[col] = df_football[col].apply(lambda x: embedding_matrix[x])
        embedding_df = pd.DataFrame(df_football[col].tolist(), index=df_football.index,
                                    columns=[f"{col}_emb_{i}" for i in range(embedding_size)])
        df_football = pd.concat([df_football, embedding_df], axis=1)
        df_football.drop(columns=[col], inplace=True)

    numeric_columns = ['edad', 'coste', 'vm_tm', 'elo_eo', 'elo_ed', 'elo_co', 'elo_cd', 'partidos', 'goles', 'asistencias', 'goles_concedidos', 'rdt']
    embedding_columns = [f"{col}_emb_{i}" for col in categorical_columns for i in range(embedding_size)]
    numeric_columns += embedding_columns
    
    scaler = MinMaxScaler()
    df_football[numeric_columns] = scaler.fit_transform(df_football[numeric_columns])

    return df_football

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    df = pd.DataFrame(data)
    
    df_processed = preprocesar(df)
    
    X_new = df_processed.drop(columns=['jugador', 'coste', 'temporada'])

    predictions = model.predict(X_new)

    df['prediccion'] = predictions

    return jsonify(df[['jugador', 'prediccion']].to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
