"""Indexación vectorial: embeddings (locales o Voyage AI) + ChromaDB persistente.

Los imports pesados (Chroma, proveedores de embeddings) son perezosos: se
cargan al usarse, no al importar el módulo.
"""
from langchain_core.documents import Document

from src.config import (
    COLLECTION_NAME, EMBEDDINGS_PROVIDER, LOCAL_EMBEDDINGS_MODEL,
    VECTORSTORE_DIR, VOYAGE_MODEL,
)


def get_embeddings():
    """Proveedor de embeddings según configuración.

    - "local" (default): modelo multilingüe de HuggingFace ejecutado en la
      propia máquina — sin límites de peticiones, sin costo por consulta.
    - "voyage": API de Voyage AI (requiere VOYAGE_API_KEY).
    """
    if EMBEDDINGS_PROVIDER == "voyage":
        from langchain_voyageai import VoyageAIEmbeddings
        return VoyageAIEmbeddings(model=VOYAGE_MODEL)
    return _get_local_embeddings()


_local_cache = None


def _get_local_embeddings():
    """Modelo local cacheado (cargarlo toma segundos; se hace una sola vez).

    Los modelos e5 requieren prefijos distintos para documentos ("passage: ")
    y consultas ("query: ") — sin ellos la calidad de recuperación baja.
    """
    global _local_cache
    if _local_cache is None:
        from langchain_huggingface import HuggingFaceEmbeddings

        class E5Embeddings(HuggingFaceEmbeddings):
            def embed_documents(self, texts):
                return super().embed_documents([f"passage: {t}" for t in texts])

            def embed_query(self, text):
                return super().embed_query(f"query: {text}")

        _local_cache = E5Embeddings(
            model_name=LOCAL_EMBEDDINGS_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )
    return _local_cache


def get_vectorstore():
    """Abre la base vectorial persistida (para consultas)."""
    from langchain_chroma import Chroma
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(VECTORSTORE_DIR),
    )


def build_index(chunks: list[Document], reset: bool = True):
    """Crea (o recrea) el índice vectorial a partir de los chunks.

    El directorio nunca se elimina (puede ser un volumen montado en Docker
    o estar abierto por otro proceso en Windows): se vacía la colección.
    """
    from langchain_chroma import Chroma
    if reset and VECTORSTORE_DIR.exists() and any(VECTORSTORE_DIR.iterdir()):
        get_vectorstore().reset_collection()
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTORSTORE_DIR),
    )


def add_file_to_index(chunks: list[Document], archivo: str) -> None:
    """Indexación incremental: reemplaza los chunks de un archivo sin
    reconstruir el índice (seguro con la app corriendo).

    Si el archivo ya estaba indexado, sus chunks anteriores se eliminan
    para no duplicar resultados.
    """
    vectorstore = get_vectorstore()
    existentes = vectorstore.get(where={"archivo": archivo})
    if existentes["ids"]:
        vectorstore.delete(ids=existentes["ids"])
    vectorstore.add_documents(chunks)
