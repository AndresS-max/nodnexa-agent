#!/bin/sh
set -e

# Construye el índice vectorial en el primer arranque (persistido en volumen)
if [ ! -d "data/vectorstore" ] || [ -z "$(ls -A data/vectorstore 2>/dev/null)" ]; then
    echo ">> Índice vectorial no encontrado: ejecutando ingesta inicial..."
    python -m src.ingestion.run_ingestion
fi

exec python -m streamlit run src/ui/app.py \
    --server.port "${PORT:-8501}" \
    --server.address 0.0.0.0 \
    --server.headless true
