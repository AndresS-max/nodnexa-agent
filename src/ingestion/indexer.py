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
    """Crea (o recrea) el índice vectorial a partir de los chunks."""
    if reset and VECTORSTORE_DIR.exists():
        shutil.rmtree(VECTORSTORE_DIR)
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTORSTORE_DIR),
    )
