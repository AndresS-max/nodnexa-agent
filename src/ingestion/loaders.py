"""Extracción de contenido por formato (etapa 2 del pipeline RAG).

Cada loader devuelve una lista de Documents de LangChain con el texto limpio
y metadatos: archivo de origen, categoría de negocio, formato y ubicación
(página/fila/sección) para poder citar fuentes en las respuestas.
"""
import json
import re
from pathlib import Path

import pandas as pd
from langchain_core.documents import Document
from pypdf import PdfReader

from src.config import CATEGORIA_POR_ARCHIVO


def _limpiar(texto: str) -> str:
    """Elimina ruido común de extracción: espacios duplicados y líneas vacías."""
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def _meta(path: Path, formato: str, **extra) -> dict:
    return {
        "archivo": path.name,
        "categoria": CATEGORIA_POR_ARCHIVO.get(path.name, "General"),
        "formato": formato,
        **extra,
    }


def load_pdf(path: Path) -> list[Document]:
    """Un Document por página, para citar 'archivo, página N'."""
    docs = []
    reader = PdfReader(str(path))
    for num, page in enumerate(reader.pages, start=1):
        texto = _limpiar(page.extract_text() or "")
        if texto:
            docs.append(Document(page_content=texto,
                                 metadata=_meta(path, "pdf", pagina=num)))
    return docs


def load_csv(path: Path) -> list[Document]:
    """Cada fila se convierte en una frase legible con sus encabezados,
    porque las tablas pierden el sentido si se tratan como texto corrido."""
    df = pd.read_csv(path)
    docs = []
    for idx, row in df.iterrows():
        partes = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
        texto = ". ".join(str(p) for p in partes)
        docs.append(Document(page_content=texto,
                             metadata=_meta(path, "csv", fila=int(idx) + 2)))
    return docs


def load_markdown(path: Path) -> list[Document]:
    """Divide por secciones (##) para preservar la estructura lógica."""
    contenido = path.read_text(encoding="utf-8")
    secciones = re.split(r"\n(?=## )", contenido)
    docs = []
    for seccion in secciones:
        texto = _limpiar(seccion)
        if not texto:
            continue
        titulo = texto.splitlines()[0].lstrip("# ").strip()
        docs.append(Document(page_content=texto,
                             metadata=_meta(path, "markdown", seccion=titulo)))
    return docs


def load_json(path: Path) -> list[Document]:
    """Convierte cada caso de uso en un párrafo comprensible."""
    data = json.loads(path.read_text(encoding="utf-8"))
    docs = []
    for caso in data.get("casos_de_uso", []):
        texto = (
            f"Industria: {caso['industria']}.\n"
            f"Problemas típicos: {'; '.join(caso['problemas_tipicos'])}.\n"
            f"Solución de Nodnexa: {caso['solucion_nodnexa']}.\n"
            f"Servicios relacionados: {', '.join(caso['servicios_relacionados'])}.\n"
            f"Resultado esperado: {caso['resultado_esperado']}."
        )
        docs.append(Document(page_content=texto,
                             metadata=_meta(path, "json", seccion=caso["industria"])))
    return docs


LOADERS = {
    ".pdf": load_pdf,
    ".csv": load_csv,
    ".md": load_markdown,
    ".json": load_json,
}


def load_documents(docs_dir: Path) -> list[Document]:
    """Carga todos los documentos soportados de la carpeta."""
    documentos = []
    for path in sorted(docs_dir.iterdir()):
        loader = LOADERS.get(path.suffix.lower())
        if loader:
            documentos.extend(loader(path))
    return documentos
