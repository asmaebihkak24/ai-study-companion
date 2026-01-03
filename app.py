import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Cle API manquante")
    st.stop()

client = genai.Client(api_key=api_key)

st.set_page_config(page_title="AI Study Companion", page_icon="📚", layout="wide")

st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h1 style='color: #1f77b4;'>📚 AI Study Companion</h1>
    <p style='color: #666;'>Upload → Resumer → Telecharger</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Parametres")
level = st.sidebar.selectbox("Niveau", ["Debutant", "Intermediaire", "Avance"])

col1, col2 = st.columns([2, 1])

with col1:
    st.header("📄 Upload ton cours")
    uploaded_file = st.file_uploader("PDF", type="pdf")

if uploaded_file:
    st.info(f"📁 {uploaded_file.name}")
    
    if st.button("🔍 Extraire", type="primary", use_container_width=True):
        with st.spinner("Lecture..."):
            try:
                pdf = PdfReader(io.BytesIO(uploaded_file.read()))
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                st.session_state.pdf_text = text
                st.session_state.pdf_pages = len(pdf.pages)
                st.balloons()
                st.success(f"✅ {len(pdf.pages)} pages")
                
            except Exception as e:
                st.error(f"Erreur: {e}")

if "pdf_text" in st.session_state:
    with col2:
        st.metric("Pages", st.session_state.pdf_pages)
    
    st.divider()
    st.header("🧠 Resume Pedagogique")
    
    if st.button("✨ Generer", type="primary", use_container_width=True):
        with st.spinner("Gemini cree ton resume..."):
            try:
                # ✅ PROMPT PÉDAGOGIQUE
                prompt = f"""Tu es professeur. CRÉE UN RÉSUMÉ PÉDAGOGIQUE du cours pour étudiant {level}.

OBJECTIF: L'étudiant COMPREND le cours (pas un CV!)

CONTENU À RÉSUMER:
{st.session_state.pdf_text[:4000]}

FORMAT OBLIGATOIRE:
## 1. Concepts Fondamentaux
[Explique les idées principales du cours en langage simple]
- Concept 1: Explication claire
- Concept 2: Explication claire
- Concept 3: Explication claire

## 2. Points Clés à Retenir
[Les éléments ESSENTIELS pour comprendre et réussir l'examen]
1. Point important 1: Pourquoi c'est important
2. Point important 2: Pourquoi c'est important
3. Point important 3: Pourquoi c'est important

## 3. Comment Ces Concepts Fonctionnent
[Explique comment les concepts s'appliquent ensemble]
- Relation entre concepts
- Applications pratiques
- Exemples concrets

## 4. Vocabulaire Important
[Mots clés à connaître]
- Terme 1: Définition
- Terme 2: Définition
- Terme 3: Définition

Sois SIMPLE, CLAIR, PÉDAGOGIQUE."""
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                st.session_state.summary = response.text
                st.success("✅ Resume pedagogique genere!")
                
            except Exception as e:
                st.error(f"Erreur: {e}")

if "summary" in st.session_state:
    st.markdown("### 📝 Ton Resume")
    st.markdown(st.session_state.summary)
    
    # ✅ CRÉER PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Ajouter le contenu
    for line in st.session_state.summary.split("\n"):
        if line.strip():
            elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
    
    doc.build(elements)
    pdf_bytes = pdf_buffer.getvalue()
    
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    with col_dl1:
        st.download_button(
            "💾 PDF",
            pdf_bytes,
            "resume.pdf",
            "application/pdf",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            "💾 Markdown",
            st.session_state.summary,
            "resume.md",
            use_container_width=True
        )
    with col_dl3:
        st.download_button(
            "💾 TXT",
            st.session_state.summary,
            "resume.txt",
            use_container_width=True
        )

st.divider()
if st.button("🔄 Nouveau"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
