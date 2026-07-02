# Agente Nodnexa — imagen de producción
FROM python:3.12-slim

WORKDIR /app

# Dependencias primero (aprovecha la caché de capas de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código y base de conocimiento
COPY src/ src/
COPY data/documents/ data/documents/
COPY .streamlit/ .streamlit/

# El índice vectorial se construye al arrancar si no existe (ver docker-entrypoint.sh)
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
