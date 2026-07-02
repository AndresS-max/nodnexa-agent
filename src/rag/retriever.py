"""Capa de recuperación: búsqueda semántica sobre la base vectorial.

Convierte la pregunta en embedding (mismo modelo que la indexación),
busca los chunks más cercanos y aplica un umbral de relevancia para
que el agente pueda admitir cuando no hay información suficiente.
"""
from dataclasses import dataclass

from langchain_core.documents import Document

from src.config import TOP_K
from src.ingestion.indexer import get_vectorstore

# Umbral de relevancia (similitud coseno normalizada 0-1). Por debajo de esto,
# el fragmento no se considera respaldo suficiente para responder.
UMBRAL_RELEVANCIA = 0.35


@dataclass
class ResultadoBusqueda:
    documento: Document
    score: float


def buscar(pregunta: str, k: int = TOP_K,
           categoria: str | None = None) -> list[ResultadoBusqueda]:
    """Devuelve los k fragmentos más relevantes que superan el umbral."""
    vectorstore = get_vectorstore()
    filtro = {"categoria": categoria} if categoria else None
    resultados = vectorstore.similarity_search_with_relevance_scores(
        pregunta, k=k, filter=filtro,
    )
    return [
        ResultadoBusqueda(documento=doc, score=score)
        for doc, score in resultados
        if score >= UMBRAL_RELEVANCIA
    ]


def formatear_contexto(resultados: list[ResultadoBusqueda]) -> str:
    """Arma el bloque de contexto que se inserta en el prompt del LLM,
    con la referencia de origen de cada fragmento para poder citarla."""
    bloques = []
    for i, r in enumerate(resultados, start=1):
        m = r.documento.metadata
        ubicacion = (
            f"página {m['pagina']}" if "pagina" in m
            else f"sección '{m['seccion']}'" if "seccion" in m
            else f"fila {m['fila']}" if "fila" in m
            else ""
        )
        referencia = f"{m['archivo']}" + (f", {ubicacion}" if ubicacion else "")
        bloques.append(
            f"[Fragmento {i} — Fuente: {referencia} — Categoría: {m['categoria']}]\n"
            f"{r.documento.page_content}"
        )
    return "\n\n---\n\n".join(bloques)
