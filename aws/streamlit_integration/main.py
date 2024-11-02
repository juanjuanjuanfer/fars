import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="FARS - Facial Attendance Recognition System",
    page_icon="📷",
    layout="wide"
)

# CSS personalizado
st.markdown("""
    <style>
    /* Contenedor principal para centrar el contenido */
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    /* Título principal */
    .main-title {
        font-size: 5rem;
        color: #003366;
        font-weight: bold;
        margin-bottom: 30px;
    }

    /* Subtítulo */
    .subtitle {
        font-size: 1.2rem;
        color: #34495E;
        margin-bottom: 40px;
    }

    /* Botones de login y registro */
    .stButton>button {
        background-color: #003366;
        color: white;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        margin: 10px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition-duration: 0.4s;
    }

    .stButton>button:hover {
        background-color: #002244;
    }

    /* Sección de créditos */
    .credits-section {
        background-color: #F7F9FB;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
        width: 100%;  /* Asegura que ocupe todo el ancho del contenedor */
        max-width: 800px;  /* Máximo ancho para no ocupar toda la pantalla */
        display: flex;
        flex-direction: column;
        align-items: center;  /* Centra "Our Team" */
    }

    /* Título de créditos */
    .credits-title {
        font-size: 1.5rem;
        color: #2C3E50;
        margin-bottom: 20px;
        font-weight: bold;
        text-align: center;
    }

    /* Estilo para la sección de equipo */
    .team-section {
        color: #34495E;
        text-align: left;  /* Alinea los nombres a la izquierda dentro de la columna */
        width: 100%;
    }

    .team-container {
        display: flex;
        justify-content: flex-end;  /* Alinea las columnas del equipo a la derecha */
        gap: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-title">FARS</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Facial Attendance Recognition System</p>', unsafe_allow_html=True)

# Center the buttons
col1, col2, col3 = st.columns(3)
with col2:
    login_col, register_col = st.columns(2)
    with login_col:
        if st.button("Login", key="login_btn"):
            st.switch_page("pages/login.py")
    with register_col:
        if st.button("Register", key="register_btn"):
            st.switch_page("pages/register.py")

# Credits section
st.markdown('<div class="credits-section">', unsafe_allow_html=True)
st.markdown('<h2 class="credits-title">Our Team</h2>', unsafe_allow_html=True)

# Team members aligned to the right
st.markdown('<div class="team-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown('<div class="team-section"><h3>Data Analysts</h3>', unsafe_allow_html=True)
    st.write("• Sonia Mendía")
    st.write("• Christopher Cumi")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="team-section"><h3>Data Engineers</h3>', unsafe_allow_html=True)
    st.write("• Juan Fernandez")
    st.write("• Carlo Ek")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="team-section"><h3>Data Engineers</h3>', unsafe_allow_html=True)
    st.write("• Miguel Bastarrachea")
    st.write("• Yahir Sulu")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
