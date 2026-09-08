import streamlit as st
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# --- CONFIGURACIÓN DE PÁGINA Y METADATOS ---
st.set_page_config(
    page_title="Atom Studio Search",
    page_icon="🎨",
    layout="centered"
)

st.markdown("""
    <head>
        <meta property="og:title" content="Atom Studio Search" />
        <meta property="og:description" content="Buscador inteligente de materiales y recursos creativos diseñados por Atom Studio para todas las áreas." />
    </head>
""", unsafe_allow_html=True)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 1. FONDO AMBIENTAL SUBTIL */
    .stApp {
        background: radial-gradient(circle at 15% 20%, #F5F3FF 0%, transparent 45%),
                    radial-gradient(circle at 85% 30%, #EFF6FF 0%, transparent 45%),
                    radial-gradient(circle at 50% 85%, #F1FDF4 0%, transparent 50%),
                    #fafafa !important;
        background-attachment: fixed !important;
    }

    /* 2. TARJETA GLASSMORPHISM TRANSLÚCIDA */
    [data-testid="stMainBlockContainer"] {
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
        border-radius: 32px !important;
        border: 1px solid rgba(255, 255, 255, 0.85) !important;
        box-shadow: 0 20px 60px rgba(128, 35, 255, 0.07), 0 4px 20px rgba(0, 0, 0, 0.02) !important;
        padding: 45px 40px !important;
        margin-top: 5rem !important;
        margin-bottom: 4rem !important;
        max-width: 820px !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* 3. ANIMACIÓN DE ESFERA 3D ROTATIVA */
    .ai-orb-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1.5rem;
        perspective: 800px;
    }

    .ai-orb {
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ff6600 10%, #8023ff 70%, #4338ca 100%);
        box-shadow: 0 0 22px rgba(128, 35, 255, 0.45), 0 0 38px rgba(255, 102, 0, 0.35);
        animation: spinOrb 6s infinite linear, pulseDepth 3s infinite ease-in-out;
        transform-style: preserve-3d;
    }

    @keyframes spinOrb {
        0% { transform: rotate3d(1, 1, 0, 0deg); }
        50% { transform: rotate3d(1, 1, 1, 180deg); }
        100% { transform: rotate3d(1, 1, 0, 360deg); }
    }

    @keyframes pulseDepth {
        0%, 100% { transform: scale(0.96); opacity: 0.9; }
        50% { transform: scale(1.06); opacity: 1; }
    }

    /* 4. TÍTULOS Y SUBTÍTULO */
    .title-container {
        text-align: center;
        margin-bottom: 2rem;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }

    .highlight-search {
        color: #ff6600;
    }

    .subtitle-text {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 400;
    }

    /* 5. CAJA DE BÚSQUEDA CON BORDE DEGRADE Y RESPLANDOR */
    .stTextInput > div {
        border-radius: 28px !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    .stTextInput div[data-baseweb="input"],
    .stTextInput div[data-baseweb="base-input"] {
        border-radius: 28px !important;
        background-color: #ffffff !important;
        border: 2px solid transparent !important;
        background-image: linear-gradient(#ffffff, #ffffff), linear-gradient(135deg, #ff6600 0%, #8023ff 100%) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        box-shadow: 0 4px 20px rgba(128, 35, 255, 0.12), 0 2px 8px rgba(255, 102, 0, 0.12) !important;
        transition: all 0.3s ease !important;
    }

    /* Efecto al hacer clic para escribir (alumbra más el degradado) */
    .stTextInput div[data-baseweb="input"]:focus-within,
    .stTextInput div[data-baseweb="base-input"]:focus-within {
        box-shadow: 0 6px 25px rgba(255, 102, 0, 0.25), 0 2px 12px rgba(128, 35, 255, 0.3) !important;
        transform: translateY(-1px);
    }

    .stTextInput input {
        border-radius: 28px !important;
        padding: 14px 22px !important;
        font-size: 16px !important;
        color: #0f172a !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        font-family: 'Inter', sans-serif !important;
        background: transparent !important;
    }

    /* 6. BOTÓN CTA CENTRADO */
    div.element-container:has(button) {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    .stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    .stButton > button {
        border-radius: 18px !important;
        background: linear-gradient(135deg, #ff6600 0%, #8023ff 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: none !important;
        max-width: 220px !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block !important;
        transition: opacity 0.2s ease;
    }

    .stButton > button:hover {
        opacity: 0.92;
        box-shadow: none !important;
    }

    /* 7. TARJETAS DE RESULTADOS */
    .asset-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(226, 232, 240, 0.85);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.02);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .asset-title {
        font-weight: 600;
        color: #0f172a;
        font-size: 15px;
    }

    .asset-link {
        color: #8023ff;
        text-decoration: none;
        font-weight: 600;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Configurar Gemini con el SDK oficial
try:
    gemini_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Error al inicializar la API de Gemini: {e}")

# 2. Configurar Drive desde secretos
@st.cache_resource
def conectar_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

try:
    drive_service = conectar_drive()
except Exception as e:
    st.error(f"Error al conectar con Drive: {e}")

# --- CONTENIDO DE LA APP ---

# Esfera 3D giratoria
st.markdown("""
    <div class="ai-orb-container">
        <div class="ai-orb"></div>
    </div>
""", unsafe_allow_html=True)

# Título, Subtítulo y Nota de Acceso
st.markdown("""
    <div class="title-container">
        <h1 class="main-title">Atom Studio <span class="highlight-search">Search</span></h1>
        <p class="subtitle-text">Escribe qué necesitas encontrar (ej. 'gif financiera remarketing', 'logo blanco', 'fotos navidad')</p>
        <div style="
            background: rgba(248, 250, 252, 0.85);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 8px 16px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        ">
            <span style="font-size: 0.9rem;">🔒</span>
            <span style="color: #475569; font-size: 0.83rem; font-weight: 500;">
                Recuerda iniciar sesión en Google con tu correo <strong>@atomchat.io</strong> para abrir los archivos.
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Caja de búsqueda a ancho completo
query_usuario = st.text_input("", placeholder="🔍 Escribe tu búsqueda aquí...", label_visibility="collapsed")

# Botón CTA Centrado
st.markdown("<br>", unsafe_allow_html=True)
buscar_clicked = st.button("🔎 Buscar Materiales")

# PIE DE PÁGINA (DENTRO DEL TARJETÓN BLANCO)
st.markdown("""
    <div style="
        margin-top: 35px;
        padding-top: 18px;
        border-top: 1px solid rgba(226, 232, 240, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
    ">
        <a href="https://atomchat.io" target="_blank" style="display: flex; align-items: center; text-decoration: none;">
            <img src="https://raw.githubusercontent.com/atomnatalie/atom-studio-buscador/main/logo.png" alt="ATOM Logo" style="height: 24px; width: auto; object-fit: contain;">
        </a>
        <div style="height: 16px; width: 1px; background-color: #cbd5e1;"></div>
        <div style="display: flex; align-items: center; gap: 14px;">
            <a href="https://www.instagram.com/atom_chat/" target="_blank" style="color: #64748b; text-decoration: none; display: flex; align-items: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            </a>
            <a href="https://www.linkedin.com/company/atomchat/" target="_blank" style="color: #64748b; text-decoration: none; display: flex; align-items: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            </a>
            <a href="https://www.youtube.com/channel/UCvVlbyMlf5X_h-HvjoC14nA" target="_blank" style="color: #64748b; text-decoration: none; display: flex; align-items: center;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/></svg>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Lógica y Resultados
if buscar_clicked:
    if query_usuario:
        with st.spinner("⚡ Buscando assets..."):
            prompt = f"""
            Extrae las palabras clave para buscar archivos en Google Drive a partir del texto: '{query_usuario}'.
            Devuelve ÚNICAMENTE las palabras clave separadas por comas.
            Ejemplo: 'gif,financiera,remarketing'
            """
            
            try:
                respuesta_gemini = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                palabras_raw = respuesta_gemini.text.strip()
                palabras_clave = [p.strip() for p in palabras_raw.split(',') if p.strip()]
            except Exception:
                palabras_clave = query_usuario.split()

            if not palabras_clave:
                palabras_clave = query_usuario.split()

            # Búsqueda AND en Drive
            condiciones_drive = [f"name contains '{p}'" for p in palabras_clave]
            query_drive = " and ".join(condiciones_drive) + " and trashed = false"
            
            try:
                resultados = drive_service.files().list(
                    q=query_drive,
                    spaces='drive',
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    fields='files(id, name, webViewLink)',
                    pageSize=15
                ).execute()
                
                archivos = resultados.get('files', [])
                
                # Búsqueda flexible OR si falla la primera
                if not archivos and len(palabras_clave) > 1:
                    query_drive_flexible = f"({' or '.join(condiciones_drive)}) and trashed = false"
                    resultados = drive_service.files().list(
                        q=query_drive_flexible,
                        spaces='drive',
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                        fields='files(id, name, webViewLink)',
                        pageSize=15
                    ).execute()
                    archivos = resultados.get('files', [])

                st.markdown("<br>", unsafe_allow_html=True)

                if not archivos:
                    st.warning("No encontramos archivos que coincidan con esa descripción.")
                else:
                    st.success(f"¡Encontramos {len(archivos)} archivo(s)!")
                    for archivo in archivos:
                        st.markdown(f"""
                            <div class="asset-card">
                                <span class="asset-title">📄 {archivo['name']}</span>
                                <a class="asset-link" href="{archivo['webViewLink']}" target="_blank">Abrir / Descargar ↗</a>
                            </div>
                        """, unsafe_allow_html=True)
                            
            except Exception as e:
                st.error(f"Error al conectar con Drive: {e}")
    else:
        st.warning("Por favor, escribe algo para buscar.")
