import streamlit as st
import pdfplumber
import re
import pandas as pd
from io import BytesIO

# ==============================
# ⚙️ CONFIG GENERAL
# ==============================
st.set_page_config(page_title="Buscador Judicial FPA", layout="centered")

# ==============================
# 🔐 CONFIGURACIÓN DE LOGIN
# ==============================

# Diccionario de usuarios válidos: {"usuario": "contraseña"}
VALID_USERS = {
    "fpa_admin": "panamera2025",
    "carlota": "chapity298"
    # agrega los que quieras:
    # "otro_usuario": "otra_contraseña"
}

def check_credentials(username, password):
    """Verifica si el usuario y contraseña son válidos."""
    return username in VALID_USERS and VALID_USERS[username] == password

def login_screen():
    """Muestra la pantalla de login."""
    st.title("🔐 Acceso al Buscador Judicial FPA")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if check_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success(f"Bienvenido, {username} ✨")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

# Inicializar estado de sesión
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ==============================
# 🔓 LOGOUT (BOTÓN EN SIDEBAR)
# ==============================
if st.session_state["authenticated"]:
    with st.sidebar:
        st.markdown("### 👤 Sesión")
        st.write(f"Usuario: **{st.session_state.get('username', '')}**")
        if st.button("Cerrar sesión"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = ""
            st.experimental_rerun()

# Si NO está autenticado, mostrar login y parar
if not st.session_state["authenticated"]:
    login_screen()
    st.stop()

# ==============================
# 🚀 APP PRINCIPAL (DESPUÉS DEL LOGIN)
# ==============================

st.title("🔍 Buscador Judicial – FPA Solutions")
st.caption(f"Usuario conectado: **{st.session_state.get('username', '')}**")
st.write("Sube un PDF y busca datos dentro del boletín judicial.")

# ---------------------------------------------------------
# Función de búsqueda flexible
# ---------------------------------------------------------
def normalize(text):
    if not text:
        return None
    text = text.lower()
    text = re.sub(r'[^a-z0-9áéíóúñ/° ]', '', text)
    return text

def flexible_search(clean_text, pattern):
    if not pattern:
        return None
    pattern = normalize(pattern)
    words = pattern.split()
    regex = r".{0,25}" + r".*?".join(words) + r".{0,25}"
    match = re.search(regex, clean_text)
    if match:
        return match.group(0)
    return "No encontrado"

# ---------------------------------------------------------
# Cargar PDF
# ---------------------------------------------------------
uploaded_pdf = st.file_uploader("Sube el archivo PDF", type=["pdf"])

if uploaded_pdf:
    with pdfplumber.open(uploaded_pdf) as pdf:
        full_text = ""
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"

    clean_text = normalize(full_text)

    st.success("PDF cargado correctamente ✔️")

    st.subheader("📌 Ingresa los datos a buscar dentro del PDF")

    col1, col2 = st.columns(2)

    with col1:
        juzgado = st.text_input("Juzgado")
        expediente = st.text_input("Expediente")
        secretaria = st.text_input("Secretaría")

    with col2:
        juicio = st.text_input("Tipo de Juicio")
        demandante = st.text_input("Demandante")
        demandado = st.text_input("Demandado")

    if st.button("Buscar en el PDF"):
        st.subheader("📄 Resultados")

        results = {
            "Juzgado": flexible_search(clean_text, juzgado),
            "Expediente": flexible_search(clean_text, expediente),
            "Secretaría": flexible_search(clean_text, secretaria),
            "Juicio": flexible_search(clean_text, juicio),
            "Demandante": flexible_search(clean_text, demandante),
            "Demandado": flexible_search(clean_text, demandado)
        }

        st.write(results)

        # Convertir resultados a Excel
        df = pd.DataFrame(results.items(), columns=["Campo", "Valor"])

        output = BytesIO()
        df.to_excel(output, index=False)
        excel_data = output.getvalue()

        st.download_button(
            label="📥 Descargar resultados en Excel",
            data=excel_data,
            file_name="resultados_busqueda.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.success("Búsqueda finalizada ✔️")
else:
    st.info("Por favor sube un archivo PDF para comenzar.")
