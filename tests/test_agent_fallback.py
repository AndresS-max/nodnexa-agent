"""Prueba del fallback honesto del agente — sin APIs externas.

Si la búsqueda no supera el umbral de relevancia, el agente debe responder
el mensaje de "no encontré" SIN llamar al LLM (ahorro de tokens y latencia).
"""
from src.rag import agent as agent_mod


def test_sin_resultados_responde_fallback_sin_llamar_al_llm(monkeypatch):
    # Búsqueda vacía simulada (nada supera el umbral)
    monkeypatch.setattr(agent_mod, "buscar", lambda *a, **k: [])

    # Instancia sin __init__: si el flujo tocara self.llm, explotaría —
    # lo cual es exactamente lo que queremos verificar que NO pasa.
    agente = agent_mod.NodnexaAgent.__new__(agent_mod.NodnexaAgent)
    r = agent_mod.NodnexaAgent.preguntar(agente, "¿dónde queda la oficina de Quito?")

    assert r.uso_rag is False
    assert r.uso_calculo is False
    assert "No encontré esta información" in r.respuesta
    assert r.fuentes == []


def test_busqueda_acepta_filtro_de_categoria(monkeypatch):
    """El parámetro categoria debe llegar hasta la búsqueda."""
    capturado = {}

    def falso_buscar(pregunta, categoria=None):
        capturado["categoria"] = categoria
        return []

    monkeypatch.setattr(agent_mod, "buscar", falso_buscar)
    agente = agent_mod.NodnexaAgent.__new__(agent_mod.NodnexaAgent)
    agent_mod.NodnexaAgent.preguntar(agente, "algo", categoria="Legal")
    assert capturado["categoria"] == "Legal"
