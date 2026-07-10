"""Interfaz de chat del Agente Nodnexa (Streamlit).

Uso:
    streamlit run src/ui/app.py
"""
import sys
from pathlib import Path

# Permite ejecutar `streamlit run src/ui/app.py` desde la raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from src.config import DOCS_DIR
from src.ingestion.chunker import chunk_documents
from src.ingestion.indexer import add_file_to_index
from src.ingestion.loaders import LOADERS
from src.rag.agent import NodnexaAgent
from src.rag.logger import Cronometro, registrar_consulta, registrar_feedback

# ------------------------------------------------------------------ Estilo
ACCENT = "#0EA5A4"
INK = "#0F172A"

st.set_page_config(
    page_title="Nodnexa · Asistente corporativo",
    page_icon="🤖",
    layout="centered",
)

st.markdown(f"""
<style>
    .stApp {{ background: linear-gradient(180deg, #F8FAFC 0%, #EEF6F6 100%); }}
    h1 {{ color: {INK}; }}
    .nodnexa-badge {{
        display: inline-block; background: {ACCENT}; color: white;
        padding: 2px 12px; border-radius: 999px; font-size: 0.8rem;
        font-weight: 600; letter-spacing: 0.5px;
    }}
    .nodnexa-disclaimer {{
        color: #64748B; font-size: 0.82rem; margin-top: -6px;
    }}
    [data-testid="stChatMessage"] {{
        border-radius: 14px; border: 1px solid #E2E8F0;
        background: white; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }}
    [data-testid="stSidebar"] {{ background: {INK}; }}
    [data-testid="stSidebar"] * {{ color: #E2E8F0; }}
    [data-testid="stSidebar"] code {{
        background: rgba(255, 255, 255, 0.10) !important;
        color: #5EEAD4 !important;
        padding: 1px 6px; border-radius: 6px; font-size: 0.78rem;
    }}
    /* Oculta el menú de desarrollador de Streamlit (tema, imprimir, etc.) */
    [data-testid="stToolbar"], #MainMenu, footer {{ display: none !important; }}
    /* Zona de carga de archivos legible sobre la barra lateral oscura */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1.5px dashed rgba(94, 234, 212, 0.45) !important;
        border-radius: 12px;
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {{
        color: #CBD5E1 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {{
        background: {ACCENT} !important; color: white !important;
        border: none !important; border-radius: 8px !important;
    }}
    /* Selector de categoría legible sobre la barra lateral oscura */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(94, 234, 212, 0.45) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="select"] div[value] {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        fill: #5EEAD4 !important;
    }}
    .stButton > button {{ border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ Estado
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "agente" not in st.session_state:
    st.session_state.agente = NodnexaAgent()

# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    st.markdown("## ⚡ Nodnexa")
    st.caption("Agencia de automatizaciones con IA")
    st.divider()

    st.markdown("### 📚 Base de conocimiento")
    formatos = tuple(ext.lstrip(".") for ext in LOADERS)
    archivos = sorted(p.name for p in DOCS_DIR.iterdir()
                      if p.suffix.lower() in LOADERS and not p.name.startswith("_"))
    for a in archivos:
        st.markdown(f"- `{a}`")

    st.divider()
    st.markdown("### 🔎 Filtrar búsqueda")

    @st.cache_data(ttl=600, show_spinner=False)
    def _categorias_indexadas() -> list[str]:
        """Categorías presentes en el índice (cacheado: leerlas en cada
        interacción hacía lenta la app en servidores pequeños)."""
        from src.ingestion.indexer import get_vectorstore
        try:
            metas = get_vectorstore().get(include=["metadatas"])["metadatas"]
            return sorted({m["categoria"] for m in metas if m.get("categoria")})
        except Exception:
            return []

    filtro_categoria = st.selectbox(
        "Categoría", ["Todas"] + _categorias_indexadas(),
        help="Restringe las respuestas a los documentos de una categoría.",
    )

    st.divider()
    st.markdown("### ⬆️ Actualizar documentos")
    subida = st.file_uploader(
        "Agrega un documento nuevo", type=list(formatos),
        help="El documento se suma a la base y el índice se reconstruye.",
    )
    if subida is not None and st.session_state.get("ultimo_indexado") != subida.name:
        destino = DOCS_DIR / subida.name
        destino.write_bytes(subida.getvalue())
        loader = LOADERS[destino.suffix.lower()]
        with st.spinner(f"Indexando '{subida.name}'…"):
            chunks = chunk_documents(loader(destino))
            add_file_to_index(chunks, subida.name)
        st.session_state.ultimo_indexado = subida.name
        st.success(f"'{subida.name}' agregado a la base ({len(chunks)} fragmentos) ✅")

    st.divider()
    if st.button("🗑️ Limpiar conversación", width="stretch"):
        st.session_state.mensajes = []
        st.rerun()

# ------------------------------------------------------------------ Cabecera
st.markdown('<span class="nodnexa-badge">ASISTENTE IA</span>', unsafe_allow_html=True)
st.title("Asistente corporativo de Nodnexa")
st.markdown(
    '<p class="nodnexa-disclaimer">🤖 Estás conversando con un agente de '
    'inteligencia artificial. Responde con base en los documentos oficiales '
    'de Nodnexa y cita sus fuentes.</p>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ Historial
for i, msg in enumerate(st.session_state.mensajes):
    with st.chat_message(msg["rol"], avatar="⚡" if msg["rol"] == "assistant" else None):
        if msg.get("uso_calculo"):
            st.caption("🧮 Cotización con cálculo exacto sobre la tabla oficial de precios")
        st.markdown(msg["texto"])
        if msg["rol"] == "assistant" and msg.get("fuentes"):
            with st.expander("📄 Fuentes consultadas"):
                for f in msg["fuentes"]:
                    ubic = f" · {f['ubicacion']}" if f["ubicacion"] else ""
                    st.markdown(
                        f"**{f['archivo']}**{ubic} · _{f['categoria']}_ "
                        f"(relevancia {f['score']:.0%})\n\n> {f['extracto']}…"
                    )
        if msg["rol"] == "assistant":
            c1, c2, _ = st.columns([1, 1, 8])
            pregunta_previa = st.session_state.mensajes[i - 1]["texto"] if i else ""
            if c1.button("👍", key=f"up_{i}"):
                registrar_feedback(pregunta_previa, msg["texto"], positivo=True)
                st.toast("¡Gracias por tu feedback!")
            if c2.button("👎", key=f"down_{i}"):
                registrar_feedback(pregunta_previa, msg["texto"], positivo=False)
                st.toast("Gracias, lo usaremos para mejorar.")

# ------------------------------------------------------------------ Entrada
if pregunta := st.chat_input("Pregunta sobre servicios, precios, soporte, políticas…"):
    st.session_state.mensajes.append({"rol": "user", "texto": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    historial = [(m["rol"].replace("assistant", "assistant").replace("user", "user"),
                  m["texto"]) for m in st.session_state.mensajes[:-1]]

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Buscando en los documentos de Nodnexa…"):
            with Cronometro() as t:
                resultado = st.session_state.agente.preguntar(
                    pregunta, historial,
                    categoria=None if filtro_categoria == "Todas" else filtro_categoria,
                )
        if resultado.uso_calculo:
            st.caption("🧮 Cotización con cálculo exacto sobre la tabla oficial de precios")
        st.markdown(resultado.respuesta)

    registrar_consulta(pregunta, resultado.respuesta, resultado.fuentes,
                       resultado.uso_rag, t.segundos)
    st.session_state.mensajes.append({
        "rol": "assistant",
        "texto": resultado.respuesta,
        "fuentes": resultado.fuentes,
        "uso_calculo": resultado.uso_calculo,
    })
    st.rerun()
