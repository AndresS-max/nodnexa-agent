"""Registro de ejecución del agente (etapa de trazabilidad del proyecto).

Cada consulta se registra en formato JSON Lines con: pregunta, respuesta,
fuentes usadas, si se usó RAG, tiempo de respuesta y timestamp. Esto permite
auditar qué preguntó cada usuario, qué documento respaldó la respuesta y
detectar preguntas sin cobertura en la base de conocimiento.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import ROOT_DIR

LOGS_DIR = ROOT_DIR / "logs"
LOG_CONSULTAS = LOGS_DIR / "consultas.jsonl"
LOG_FEEDBACK = LOGS_DIR / "feedback.jsonl"


def _append(path: Path, registro: dict) -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    registro["timestamp"] = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def registrar_consulta(pregunta: str, respuesta: str, fuentes: list[dict],
                       uso_rag: bool, duracion_s: float) -> None:
    _append(LOG_CONSULTAS, {
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fuentes": [f["archivo"] for f in fuentes],
        "uso_rag": uso_rag,
        "duracion_s": round(duracion_s, 2),
    })


def registrar_feedback(pregunta: str, respuesta: str, positivo: bool) -> None:
    _append(LOG_FEEDBACK, {
        "pregunta": pregunta,
        "respuesta": respuesta[:300],
        "feedback": "positivo" if positivo else "negativo",
    })


class Cronometro:
    """Context manager simple para medir el tiempo de respuesta."""

    def __enter__(self):
        self._inicio = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.segundos = time.perf_counter() - self._inicio
