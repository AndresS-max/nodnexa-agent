"""Pipeline de ingesta completo: extracción -> limpieza -> chunking -> indexación.

Uso:
    python -m src.ingestion.run_ingestion
"""
from collections import Counter

from src.config import DOCS_DIR
from src.ingestion.chunker import chunk_documents
from src.ingestion.indexer import build_index
from src.ingestion.loaders import load_documents


def main() -> None:
    print(f"📂 Leyendo documentos de: {DOCS_DIR}")
    documentos = load_documents(DOCS_DIR)
    por_archivo = Counter(d.metadata["archivo"] for d in documentos)
    for archivo, n in por_archivo.items():
        print(f"   · {archivo}: {n} secciones/páginas/filas")

    chunks = chunk_documents(documentos)
    print(f"✂️  {len(documentos)} documentos -> {len(chunks)} chunks")

    print("🧮 Generando embeddings (Voyage AI) e indexando en ChromaDB...")
    build_index(chunks)
    print("✅ Índice vectorial creado en data/vectorstore/")


if __name__ == "__main__":
    main()
