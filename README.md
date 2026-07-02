# 🤖 Nodnexa — Agente de Conocimiento Corporativo con IA

> Challenge Alura Agente — ONE (Oracle Next Education) · IA for Tech

**Nodnexa** es una agencia de automatizaciones con IA. Este proyecto es su **agente de conocimiento corporativo**: un asistente conversacional capaz de responder preguntas en lenguaje natural sobre la documentación interna de la empresa —servicios, precios, procesos, políticas y FAQ— citando siempre la fuente y admitiendo cuando no encuentra la respuesta en los documentos.

## 🚧 Estado del proyecto

**En desarrollo activo.** Roadmap:

- [x] Definición del escenario y stack tecnológico
- [x] Estructura del proyecto y repositorio
- [ ] Documentación corporativa (base de conocimiento)
- [ ] Pipeline de ingesta: extracción, chunking e indexación vectorial
- [ ] Agente RAG: recuperación semántica + generación de respuestas con citas
- [ ] Interfaz de chat web
- [ ] Deploy en Oracle Cloud Infrastructure (OCI)
- [ ] Evidencia de ejecución en la nube

## 🏗️ Arquitectura (resumen)

```
Documentos (PDF/CSV/MD) → Extracción y limpieza → Chunking con overlap
    → Embeddings (Voyage AI) → Base vectorial (ChromaDB)
                                      ↓
Pregunta del usuario → Búsqueda semántica → Contexto relevante
    → Claude (Anthropic) → Respuesta con fuentes citadas
```

## 🛠️ Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Orquestación RAG | LangChain |
| LLM (generación) | Claude (Anthropic API) |
| Embeddings | Voyage AI |
| Base vectorial | ChromaDB |
| Interfaz | Streamlit |
| Nube | Oracle Cloud Infrastructure (OCI) |

## 📁 Estructura del repositorio

```
├── data/
│   └── documents/      # Base de conocimiento (documentos de la empresa)
├── docs/               # Diagramas de arquitectura y capturas
├── src/
│   ├── ingestion/      # Extracción, chunking e indexación
│   ├── rag/            # Recuperación y generación de respuestas
│   └── ui/             # Interfaz de chat (Streamlit)
├── tests/              # Pruebas
├── .env.example        # Plantilla de variables de entorno
└── requirements.txt    # Dependencias
```

## ⚙️ Instalación (preliminar)

```bash
git clone https://github.com/AndresS-max/nodnexa-agent.git
cd nodnexa-agent
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # y completa tus API keys
```

*Las instrucciones completas de ejecución se documentarán al finalizar el desarrollo.*

---

📌 Proyecto desarrollado para el **Challenge Alura Agente** del programa **ONE — Oracle Next Education** (Alura Latam + Oracle).
