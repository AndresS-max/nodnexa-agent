"""Chat por terminal con el agente Nodnexa (útil para pruebas y demos rápidas).

Uso:
    python -m src.rag.cli
"""
from src.rag.agent import NodnexaAgent


def main() -> None:
    print("🤖 Agente Nodnexa — escribe tu pregunta (o 'salir' para terminar)\n")
    agente = NodnexaAgent()
    historial: list[tuple[str, str]] = []

    while True:
        try:
            pregunta = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pregunta or pregunta.lower() in {"salir", "exit", "quit"}:
            break

        resultado = agente.preguntar(pregunta, historial)
        print(f"\nNodnexa: {resultado.respuesta}\n")
        if resultado.fuentes:
            archivos = {f"{f['archivo']}" for f in resultado.fuentes}
            print(f"   (fuentes consultadas: {', '.join(sorted(archivos))})\n")

        historial.append(("user", pregunta))
        historial.append(("assistant", resultado.respuesta))

    print("\n👋 Hasta pronto")


if __name__ == "__main__":
    main()
