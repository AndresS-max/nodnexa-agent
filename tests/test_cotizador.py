"""Pruebas de la herramienta de cotización (cálculo determinístico, sin LLM)."""
from src.rag.tools import cotizar


def _run(**kwargs):
    return cotizar.invoke(kwargs)


def test_whatsapp_mas_6_meses_mantenimiento_pro():
    r = _run(servicios=["Chatbot de atención al cliente (WhatsApp)"],
             meses_mantenimiento=6, plan_mantenimiento="Pro")
    assert r["lineas"][0]["precio_usd"] == 1000
    assert r["mantenimiento"]["total_usd"] == 6 * 150
    assert r["total_usd"] == 1000 + 900
    assert r["nota"]  # el chatbot es precio "desde"


def test_paquete_starter_sin_mantenimiento():
    r = _run(servicios=["Starter"])
    assert r["total_usd"] == 450
    assert "mantenimiento" not in r
    assert "nota" not in r  # Starter es precio cerrado, sin "desde"


def test_combinacion_y_busqueda_flexible():
    # nombres aproximados y sin tildes deben resolver igual
    r = _run(servicios=["automatizacion simple", "consultoría de automatización por hora"])
    assert r["total_usd"] == 250 + 45
    assert len(r["lineas"]) == 2


def test_servicio_inexistente_se_reporta():
    r = _run(servicios=["desarrollo de videojuegos"])
    assert r["no_encontrados"] == ["desarrollo de videojuegos"]
    assert r["total_usd"] == 0
