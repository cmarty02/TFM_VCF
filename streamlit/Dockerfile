# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos y lo instala
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copia todos los archivos Python necesarios
COPY app.py .
COPY elements.py .
COPY funciones.py .
COPY img_players.csv .
COPY elements.py .
COPY funciones.py .
COPY tfm-vcf-1f05acc80f94.json .


# Copia las carpetas
COPY .streamlit/ ./.streamlit/


# Informa a Docker que el contenedor puede escuchar en cualquier puerto asignado por el ambiente
EXPOSE $PORT

# Comando para ejecutar la aplicación de Streamlit utilizando la variable de entorno PORT
CMD ["sh", "-c", "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"]
