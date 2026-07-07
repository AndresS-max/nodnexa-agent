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

# Embeddings: "local" (HuggingFace, sin límites ni costo) o "voyage" (API externa)
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", "local")
LOCAL_EMBEDDINGS_MODEL = os.getenv("LOCAL_EMBEDDINGS_MODEL", "intfloat/multilingual-e5-small")
VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-3.5-lite")

# Parámetros de chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Parámetros de recuperación
TOP_K = 5
# Umbral de relevancia para el fallback "no encontré": cada modelo de
# embeddings tiene su propia escala de scores (calibrado empíricamente:
# e5 puntúa irrelevantes ~0.70-0.76 y relevantes ~0.81+; Voyage mucho más bajo)
UMBRAL_RELEVANCIA = float(os.getenv(
    "UMBRAL_RELEVANCIA",
    "0.78" if os.getenv("EMBEDDINGS_PROVIDER", "local") == "local" else "0.35",
))

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
