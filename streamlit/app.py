import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import pandas as pd
import io

# Ruta al archivo de credenciales JSON
CREDENTIALS_JSON_PATH = 'tfm-vcf-1f05acc80f94.json'

# Configurar las credenciales y el cliente de Google Cloud Storage
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

# Interfaz de Streamlit
st.title('Upload CSV to Google Cloud Storage')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Display the file content
    df = pd.read_csv(uploaded_file)
    st.write(df)

    # Save file to GCS
    if st.button('Upload to GCS'):
        file_name = uploaded_file.name
        upload_to_gcs('tfm_vcf_bucket', file_name, io.BytesIO(uploaded_file.getvalue()))
