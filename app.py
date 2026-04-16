import streamlit as st
import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Sayfa Konfigürasyonu ---
st.set_page_config(page_title="Haber Manipülasyon Dedektörü", page_icon="📰", layout="wide")

st.title("🕵️‍♂️ Ajan Tabanlı Haber Manipülasyon Analizi")
st.markdown("""
Bu sistem, **Google Gemini 2.0 Flash** modeli ve **LangChain** orkestrasyonu kullanarak haber metinlerini analiz eder ve bir **Manipülasyon Riski** puanı hesaplar.
""")

# --- API Key Yönetimi ---
st.sidebar.header("Ayarlar")

# Önce ortam değişkenlerinden anahtarı çekmeyi dene
google_api_key = os.environ.get("GOOGLE_API_KEY")

if google_api_key:
    st.sidebar.success("Google API Anahtarı Sistemden Alındı ✅")
else:
    st.sidebar.warning("API Anahtarı Bulunamadı.")
    google_api_key = st.sidebar.text_input(
        "Google AI Studio API Key", 
        type="password", 
        help="https://aistudio.google.com/ adresinden 'Create API Key' diyerek alabilirsiniz."
    )

# --- Model Kurulumu ---
@st.cache_resource
def get_llm(api_key):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.1, 
            convert_system_message_to_human=True
        )
        return llm
    except Exception as e:
        return None

# --- Ajan (Zincir) Tanımları ---

# 1. AJAN A: Adjective Hunter (Duygu Avcısı)
prompt_template_a = """
You are an expert linguist and 'Adjective Hunter'.
Your Task: Analyze the provided Turkish news text. Identify explicitly emotional, exaggerated, or manipulative adjectives and adverbs (e.g., 'korkunç', 'skandal', 'müthiş', 'vahşice', 'akılalmaz').

Output format:
- List the detected words.
- Briefly explain why they are manipulative in Turkish context.
- If no such words are found, state that the text seems neutral regarding adjectives.
- Use Turkish for text.

News Text:
{text}

Analysis (in Turkish):
"""

# 2. AJAN B: Perspective Analyst (Perspektif Analisti)
prompt_template_b = """
You are a 'Perspective Analyst' specialized in media bias and framing.
Your Task: Analyze the provided Turkish news text for perspective bias. Use Turkish for text.

Please answer these questions:
1. Whose perspective is dominant? (Who is the subject/protagonist?)
2. Whose voice or opinion is missing?
3. Is there active/passive voice manipulation to hide responsibility?

News Text:
{text}

Perspective Analysis (in Turkish):
"""

# 3. AJAN S: Risk Scorer (YENİ - Skorlama Ajanı)
prompt_template_s = """
You are a 'Risk Assessor'. Your job is to calculate a 'Manipulation Probability Score' (0-100%) based on the text and previous analyses.

Input Data:
1. Original Text: {text}
2. Emotional Analysis: {analysis_a}
3. Perspective Analysis: {analysis_b}

Your Task:
- Evaluate how biased and manipulative the text is.
- Assign a score between 0 (Completely Neutral/Fact-based) and 100 (Highly Manipulative/Propaganda).
- Provide a ONE sentence reason in Turkish.

Output Format (Strictly follow this):
SCORE: <Insert Integer Score Here>
REASON: <Insert Explanation Here>
"""

# 4. AJAN C: Neutralizer (Nötrleştirici)
prompt_template_c = """
You are a 'Neutralizer', a senior editor aiming for pure objectivity.
Input Data:
1. Original Text: {text}
2. Analyses: {analysis_a}, {analysis_b}

Your Task: Rewrite the news text in Turkish.
- Remove all emotional/manipulative adjectives.
- State only the dry facts (5W1H).
- Use a formal, third-person objective tone.
- Use Turkish for text.

Neutralized Text (in Turkish):
"""

