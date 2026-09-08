import streamlit as st
st.set_page_config(
    page_title="Atom Studio Search",
    page_icon="🎨",
    layout="centered"
)

# Inyectar metadatos para la vista previa de Slack/WhatsApp
st.markdown("""
    <head>
        <meta property="og:title" content="Atom Studio Search" />
        <meta property="og:description" content="Buscador inteligente de materiales y recursos creativos diseñados por Atom Studio para todas las áreas." />
    </head>
""", unsafe_allow_html=True)
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Atom Studio Search",
    page_icon="🎨",
    layout="centered"
)

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
        background: rgba(255, 255, 255, 0.58) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
        border-radius: 32px !important;
        border: 1px solid rgba(255, 255, 255, 0.75) !important;
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

    /* 5. CAJA DE BÚSQUEDA SIN SUBRAYADO */
    .stTextInput > div {
        border-radius: 22px !important;
        padding: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    .stTextInput div[data-baseweb="input"],
    .stTextInput div[data-baseweb="base-input"] {
        border-radius: 20px !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #8023ff !important;
        box-shadow: none !important;
        outline: none !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput div[data-baseweb="input"]:focus-within,
    .stTextInput div[data-baseweb="base-input"]:focus-within {
        border: 2px solid #ff6600 !important;
        box-shadow: none !important;
        outline: none !important;
        background-color: #ffffff !important;
    }

    .stTextInput input {
        border-radius: 20px !important;
        padding: 12px 20px !important;
        font-size: 15px !important;
        color: #1e293b !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        font-family: 'Inter', sans-serif !important;
        background: transparent !important;
    }

    .stTextInput input:focus {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* 6. BOTÓN CTA CENTRADO Y PLANO */
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

    /* 7. CONTENEDOR DE LOGO */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        max-width: 110px;
        margin: 0 auto;
    }

    .logo-container img {
        max-height: 42px;
        width: auto;
        object-fit: contain;
    }

    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] {
            padding: 30px 20px !important;
            margin-top: 2rem !important;
            border-radius: 24px !important;
        }
        .main-title {
            font-size: 2rem !important;
        }
        .logo-container {
            max-width: 85px !important;
            margin-bottom: 10px;
        }
        .logo-container img {
            max-height: 32px !important;
        }
    }

    /* 8. TARJETAS DE RESULTADOS */
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
    # Asegura formato correcto en claves privadas multilinea
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

# Logo a la izquierda + Caja a la derecha
col_logo, col_input = st.columns([0.7, 3.3], vertical_alignment="center")

with col_logo:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h3 style='margin:0; color:#0f172a;'><b>ATOM</b></h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_input:
    query_usuario = st.text_input("", placeholder="Escribe tu búsqueda aquí...", label_visibility="collapsed")

# Botón CTA Centrado y Plano
st.markdown("<br>", unsafe_allow_html=True)
buscar_clicked = st.button("🔎 Buscar Materiales")

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
                
                # Búsqueda flexible OR encagada entre paréntesis si falla la primera
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
