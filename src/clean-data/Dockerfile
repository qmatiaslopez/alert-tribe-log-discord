FROM python:3.12-slim

WORKDIR /app

# Crear directorio de logs
RUN mkdir -p /app/logs

# Copiar archivos de la aplicación
COPY requirements.txt .
COPY app/ .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Permisos para logs
RUN chmod 777 /app/logs

# Exponer puerto
EXPOSE 8000

# Ejecutar la API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]