"""Pruebas del pipeline de ingesta (extracción y chunking, sin APIs externas)."""
from src.config import CATEGORIA_POR_ARCHIVO, DOCS_DIR
from src.ingestion.chunker import chunk_documents
from src.ingestion.loaders import load_documents


def test_carga_todos_los_documentos():
    docs = load_documents(DOCS_DIR)
    archivos = {d.metadata["archivo"] for d in docs}
    assert archivos == set(CATEGORIA_POR_ARCHIVO), (
        f"Faltan documentos: {set(CATEGORIA_POR_ARCHIVO) - archivos}"
    )


def test_todos_los_docs_tienen_metadatos():
    for doc in load_documents(DOCS_DIR):
        assert doc.metadata["archivo"]
        assert doc.metadata["categoria"] != ""
        assert doc.metadata["formato"] in {"pdf", "csv", "markdown", "json"}
        assert doc.page_content.strip()


def test_chunking_hereda_metadatos():
    chunks = chunk_documents(load_documents(DOCS_DIR))
    assert len(chunks) > 0
    for chunk in chunks:
        assert "archivo" in chunk.metadata
        assert "chunk_id" in chunk.metadata
        assert len(chunk.page_content) <= 1200  # chunk_size + margen


def test_csv_convierte_filas_en_frases():
    docs = [d for d in load_documents(DOCS_DIR) if d.metadata["formato"] == "csv"]
    assert len(docs) == 14  # 14 filas de servicios en el CSV de precios
    assert all("precio_usd" in d.page_content for d in docs)
