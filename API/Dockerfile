# Usa una imagen base de Python
FROM python:3.11-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de la API
COPY api.py .

# Exponer el puerto que usará la API
EXPOSE 8080

# Comando para ejecutar la API
CMD ["python", "api.py"]
