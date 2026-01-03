import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pypdf import PdfReader
import io

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ ERREUR: GEMINI_API_KEY non trouvée dans .env")
    st.stop()

#  Configurer Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3-flash")

# Page Streamlit
st.set_page_config(
    page_title="AI Study Companion",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Companion")
st.markdown("**Jour 2 : Upload PDF & Extraction** ")

#  ÉTAPE 1 : Test Gemini (gardé du Jour 1)
st.header("🔧 Test de Connexion Gemini")
if st.button("Tester la connexion", type="secondary"):
    try:
        response = model.generate_content("Connexion OK!")
        st.success(f"✅ {response.text}")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")

#  ÉTAPE 2 : Upload PDF
st.header("📄 Étape 1 : Upload ton PDF")
uploaded_file = st.file_uploader(
    "Choisis un fichier PDF de cours",
    type="pdf",
    help="Upload un PDF de cours ou notes (max 10MB)"
)

#  ÉTAPE 3 : Extraction du texte
if uploaded_file is not None:
    # Afficher infos du fichier
    st.info(f"📁 Fichier : **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    
    # Extraire le texte
    if st.button(" Extraire le texte du PDF", type="primary"):
        with st.spinner("Extraction en cours..."):
            try:
                # Lire le PDF
                pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                
                # Extraire tout le texte
                full_text = ""
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:  # Si la page a du texte
                        full_text += f"\\n--- PAGE {page_num} ---\\n{page_text}\\n"
                
                st.session_state.pdf_text = full_text
                
                # Afficher le résultat
                st.success(f" **Extraction réussie!** {len(pdf_reader.pages)} pages extraites")
                st.metric("Nombre de pages", len(pdf_reader.pages))
                st.metric("Nombre de caractères", len(full_text))
                
            except Exception as e:
                st.error(f" Erreur extraction: {str(e)}")

#  ÉTAPE 4 : Affichage du contenu
if "pdf_text" in st.session_state:
    st.header("Contenu extrait du PDF")
    
    # Aperçu (premiers 2000 caractères)
    preview = st.session_state.pdf_text[:2000]
    full_text_button = st.button("Voir le texte complet")
    
    with st.expander(" Aperçu du contenu (clique pour agrandir)"):
        st.text_area("Aperçu", preview, height=300, disabled=True)
    
    if full_text_button:
        st.text_area("Texte complet", st.session_state.pdf_text, height=400, disabled=True)
    
    # Bouton pour vider
    if st.button(" Nouveau PDF"):
        del st.session_state.pdf_text

