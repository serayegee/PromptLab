# streamlit_app.py 
import streamlit as st
import sys
import os
import time
from datetime import datetime

st.set_page_config(
    page_title="PromptLab Chatbot | RAG Sistemi",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS - Chatbot temalı
st.markdown("""
<style>
    /* Ana tema */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat container */
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease-out;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .chat-message.assistant {
        background: white;
        color: #31333f;
        margin-right: 20%;
        border: 2px solid #667eea;
    }
    
    .chat-message .avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 10px;
    }
    
    .chat-message.user .avatar {
        background: rgba(255,255,255,0.2);
    }
    
    .chat-message.assistant .avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .chat-message .message {
        padding: 10px 0;
        line-height: 1.6;
    }
    
    .chat-message .timestamp {
        font-size: 0.8em;
        opacity: 0.7;
        margin-top: 5px;
    }
    
    /* Metrikler */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #667eea;
        text-align: center;
        margin: 5px;
    }
    
    /* Butonlar */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Chat input */
    .stTextInput input {
        border-radius: 25px !important;
        border: 2px solid #667eea !important;
        padding: 15px 20px !important;
        font-size: 1em !important;
    }
    
    .stTextInput input:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.2) !important;
    }
    
    /* Form butonları */
    .stForm button {
        border-radius: 10px !important;
        height: 48px !important;
        margin-top: 0px !important;
    }
    
    /* Animasyonlar */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes typing {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    .typing-indicator {
        display: flex;
        gap: 5px;
        padding: 10px;
    }
    
    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid #667eea;
    }
    
    /* Başlık */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
    }
    
    /* Quick command butonları */
    .quick-command {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Model import
try:
    from promptlab_model import promptlab
    AI_ACTIVE = True
    GEMINI_MODE = promptlab.gemini_agent.available if promptlab else False
except Exception as e:
    AI_ACTIVE = False
    GEMINI_MODE = False

# Session state initialization
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Karşılama mesajı
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Merhaba! Ben **PromptLab Chatbot**'um. Prompt'larınızı optimize etmek için buradayım!\n\n✨ Basit bir prompt yazın, ben onu profesyonel hale getireyim.\n\n**Örnek:** 'bana python öğret' veya 'makale yaz'",
        "timestamp": datetime.now().strftime("%H:%M"),
        "type": "greeting"
    })

if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0

if 'quick_prompt' not in st.session_state:
    st.session_state.quick_prompt = ""

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Başlık
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 class="main-header" style="font-size: 3em;">🤖 PromptLab Chatbot</h1>
    <p style="color: #667eea; font-size: 1.2em; font-weight: 600;">
        Yapay Zeka Destekli Prompt Optimizasyon Asistanı
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 4em;">🤖</div>
        <h2 style="color: white; margin: 10px 0;">PromptLab Bot</h2>
        <p style="color: #a0aec0; font-size: 0.9em;">Sohbet Asistanı</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Key
    with st.expander("🔑 Gemini API Anahtarı", expanded=not bool(os.environ.get('GEMINI_API_KEY'))):
        current_key = os.environ.get('GEMINI_API_KEY', '')
        
        if current_key:
            st.success("✅ API Anahtarı Aktif")
            if st.button("🔄 Değiştir", use_container_width=True):
                st.session_state.show_api_input = True
        else:
            st.warning("⚠️ API Yok")
            st.session_state.show_api_input = True
        
        if st.session_state.get('show_api_input', not current_key):
            with st.form("api_form"):
                api_key = st.text_input("API Key:", type="password")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("💾 Kaydet"):
                        if api_key:
                            os.environ['GEMINI_API_KEY'] = api_key
                            st.success("✅ Kaydedildi!")
                            time.sleep(0.5)
                            st.rerun()
                
                with col2:
                    if st.form_submit_button("❌ İptal"):
                        st.session_state.show_api_input = False
                        st.rerun()
    
    # Sohbet İstatistikleri
    st.markdown("### 📊 Sohbet İstatistikleri")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mesajlar", len(st.session_state.messages))
    with col2:
        st.metric("Optimizasyon", st.session_state.conversation_count)
    
    st.markdown("---")
    
    # Hızlı Komutlar
    st.markdown("### ⚡ Hızlı Komutlar")
    
    quick_commands = [
        ("🐍 Python Öğret", "bana python öğret"),
        ("💻 Kod Yaz", "fibonacci kodu yaz"),
        ("📝 Makale", "yapay zeka hakkında makale yaz"),
        ("🎨 Hikaye", "bilim kurgu hikayesi yaz"),
        ("📊 Analiz", "veri analizi için prompt yaz"),
        ("🌍 Bilgi", "Türkiye hakkında bilgi ver")
    ]
    
    for label, prompt in quick_commands:
        if st.button(label, use_container_width=True, key=f"quick_{label}"):
            # Session state'e kaydet ve input key'ini değiştir
            st.session_state.quick_prompt = prompt
            st.session_state.input_key += 1
            st.toast(f"✅ '{label}' input'a yazıldı! Düzenleyip Enter'a basın.", icon="✅")
            st.rerun()
    
    st.markdown("---")
    
    # Sohbet Kontrolü
    st.markdown("### 🎮 Kontroller")
    
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.session_state.quick_prompt = ""
        st.session_state.input_key += 1
        # Karşılama mesajını tekrar ekle
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Sohbet temizlendi! Yeni bir prompt ile başlayalım.",
            "timestamp": datetime.now().strftime("%H:%M"),
            "type": "greeting"
        })
        st.rerun()
    
    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        # Sohbeti text olarak kaydet
        chat_text = "\n\n".join([
            f"[{msg['timestamp']}] {'Kullanıcı' if msg['role'] == 'user' else 'Asistan'}: {msg['content']}"
            for msg in st.session_state.messages
        ])
        st.download_button(
            "📥 İndir",
            chat_text,
            file_name=f"promptlab_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Sistem Durumu
    st.markdown("### 🔧 Sistem")
    if AI_ACTIVE:
        if GEMINI_MODE:
            st.success("🤖 Gemini Pro")
        else:
            st.info("🔄 Yedek Mod")
        
        st.metric("Vektör DB", "✅")
        st.metric("RAG Pipeline", "✅")
    else:
        st.error("❌ Hata")

# Ana chat alanı
chat_container = st.container()

with chat_container:
    # Mesajları göster
    for i, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="avatar">👤</div>
                <div class="message">{content}</div>
                <div class="timestamp">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Eğer optimizasyon sonucu varsa
            if "result" in message:
                result = message["result"]
                
                # Asistan mesajı
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="avatar">🤖</div>
                    <div class="message">
                        <strong>✨ Prompt'unuz optimize edildi!</strong><br><br>
                        {result['optimized_prompt']}
                    </div>
                    <div class="timestamp">{timestamp}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Metrikler
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Model", result.get('ai_model', 'N/A').split('(')[0].strip())
                with col2:
                    st.metric("RAG", result.get('rag_mode', 'N/A'))
                with col3:
                    st.metric("İyileşme", f"%{result.get('improvement_percentage', 0):.0f}")
                with col4:
                    kelime_artisi = len(result['optimized_prompt'].split()) - len(result['original_prompt'].split())
                    st.metric("Kelime", f"+{kelime_artisi}")
                
                # Analiz detayları
                with st.expander("📊 Detaylı Analiz"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write("**Orijinal Prompt:**")
                        st.info(result['original_prompt'])
                    with col_b:
                        st.write("**Analiz:**")
                        st.write(f"- Kategori: {result['analysis']['category']}")
                        st.write(f"- Amaç: {result['analysis']['intent']}")
                        st.write(f"- Kelime: {result['analysis']['word_count']}")
                        st.write(f"- Skor: {result['analysis']['overall_score']:.2f}/1.0")
            else:
                # Normal asistan mesajı
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="avatar">🤖</div>
                    <div class="message">{content}</div>
                    <div class="timestamp">{timestamp}</div>
                </div>
                """, unsafe_allow_html=True)

# Chat input - Form ile Enter desteği
st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-bottom: 10px;">
    <p style="color: #667eea; font-size: 0.9em;">
        💡 <strong>İpucu:</strong> Sol paneldeki hızlı komutları kullanarak prompt'u buraya yazabilir, düzenleyebilir ve Enter ile gönderebilirsiniz!
    </p>
</div>
""", unsafe_allow_html=True)

# Form ile Enter desteği - DÜZELTİLMİŞ VERSİYON
with st.form(key="chat_form", clear_on_submit=True):  # clear_on_submit=True yap
    col_input, col_buttons = st.columns([4, 1])
    
    with col_input:
        # Dynamic key ile text input - quick_prompt değiştiğinde yeniden render olacak
        user_input = st.text_input(
            "💬 Prompt",
            value=st.session_state.quick_prompt,  # Doğrudan session state'ten al
            placeholder="💬 Buraya yazın ve Enter'a basın...",
            disabled=not AI_ACTIVE,
            label_visibility="collapsed",
            key=f"message_input_{st.session_state.input_key}"  # Dynamic key
        )
    
    with col_buttons:
        col_send, col_clear = st.columns(2)
        with col_send:
            send_button = st.form_submit_button("📤", use_container_width=True, type="primary")
        with col_clear:
            clear_button = st.form_submit_button("🗑️", use_container_width=True)

# Clear butonuna basıldıysa
if clear_button:
    st.session_state.quick_prompt = ""
    st.session_state.input_key += 1  # Input'u yeniden render et
    st.rerun()

# Gönder butonuna basıldığında veya Enter'a basıldığında
if send_button and user_input.strip():
    prompt = user_input.strip()
    
    # Quick prompt'u temizle ve input key'ini güncelle
    st.session_state.quick_prompt = ""
    st.session_state.input_key += 1
    
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    # Typing indicator göster
    with st.spinner("🤖 Düşünüyorum..."):
        time.sleep(0.5)
        
        try:
            # RAG ile işle
            result = promptlab.process_prompt(prompt)
            
            # Asistan cevabını ekle
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"İşte optimize edilmiş prompt'unuz:",
                "timestamp": datetime.now().strftime("%H:%M"),
                "result": result
            })
            
            st.session_state.conversation_count += 1
            
            # Başarı sesi (optional)
            st.balloons()
            
        except Exception as e:
            # Hata mesajı
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Üzgünüm, bir hata oluştu: {str(e)}\n\nLütfen tekrar deneyin.",
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    st.rerun()

# Yardım alanı
with st.expander("❓ Nasıl Kullanılır?"):
    st.markdown("""
    ### 🤖 PromptLab Chatbot Rehberi
    
    **1. Prompt Yazın:**
    - Alttaki chat kutusuna basit bir prompt yazın
    - Örnek: "bana python öğret"
    
    **2. Hızlı Komutlar:**
    - Sol paneldeki butonlara tıklayın
    - Prompt otomatik olarak input kutusuna yazılacak
    - İstediğiniz gibi düzenleyip Enter'a basın
    
    **3. Optimizasyon:**
    - Bot prompt'unuzu analiz edecek
    - RAG sistemi ile optimize edecek
    - Profesyonel sonucu size sunacak
    
    **4. Sohbet Yönetimi:**
    - 🗑️ Sohbeti temizleyin
    - 💾 Sohbeti kaydedin
    - 📊 İstatistikleri görün
    
    **İpuçları:**
    - Kısa ve net promptlar yazın
    - Farklı kategorileri deneyin
    - API key'inizi eklemeyi unutmayın!
    """)

# Alt bilgi
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p style="color: #667eea; font-weight: 600;">
        🤖 PromptLab Chatbot | Akbank GenAI Bootcamp 2024
    </p>
    <p style="color: #666; font-size: 0.9em;">
        ❤️ Streamlit + Google Gemini Pro + RAG Pipeline
    </p>
</div>
""", unsafe_allow_html=True)