# --- Yardımcı Fonksiyonlar ---
def parse_score(output_text):
    """Model çıktısından skoru ayıklar."""
    try:
        # Regex ile "SCORE: 85" gibi yapıları bul
        match = re.search(r"SCORE:\s*(\d+)", output_text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0
    except:
        return 0

def parse_reason(output_text):
    """Model çıktısından nedeni ayıklar."""
    try:
        match = re.search(r"REASON:\s*(.*)", output_text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Neden belirtilmedi."
    except:
        return output_text

# --- Arayüz Mantığı ---

default_text = "Belediyenin aldığı bu skandal karar, vatandaşları çileden çıkardı. Yöneticiler keyif çatarken halk perişan oldu."
news_text = st.text_area("Analiz edilecek haber metnini giriniz:", height=150, value=default_text)

btn_analyze = st.button("Analizi Başlat", type="primary")

if btn_analyze:
    if not google_api_key:
        st.error("Lütfen Google AI Studio API Anahtarınızı giriniz.")
    elif not news_text:
        st.warning("Lütfen bir metin giriniz.")
    else:
        llm = get_llm(google_api_key)
        
        if llm is None:
             st.error("Model başlatılamadı.")
        else:
            try:
                # Zincirleri Oluştur
                chain_a = PromptTemplate.from_template(prompt_template_a) | llm | StrOutputParser()
                chain_b = PromptTemplate.from_template(prompt_template_b) | llm | StrOutputParser()
                chain_s = PromptTemplate.from_template(prompt_template_s) | llm | StrOutputParser() 
                chain_c = PromptTemplate.from_template(prompt_template_c) | llm | StrOutputParser()

                # --- İŞLEM BAŞLIYOR ---
                status_container = st.empty()
                
                # Adım 1 & 2: Analizler
                status_container.info('🕵️ Ajan A ve B metni inceliyor...')
                result_a = chain_a.invoke({"text": news_text})
                result_b = chain_b.invoke({"text": news_text})
                
                # Adım 3: Skorlama (Yeni)
                status_container.info('📊 Ajan S manipülasyon riskini hesaplıyor...')
                result_s_raw = chain_s.invoke({
                    "text": news_text, 
                    "analysis_a": result_a, 
                    "analysis_b": result_b
                })
                score = parse_score(result_s_raw)
                reason = parse_reason(result_s_raw)

                # Adım 4: Nötrleştirme
                status_container.info('✍️ Ajan C metni yeniden yazıyor...')
                result_c = chain_c.invoke({
                    "text": news_text,
                    "analysis_a": result_a,
                    "analysis_b": result_b
                })
                
                status_container.empty()

                # --- SONUÇLARI GÖSTERME ---
                
                # 1. SKOR KARTI (En Üste)
                st.divider()
                score_col1, score_col2 = st.columns([1, 3])
                
                with score_col1:
                    # Renk belirleme
                    score_color = "green" if score < 30 else "orange" if score < 70 else "red"
                    st.markdown(f"""
                    <div style="text-align: center; border: 2px solid {score_color}; padding: 10px; border-radius: 10px;">
                        <h3 style="margin:0; color: {score_color};">Manipülasyon Riski</h3>
                        <h1 style="margin:0; font-size: 48px; color: {score_color};">%{score}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with score_col2:
                    st.caption("SKORLAMA NEDENİ")
                    st.info(reason)
                    st.progress(score / 100)

                st.divider()

                # 2. DETAYLI ANALİZLER
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🔴 Duygu Analizi")
                    st.markdown(result_a)
                with col2:
                    st.subheader("🔵 Perspektif Analizi")
                    st.markdown(result_b)
                
                # 3. NÖTR METİN
                st.divider()
                st.subheader("🟢 Ajan C: Nötrleştirilmiş Metin")
                st.success(result_c)
                
                with st.expander("Orijinal ve Nötr Metni Karşılaştır"):
                    c1, c2 = st.columns(2)
                    c1.text_area("Orijinal", news_text, height=200, disabled=True)
                    c2.text_area("Nötr (AI)", result_c, height=200, disabled=True)

            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")