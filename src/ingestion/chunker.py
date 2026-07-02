"""División del texto en fragmentos (chunks) con solapamiento.

Los chunks heredan los metadatos de su documento de origen, de modo que
cada fragmento indexado sabe de qué archivo, categoría y página/sección viene.
"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_documents(documentos: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documentos)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
    return chunks
