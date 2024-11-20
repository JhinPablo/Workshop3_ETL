# Usa una imagen base de Python
FROM python:3.12-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script del producer al contenedor
COPY . .
COPY data/ ./data/

# Ejecuta el script del producer
CMD ["python", "producer.py"]
