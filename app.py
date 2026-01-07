import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
import io

# Config
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 Clé API manquante (.env)")
    st.stop()

client = genai.Client(api_key=api_key)
st.set_page_config(page_title="AI Study Companion", page_icon="📚", layout="wide")

# Header
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;'>
    <h1>📚 AI Study Companion</h1>
    <p>Upload PDF → Résumé intelligent → Chat interactif → Télécharger</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Niveau")
level = st.sidebar.selectbox("Niveau d'étude", ["Débutant", "Intermédiaire", "Avancé"])

# Main columns
col1, col2 = st.columns([3, 1])

# 📄 UPLOAD PDF
with col1:
    st.header("📁 Upload ton cours PDF")
    uploaded_file = st.file_uploader("Choisis un PDF", type="pdf", help="Cours, TD, support de cours")

if uploaded_file:
    st.success(f"✅ Fichier: **{uploaded_file.name}**")
    
    if st.button("🔍 Extraire texte", type="primary", use_container_width=True):
        with st.spinner("Lecture PDF..."):
            try:
                pdf = PdfReader(io.BytesIO(uploaded_file.read()))
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                st.session_state.pdf_text = text
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.pdf_pages = len(pdf.pages)
                st.balloons()
                st.success(f"📖 **{len(pdf.pages)} pages** extraites!")
                
            except Exception as e:
                st.error(f"❌ Erreur PDF: {e}")

# Metrics
if "pdf_pages" in st.session_state:
    with col2:
        st.metric("📄 Pages", st.session_state.pdf_pages)
        st.metric("📊 Taille", f"{len(st.session_state.pdf_text[:1000])}... chars")

# 🧠 RÉSUMÉ
if "pdf_text" in st.session_state:
    st.divider()
    st.header("✨ Générer résumé pédagogique")
    
    if st.button("🎓 Créer résumé", type="primary", use_container_width=True):
        with st.spinner("Gemini analyse ton cours..."):
            try:
                prompt = f""" Crée un RÉSUMÉ PÉDAGOGIQUE pour étudiant {level}.

CONTENU DU COURS:
{st.session_state.pdf_text[:6000]}

FORMAT STRICT:
## 1. Concepts Clés
- Concept 1: explication simple
- Concept 2: explication simple  

## 2. Points Essentiels
1. Point critique 1
2. Point critique 2

## 3. Exemples Pratiques
- Application 1
- Application 2

## 4. Vocabulaire
- Terme1: définition
- Terme2: définition

**Sois CLAIR et PÉDAGOGIQUE.**"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                st.session_state.summary = response.text
                st.session_state.pdf_title = st.session_state.pdf_name.replace(".pdf", "")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

# 📥 TÉLÉCHARGEMENTS
if "summary" in st.session_state:
    st.subheader("📥 Téléchargements")
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="💾 Résumé Markdown",
            data=st.session_state.summary,
            file_name=f"{st.session_state.pdf_title}_resume.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="📄 Résumé TXT",
            data=st.session_state.summary,
            file_name=f"{st.session_state.pdf_title}_resume.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Afficher résumé
    with st.expander("👀 Aperçu résumé", expanded=True):
        st.markdown(st.session_state.summary)

# 💬 CHAT INTERACTIF
st.divider()
st.header("🤖 Chat avec Gemini (sur ton cours)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input chat
if prompt := st.chat_input("💡 '15 questions', 'quiz VR', 'explique immersion'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Gemini réfléchit..."):
            try:
                # Contexte intelligent
                if "summary" in st.session_state:
                    context = f"""COURS: {st.session_state.pdf_title}
RÉSUMÉ:
{st.session_state.summary}

QUESTION: {prompt}

Réponds PÉDAGOGIQUEMENT."""
                else:
                    context = prompt
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=context
                )
                
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"❌ Erreur chat: {e}")

# Clear chat
col_clear, col_share = st.columns(2)
with col_clear:
    if st.button("🗑️ Effacer chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
