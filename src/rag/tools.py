"""Herramientas determinísticas del agente.

Los precios se CALCULAN con pandas sobre el CSV oficial — nunca se le pide
al LLM que haga aritmética "de cabeza" (ahí es donde alucinan los números).
"""
import unicodedata

import pandas as pd
from langchain_core.tools import tool

from src.config import DOCS_DIR

PRECIOS_CSV = DOCS_DIR / "precios_y_paquetes_nodnexa.csv"


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _precio_numerico(valor: str) -> tuple[float, bool]:
    """'desde 250' -> (250.0, True); '450' -> (450.0, False)."""
    texto = str(valor).strip().lower()
    es_desde = texto.startswith("desde")
    numero = float(texto.replace("desde", "").strip())
    return numero, es_desde


@tool
def cotizar(servicios: list[str], meses_mantenimiento: int = 0,
            plan_mantenimiento: str = "Pro") -> dict:
    """Calcula el precio EXACTO de una combinación de servicios de Nodnexa.

    Úsala siempre que el usuario pida una cotización, un total, o combine
    varios servicios/meses — no sumes precios mentalmente.

    Args:
        servicios: nombres de los servicios o paquetes a cotizar, tal como
            aparecen en el catálogo (ej. "Chatbot de atención al cliente
            (WhatsApp)", "Starter", "Automatización simple").
        meses_mantenimiento: meses de mantenimiento a incluir (0 = ninguno).
        plan_mantenimiento: "Básico" o "Pro".
    """
    df = pd.read_csv(PRECIOS_CSV)
    lineas, no_encontrados, subtotal, hay_desde = [], [], 0.0, False

    for pedido in servicios:
        buscado = _normalizar(pedido)
        matches = df[df["servicio"].map(
            lambda s: buscado in _normalizar(s) or _normalizar(s) in buscado)]
        if len(matches) == 0:
            no_encontrados.append(pedido)
            continue
        fila = matches.iloc[0]
        precio, es_desde = _precio_numerico(fila["precio_usd"])
        hay_desde = hay_desde or es_desde
        subtotal += precio
        lineas.append({
            "servicio": fila["servicio"],
            "precio_usd": precio,
            "es_precio_desde": es_desde,
            "plazo_entrega": fila["plazo_entrega"],
        })

    resultado = {"lineas": lineas, "subtotal_usd": subtotal}

    if meses_mantenimiento > 0:
        nombre = f"Mantenimiento {plan_mantenimiento}"
        fila = df[df["servicio"].map(
            lambda s: _normalizar(nombre) in _normalizar(s))]
        if len(fila) == 0:
            no_encontrados.append(nombre)
        else:
            mensual, _ = _precio_numerico(fila.iloc[0]["precio_usd"])
            costo = mensual * meses_mantenimiento
            resultado["mantenimiento"] = {
                "plan": fila.iloc[0]["servicio"],
                "mensual_usd": mensual,
                "meses": meses_mantenimiento,
                "total_usd": costo,
            }
            subtotal += costo

    resultado["total_usd"] = subtotal
    resultado["condiciones_pago"] = "50% de anticipo y 50% contra entrega"
    if hay_desde:
        resultado["nota"] = ("Incluye precios 'desde': el total es el punto de "
                             "partida y puede variar según el alcance final.")
    if no_encontrados:
        resultado["no_encontrados"] = no_encontrados
    return resultado


HERRAMIENTAS = [cotizar]
