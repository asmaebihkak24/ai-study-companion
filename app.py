import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# ✅ Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ ERREUR: GEMINI_API_KEY non trouvée dans .env")
    st.stop()

# ✅ Configurer Gemini
genai.configure(api_key=api_key)

# ✅ Page Streamlit
st.set_page_config(
    page_title="AI Study Companion",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Companion")
st.write("Transforme tes cours en ressources d'apprentissage personnalisées")

# ✅ Test simple : Demander à Gemini de vérifier la connexion
st.header("🔧 Test de Connexion Gemini")

if st.button("Tester la connexion"):
    try:
        model = genai.GenerativeModel("gemini-3-flash")
        response = model.generate_content("Dis 'Connexion réussie!' en français.")
        st.success(f"✅ {response.text}")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")

st.info("💡 Si tu vois '✅ Connexion réussie!' au-dessus, tout marche!")

