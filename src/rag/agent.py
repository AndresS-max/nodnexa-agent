"""Agente RAG de Nodnexa: recuperación + generación con fuentes citadas.

El agente responde únicamente con base en los documentos indexados.
Si la búsqueda no encuentra respaldo suficiente, lo admite explícitamente
en lugar de inventar una respuesta.
"""
from dataclasses import dataclass, field

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from src.config import CLAUDE_MODEL
from src.rag.retriever import ResultadoBusqueda, buscar, formatear_contexto
from src.rag.tools import HERRAMIENTAS

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
7. Si el usuario pide una COTIZACIÓN, un total, o combina varios servicios \
o meses de mantenimiento, usa SIEMPRE la herramienta `cotizar` — nunca sumes \
precios mentalmente. Presenta el desglose y aclara si hay precios "desde".

CONTEXTO:
{contexto}"""


@dataclass
class RespuestaAgente:
    respuesta: str
    fuentes: list[dict] = field(default_factory=list)
    uso_rag: bool = False
    uso_calculo: bool = False  # True si la respuesta usó la herramienta cotizar


class NodnexaAgent:
    def __init__(self, temperature: float = 0.2):
        self.llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            temperature=temperature,
            max_tokens=1024,
        ).bind_tools(HERRAMIENTAS)
        self._tools = {t.name: t for t in HERRAMIENTAS}

    def preguntar(self, pregunta: str,
                  historial: list[tuple[str, str]] | None = None,
                  categoria: str | None = None) -> RespuestaAgente:
        """Responde una pregunta usando RAG.

        historial: lista de pares (rol, texto) con rol "user" o "assistant",
        para mantener el hilo de la conversación dentro de la sesión.
        categoria: si se indica, la búsqueda se restringe a esa categoría.
        """
        resultados = buscar(pregunta, categoria=categoria)
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

        # Ciclo de herramientas: si Claude pide calcular, se ejecuta la tool
        # y se le devuelve el resultado para que redacte la respuesta final.
        uso_calculo = False
        for _ in range(3):  # tope de seguridad
            if not getattr(respuesta, "tool_calls", None):
                break
            mensajes.append(respuesta)
            for llamada in respuesta.tool_calls:
                salida = self._tools[llamada["name"]].invoke(llamada["args"])
                mensajes.append(ToolMessage(content=str(salida),
                                            tool_call_id=llamada["id"]))
                uso_calculo = True
            respuesta = self.llm.invoke(mensajes)

        texto = respuesta.content if isinstance(respuesta.content, str) else \
            " ".join(b.get("text", "") for b in respuesta.content
                     if isinstance(b, dict))
        return RespuestaAgente(
            respuesta=texto,
            fuentes=[_fuente(r) for r in resultados],
            uso_rag=True,
            uso_calculo=uso_calculo,
        )


def _fuente(r: ResultadoBusqueda) -> dict:
    m = r.documento.metadata
    return {
        "archivo": m["archivo"],
        "categoria": m["categoria"],
        "ubicacion": (m.get("pagina") or m.get("diapositiva")
                      or m.get("seccion") or m.get("fila") or ""),
        "score": round(r.score, 3),
        "extracto": r.documento.page_content[:180],
    }
