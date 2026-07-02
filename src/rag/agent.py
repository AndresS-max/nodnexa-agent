"""Agente RAG de Nodnexa: recuperación + generación con fuentes citadas.

El agente responde únicamente con base en los documentos indexados.
Si la búsqueda no encuentra respaldo suficiente, lo admite explícitamente
en lugar de inventar una respuesta.
"""
from dataclasses import dataclass, field

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.config import CLAUDE_MODEL
from src.rag.retriever import ResultadoBusqueda, buscar, formatear_contexto

MENSAJE_SIN_RESPUESTA = (
    "No encontré esta información en los documentos disponibles de Nodnexa. "
    "Te sugiero escribir a hola@nodnexa.com para consultas comerciales o a "
    "soporte@nodnexa.com si eres cliente."
)

PROMPT_SISTEMA = """Eres el asistente virtual oficial de Nodnexa, una agencia de \
automatizaciones con inteligencia artificial para pymes de Latinoamérica. \
Atiendes tanto a clientes y prospectos como a colaboradores internos.

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con la información del CONTEXTO proporcionado. No uses \
conocimiento externo ni inventes datos, precios, plazos o políticas.
2. Cita siempre la fuente de tu respuesta al final, en el formato: \
📄 Fuente: <archivo> (<página/sección/fila si aplica>).
3. Si el contexto no contiene la información necesaria para responder, dilo \
claramente con este mensaje: "{sin_respuesta}"
4. Responde en español, de forma clara y directa: primero la respuesta, \
luego el detalle si aporta valor, al final la(s) fuente(s).
5. Si la pregunta involucra decisiones críticas (legales, financieras), \
recuerda amablemente que un humano del equipo puede confirmar los detalles.
6. Eres un asistente de IA y no debes hacerte pasar por una persona.

CONTEXTO:
{contexto}"""


@dataclass
class RespuestaAgente:
    respuesta: str
    fuentes: list[dict] = field(default_factory=list)
    uso_rag: bool = False


class NodnexaAgent:
    def __init__(self, temperature: float = 0.2):
        self.llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            temperature=temperature,
            max_tokens=1024,
        )

    def preguntar(self, pregunta: str,
                  historial: list[tuple[str, str]] | None = None) -> RespuestaAgente:
        """Responde una pregunta usando RAG.

        historial: lista de pares (rol, texto) con rol "user" o "assistant",
        para mantener el hilo de la conversación dentro de la sesión.
        """
        resultados = buscar(pregunta)
        if not resultados:
            return RespuestaAgente(respuesta=MENSAJE_SIN_RESPUESTA, uso_rag=False)

        contexto = formatear_contexto(resultados)
        mensajes = [SystemMessage(content=PROMPT_SISTEMA.format(
            contexto=contexto, sin_respuesta=MENSAJE_SIN_RESPUESTA))]
        for rol, texto in (historial or [])[-6:]:  # últimas 3 idas y vueltas
            cls = HumanMessage if rol == "user" else AIMessage
            mensajes.append(cls(content=texto))
        mensajes.append(HumanMessage(content=pregunta))

        respuesta = self.llm.invoke(mensajes)
        return RespuestaAgente(
            respuesta=respuesta.content,
            fuentes=[_fuente(r) for r in resultados],
            uso_rag=True,
        )


def _fuente(r: ResultadoBusqueda) -> dict:
    m = r.documento.metadata
    return {
        "archivo": m["archivo"],
        "categoria": m["categoria"],
        "ubicacion": m.get("pagina") or m.get("seccion") or m.get("fila") or "",
        "score": round(r.score, 3),
        "extracto": r.documento.page_content[:180],
    }
