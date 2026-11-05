import os
from pypdf import PdfReader
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Documentos PDF", page_icon="💬", layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(
    """
    <style>
    .main { background-color: #0E1117; color: #F8FAFC; }
    .stSidebar { background-color: #161B22 !important; }
    .hero-title { color: #FFFFFF; font-weight: 800; font-size: 2.2rem; }
    .card-box {
        background-color: #161B22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363D;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white; font-weight: bold; border-radius: 8px; border: none;
        padding: 10px 20px; width: 100%;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.markdown("### ⚙️ Configuración")
st.sidebar.markdown(
    "<p style='color: #9CA3AF; font-size: 13px;'>Este agente analiza el contenido"
    " de tu PDF mediante modelos del lenguaje.</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

st.sidebar.markdown("**Clave API de OpenAI**")
openai_api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    placeholder="sk-...",
    label_visibility="collapsed",
)

if not openai_api_key:
  st.sidebar.markdown(
      "<div"
      ' style="background-color: #3B3A2A; padding: 10px; border-radius: 6px;'
      ' color: #FACC15; font-size: 13px; font-weight: bold;">🔑 Ingresa tu API'
      " Key para habilitar la app</div>",
      unsafe_allow_html=True,
  )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color: #9CA3AF; font-size: 12px;'>Python v3.10.22</p>",
    unsafe_allow_html=True,
)

# --- CONTENIDO PRINCIPAL ---
st.markdown(
    '<p class="hero-title">Analizador de Documentos PDF 💬</p>',
    unsafe_allow_html=True,
)
st.markdown(
    "Carga tu archivo, procesa el texto y realiza preguntas sobre su contenido"
    " en tiempo real."
)
st.markdown("---")

# Estructura de dos columnas (Carga de Documento / Estado del Documento)
col1, col2 = st.columns(2)

pdf_text = ""

with col1:
  st.markdown("### 1. Cargar Documento")
  uploaded_file = st.file_uploader(
      "Drag and drop file here\nLimit 200MB per file • PDF",
      type=["pdf"],
      label_visibility="collapsed",
  )

with col2:
  st.markdown("### 2. Estado del Documento")
  if uploaded_file is not None:
    try:
      reader = PdfReader(uploaded_file)
      for page in reader.pages:
        text = page.extract_text()
        if text:
          pdf_text += text + "\n"

      st.success(
          f"¡Documento cargado con éxito! ({len(reader.pages)} páginas"
          f" procesadas)."
      )
    except Exception as e:
      st.error(f"Error al leer el archivo PDF: {e}")
  else:
    st.markdown(
        '<div class="card-box" style="color: #94A3B8;">Esperando que cargues'
        " un archivo PDF para comenzar.</div>",
        unsafe_allow_html=True,
    )

# --- SECCIÓN DE PREGUNTAS Y CHAT EN TIEMPO REAL ---
if uploaded_file is not None and pdf_text.strip() != "":
  st.markdown("---")
  st.markdown("### 🤖 Chat en Tiempo Real con el PDF")

  user_question = st.text_input(
      "Realiza una pregunta sobre el contenido del documento:"
  )

  if user_question:
    if not openai_api_key:
      st.warning(
          "Por favor ingresa tu Clave API de OpenAI en la barra lateral para"
          " generar respuestas basadas en IA."
      )
    else:
      with st.spinner("Analizando documento y generando respuesta..."):
        try:
          from openai import OpenAI

          client = OpenAI(api_key=openai_api_key)

          # Prompt contextual con el texto del PDF
          prompt = (
              f"Basándote en el siguiente contenido extraído de un documento"
              f" PDF, responde de manera clara y precisa a la pregunta del"
              f" usuario.\n\nContenido del PDF:\n{pdf_text[:12000]}"
              f"\n\nPregunta: {user_question}"
          )

          response = client.chat.completions.create(
              model="gpt-3.5-turbo",
              messages=[
                  {
                      "role": "system",
                      "content": (
                          "Eres un asistente experto analizando documentos PDF."
                      ),
                  },
                  {"role": "user", "content": prompt},
              ],
          )

          answer = response.choices[0].message.content
          st.markdown("#### 💡 Respuesta del Asistente:")
          st.info(answer)

        except Exception as e:
          st.error(
              f"Ocurrió un error al conectar con la API de OpenAI: {e}"
          )
