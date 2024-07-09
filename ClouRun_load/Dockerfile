# Usa una imagen base de Python
FROM python:3.8-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos y la aplicación
COPY requirements.txt .
COPY load.py .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "load.py"]
