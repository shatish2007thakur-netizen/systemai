import streamlit as st
from google import genai
import json
import os
import time
from datetime import datetime

# ================= STREAMLIT PAGE CONFIG =================
st.set_page_config(page_title="JARVIS AI ONLINE SYSTEM", page_icon="🤖", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; }
    .terminal-title {
        font-family: 'Courier New', Courier, monospace;
        color: #4af626;
        font-weight: bold;
        text-align: center;
        font-size: 32px;
        margin-bottom: 5px;
    }
    .terminal-status {
        color: #ffffff;
        font-style: italic;
        text-align: center;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .chat-box {
        background-color: #000000;
        border: 2px solid #2d2d2d;
        border-radius: 5px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #4af626;
        height: 350px;
        overflow-y: auto;
        margin-bottom: 20px;
        white-space: pre-wrap;
    }
    .mic-button {
        width: 100%;
        padding: 14px;
        border-radius: 8px;
        border: 2px solid #4af626;
        background-color: #000000;
        color: #4af626;
        font-weight: bold;
        cursor: pointer;
        font-size: 18px;
        font-family: 'Courier New', Courier, monospace;
        transition: 0.3s;
        margin-bottom: 10px;
    }
    .mic-button:hover {
        background-color: #4af626;
        color: #000000;
    }
    .mic-button.listening {
        background-color: #4af626;
        color: #000000;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="terminal-title">⚡ JARVIS AI ONLINE SYSTEM</div>', unsafe_allow_html=True)

# ================= GEMINI CONFIG =================
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = None

@st.cache_resource
def get_ai_client(key):
    if key:
        try:
            return genai.Client(api_key=key)
        except Exception as e:
            st.error(f"Client init error: {e}")
            return None
    return None

ai_client = get_ai_client(api_key)

# Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = "Jarvis: Systems online. Jarvis AI initialized.\nJarvis: Ready for your command, Sir."
if "tts_text" not in st.session_state:
    st.session_state.tts_text = ""
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# ================= CORE PROCESSOR =================
def process_command(command):
    if not command or command.strip() == "":
        return
        
    st.session_state.chat_history += f"\n\nYou: {command}"
    cmd = command.lower().strip()
    
    # System Commands
    if any(word in cmd for word in ["stop", "exit", "bye jarvis", "shutdown"]):
        reply = "Going offline. Goodbye, Sir. 🖥️"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply
        
    elif "open google" in cmd:
        reply = "Opening Google, Sir. 🌐"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply
        st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://www.google.com\'" />', unsafe_allow_html=True)
        
    elif "open youtube" in cmd:
        reply = "Opening YouTube, Sir. 📺"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply
        st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://www.youtube.com\'" />', unsafe_allow_html=True)
    
    elif "time" in cmd or "kitna baj" in cmd:
        now = datetime.now().strftime("%I:%M %p")
        reply = f"Sir, the current time is {now}. ⏰"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply

    elif "date" in cmd or "tareek" in cmd:
        today = datetime.now().strftime("%d %B %Y")
        reply = f"Sir, today is {today}. 📅"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply

    else:
        if not ai_client:
            reply = "Sir, Gemini API Key is missing. Please add it to secrets."
            st.session_state.chat_history += f"\n\nJarvis: {reply}"
            st.session_state.tts_text = reply
        else:
            try:
                # 🔥 FIX: Correct model name
                response = ai_client.models.generate_content(
                    model='gemini-1.5-flash',  # <--- YAHAN FIX KIYA
                    contents=command,
                    config={
                        'system_instruction': """You are JARVIS, Tony Stark's AI assistant. 
                        Keep responses short, crisp, and under 2 sentences. 
                        Use 'Sir' for the user. Be helpful and professional."""
                    }
                )
                reply = response.text.strip()
                st.session_state.chat_history += f"\n\nJarvis: {reply}"
                st.session_state.tts_text = reply
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "NOT_FOUND" in error_msg:
                    reply = "Sir, AI model not found. Please check the model name configuration. 🤖"
                elif "429" in error_msg:
                    reply = "Sir, rate limit reached. Please wait 5 seconds. ⏳"
                elif "API_KEY" in error_msg:
                    reply = "Sir, invalid API key. Please check your credentials. 🔑"
                else:
                    reply = f"Sir, AI core error: {error_msg[:80]}"
                st.session_state.chat_history += f"\n\nJarvis: {reply}"
                st.session_state.tts_text = reply

# Status
status_col1, status_col2 = st.columns([3, 1])
with status_col1:
    st.markdown('<div class="terminal-status">🟢 Status: Active | Click Mic or Type Command</div>', unsafe_allow_html=True)
with status_col2:
    if ai_client:
        st.markdown('<div class="terminal-status" style="color:#4af626;">✅ AI Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="terminal-status" style="color:#ff4b4b;">❌ API Missing</div>', unsafe_allow_html=True)

# Chat Display
st.markdown(f'<div class="chat-box">{st.session_state.chat_history}</div>', unsafe_allow_html=True)

# ================= HIDDEN VOICE INPUT =================
# Isme JS se voice text aayega
voice_text = st.text_input("hidden_voice", key="voice_input_field", label_visibility="collapsed")

if voice_text and voice_text != "":
    process_command(voice_text)
    # Clear karo taaki loop na ho
    st.session_state.voice_input_field = ""
    st.rerun()

# ================= JAVASCRIPT: VOICE RECOGNITION + TTS =================
tts_text = st.session_state.tts_text

js_code = f"""
<script>
// ================= TEXT TO SPEECH (JARVIS BOLTA HAI) =================
function speakJarvis(text) {{
    if ('speechSynthesis' in window && text && text !== "") {{
        window.speechSynthesis.cancel();
        let utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        // Try to find a male voice
        let voices = window.speechSynthesis.getVoices();
        let jarvisVoice = voices.find(v => v.name.includes('Male') || v.name.includes('David') || v.name.includes('Google UK'));
        if (jarvisVoice) utterance.voice = jarvisVoice;
        window.speechSynthesis.speak(utterance);
    }}
}}

// Agar TTS text hai toh bolo
let ttsText = `{tts_text}`;
if (ttsText && ttsText !== "") {{
    setTimeout(() => {{ speakJarvis(ttsText); }}, 300);
}}

// ================= SPEECH TO TEXT (USER BOLTA HAI) =================
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {{
    document.getElementById('mic-btn').innerHTML = '❌ Browser Not Supported';
    document.getElementById('mic-btn').disabled = true;
}} else {{
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN'; // Hindi+English samjhega
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const micBtn = document.getElementById('mic-btn');
    
    micBtn.addEventListener('click', function() {{
        try {{
            recognition.start();
            this.innerHTML = '⏳ Listening... Speak Now 🎤';
            this.classList.add('listening');
        }} catch (e) {{
            console.log('Error:', e);
        }}
    }});

    recognition.onresult = function(event) {{
        const transcript = event.results[0][0].transcript;
        console.log('Recognized:', transcript);
        
        // Streamlit ke hidden input mein daalo
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        let targetInput = null;
        for (let input of inputs) {{
            if (input.id && input.id.includes('voice_input_field')) {{
                targetInput = input;
                break;
            }}
        }}
        
        if (targetInput) {{
            targetInput.value = transcript;
            targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            
            // Enter key press simulate karo
            const enterEvent = new KeyboardEvent('keydown', {{
                bubbles: true,
                cancelable: true,
                key: 'Enter',
                keyCode: 13
            }});
            targetInput.dispatchEvent(enterEvent);
        }}
        
        micBtn.innerHTML = '🎙️ Click to Speak';
        micBtn.classList.remove('listening');
    }};

    recognition.onerror = function(event) {{
        console.error('Error:', event.error);
        micBtn.innerHTML = '❌ Error: ' + event.error;
        micBtn.classList.remove('listening');
        setTimeout(() => {{
            micBtn.innerHTML = '🎙️ Click to Speak';
        }}, 2000);
    }};

    recognition.onend = function() {{
        micBtn.innerHTML = '🎙️ Click to Speak';
        micBtn.classList.remove('listening');
    }};
}}
</script>
"""

# ================= MIC BUTTON =================
st.markdown("""
    <button id="mic-btn" class="mic-button">
        🎙️ Click to Speak
    </button>
""", unsafe_allow_html=True)

# JS inject
st.components.v1.html(js_code, height=0)

# ================= MANUAL TEXT INPUT =================
st.markdown("---")
st.markdown("### ⌨️ Type Your Command")

with st.form(key="command_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        text_input = st.text_input("Command:", placeholder="Type here...", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button("🚀 Send", use_container_width=True)
    
    if submit_button and text_input:
        process_command(text_input)
        st.rerun()

# ================= FOOTER =================
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px; font-family: 'Courier New', monospace;">
        ⚡ JARVIS AI v2.0 | Model: Gemini 1.5 Flash
    </div>
""", unsafe_allow_html=True)
