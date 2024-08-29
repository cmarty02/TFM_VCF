# Usa una imagen base de Python
FROM python:3.8-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY requirements.txt .
COPY train.py .
COPY random_forest_grid_search_best_setup.pkl .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que la app estará corriendo
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "train.py"]
