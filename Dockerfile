# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.6
FROM python:${PYTHON_VERSION}-slim as base

# Evitar la escritura de archivos pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Desactivar el almacenamiento en búfer de la salida estándar y de error
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Crear un usuario no privilegiado
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copiar y actualizar el archivo requirements.txt
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-cache-dir -r requirements.txt

# Instalar Jupyter Notebook si no está en requirements.txt
RUN python -m pip install --no-cache-dir jupyter

# Cambiar al usuario no privilegiado
USER appuser

# Copiar el código fuente al contenedor
COPY . .

# Exponer el puerto para Jupyter Notebook
EXPOSE 8080

# Ejecutar Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8080", "--no-browser", "--allow-root"]
