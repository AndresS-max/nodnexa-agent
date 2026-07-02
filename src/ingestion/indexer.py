"""Indexación vectorial: embeddings (Voyage AI) + ChromaDB persistente."""
import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_voyageai import VoyageAIEmbeddings

from src.config import COLLECTION_NAME, VECTORSTORE_DIR, VOYAGE_MODEL


def get_embeddings() -> VoyageAIEmbeddings:
    return VoyageAIEmbeddings(model=VOYAGE_MODEL)


def get_vectorstore() -> Chroma:
    """Abre la base vectorial persistida (para consultas)."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(VECTORSTORE_DIR),
    )


def build_index(chunks: list[Document], reset: bool = True) -> Chroma:
    """Crea (o recrea) el índice vectorial a partir de los chunks.

    Pensado para ejecutarse offline (run_ingestion). Si el borrado del
    directorio falla porque otro proceso lo tiene abierto (Windows),
    se vacía la colección en su lugar.
    """
    if reset and VECTORSTORE_DIR.exists():
        try:
            shutil.rmtree(VECTORSTORE_DIR)
        except PermissionError:
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
