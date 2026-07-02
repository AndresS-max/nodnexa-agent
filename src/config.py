"""Configuración central del proyecto Nodnexa Agent."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Rutas
ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "data" / "documents"
VECTORSTORE_DIR = ROOT_DIR / "data" / "vectorstore"

# Modelos (ajustables por variable de entorno sin tocar código)
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")
VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-3.5-lite")

# Parámetros de chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Parámetros de recuperación
TOP_K = 5

# Colección de la base vectorial
COLLECTION_NAME = "nodnexa_docs"

# Categorías de negocio por documento (metadato para filtrar y citar fuentes)
CATEGORIA_POR_ARCHIVO = {
    "catalogo_servicios_nodnexa.pdf": "Comercial",
    "precios_y_paquetes_nodnexa.csv": "Comercial",
    "casos_de_uso_por_industria.json": "Comercial",
    "faq_nodnexa.md": "Atención al cliente",
    "proceso_de_trabajo_nodnexa.pdf": "Operacional",
    "terminos_y_condiciones_nodnexa.pdf": "Legal",
    "sop_soporte_interno_nodnexa.md": "Interno",
}
