import pandas as pd
import unidecode
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import numpy as np


def pre_procesado(df_football):
    # Convertir las fechas a números ordinales
    df_football['fecha'] = pd.to_datetime(df_football['fecha']).map(pd.Timestamp.toordinal)

    # Eliminar la columnas
    df_football.drop(columns=['equipo_origen','upload_id','file_hash','img_player','equipo_destino', 'competicion_origen', 'competicion_destino'], inplace=True)

    # Codificar los campos categóricos con LabelEncoder para el embedding
    le_position = LabelEncoder()
    le_nationality = LabelEncoder()

    df_football['posicion'] = le_position.fit_transform(df_football['posicion'])
    df_football['nacionalidad'] = le_nationality.fit_transform(df_football['nacionalidad'])

    # Crear embeddings para las columnas categóricas utilizando un enfoque simple
    categorical_columns = ['posicion', 'nacionalidad']
    embedding_size = 5  # Tamaño del embedding, ajustable según el caso

    for col in categorical_columns:
        # Crear un embedding aleatorio para cada valor categórico
        unique_values = df_football[col].nunique()
        np.random.seed(42)
        embedding_matrix = np.random.rand(unique_values, embedding_size)

        # Reemplazar los valores categóricos con sus correspondientes embeddings
        df_football[col] = df_football[col].apply(lambda x: embedding_matrix[x])

        # Expandir la columna de embedding en varias columnas
        embedding_df = pd.DataFrame(df_football[col].tolist(), index=df_football.index,
                                    columns=[f"{col}_emb_{i}" for i in range(embedding_size)])
        df_football = pd.concat([df_football, embedding_df], axis=1)
        df_football.drop(columns=[col], inplace=True)

    embedding_columns = [f"{col}_emb_{i}" for col in categorical_columns for i in range(embedding_size)]

    # Añadir las columnas de embedding a la lista de columnas numéricas
    numeric_columns += embedding_columns

    # Normalizar características numéricas después de aplicar el embedding
    scaler = MinMaxScaler()
    df_football[numeric_columns] = scaler.fit_transform(df_football[numeric_columns])

    return df_football