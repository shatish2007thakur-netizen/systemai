import streamlit as st
import requests
import json
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; }
    .chat-box {
        background-color: #000000;
        border: 1px solid #4af626;
        border-radius: 10px;
        padding: 20px;
        height: 400px;
        overflow-y: auto;
        color: #4af626;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
    .title { color: #4af626; text-align: center; font-size: 40px; font-weight: bold; }
    .status { color: #aaa; text-align: center; font-style: italic; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">⚡ JARVIS (AWS Proxy)</div>', unsafe_allow_html=True)

# ================= SECRETS LOAD =================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    API_URL = st.secrets["GEMINI_API_BASE_URL"]  # Ye URL aapko AWS se lena hai
except KeyError as e:
    st.error(f"❌ Secrets mein '{e.args[0]}' missing hai! `.streamlit/secrets.toml` check karein.")
    st.stop()

if not API_URL:
    st.error("❌ GEMINI_API_BASE_URL empty hai. AWS API Gateway URL daalein.")
    st.stop()

# ================= SESSION STATE =================
if "history" not in st.session_state:
    st.session_state.history = "Jarvis: Systems online. Ready, Sir.\n"
if "tts" not in st.session_state:
    st.session_state.tts = ""

# ================= CHAT DISPLAY =================
st.markdown(f'<div class="chat-box">{st.session_state.history}</div>', unsafe_allow_html=True)
st.markdown('<div class="status">🟢 Status: Active | Click Mic or Type Command</div>', unsafe_allow_html=True)

# ================= VOICE INPUT (Hidden) =================
voice_text = st.text_input("voice", key="voice_input", label_visibility="collapsed")
if voice_text:
    st.session_state.voice_input = ""

# ================= AI CALL FUNCTION (Using AWS Proxy) =================
def call_ai(cmd):
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY  # AWS API Gateway expects this
        }
        # Payload format – adjust based on your proxy expectation
        payload = {
            "contents": [{"parts": [{"text": f"You are JARVIS. User said: {cmd}. Reply in 1-2 short sentences."}]}]
        }
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Try to extract reply (Google-style or custom)
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except:
                return data.get("reply") or data.get("response") or "Sir, I got a response but couldn't parse it."
        else:
            return f"Sir, API error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"Sir, connection error: {str(e)[:80]}"

# ================= PROCESS COMMAND =================
def process_cmd(cmd):
    if not cmd:
        return
    st.session_state.history += f"You: {cmd}\n"
    cmd_lower = cmd.lower()

    # Local commands
    if "time" in cmd_lower:
        reply = f"Sir, time is {datetime.now().strftime('%I:%M %p')}."
    elif "date" in cmd_lower:
        reply = f"Sir, today is {datetime.now().strftime('%d %B %Y')}."
    elif "open google" in cmd_lower:
        reply = "Opening Google, Sir."
        st.session_state.history += f"Jarvis: {reply}\n"
        st.session_state.tts = reply
        st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://google.com\'">', unsafe_allow_html=True)
        return
    elif "exit" in cmd_lower or "bye" in cmd_lower:
        reply = "Goodbye, Sir!"
        st.session_state.history += f"Jarvis: {reply}\n"
        st.session_state.tts = reply
        st.rerun()
        return
    else:
        reply = call_ai(cmd)  # AI call

    st.session_state.history += f"Jarvis: {reply}\n"
    st.session_state.tts = reply

# ================= JAVASCRIPT (Voice + TTS) =================
tts_text = st.session_state.get("tts", "")
js_code = f"""
<script>
// Text to Speech
function speak(text) {{
    if (window.speechSynthesis && text) {{
        window.speechSynthesis.cancel();
        let u = new SpeechSynthesisUtterance(text);
        u.rate = 0.9;
        window.speechSynthesis.speak(u);
    }}
}}
let t = `{tts_text}`;
if (t) {{ setTimeout(() => speak(t), 300); }}

// Speech to Text
const btn = document.createElement('button');
btn.innerText = '🎤 Click to Speak';
btn.style.cssText = 'width:100%; padding:15px; background:#000; color:#4af626; border:2px solid #4af626; border-radius:8px; font-size:20px; margin:10px 0; cursor:pointer;';
btn.id = 'micBtn';
document.querySelector('.stApp').prepend(btn);

const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {{
    const rec = new SR();
    rec.lang = 'en-IN';
    btn.onclick = () => {{
        btn.innerText = '⏳ Listening...';
        btn.style.background = '#4af626';
        btn.style.color = '#000';
        rec.start();
    }};
    rec.onresult = (e) => {{
        let text = e.results[0][0].transcript;
        let inputs = window.parent.document.querySelectorAll('input[type="text"]');
        for (let inp of inputs) {{
            if (inp.id && inp.id.includes('voice_input')) {{
                inp.value = text;
                inp.dispatchEvent(new Event('input', {{bubbles:true}}));
                inp.dispatchEvent(new KeyboardEvent('keydown', {{key:'Enter', keyCode:13}}));
                break;
            }}
        }}
        btn.innerText = '🎤 Click to Speak';
        btn.style.background = '#000';
        btn.style.color = '#4af626';
    }};
    rec.onerror = () => {{
        btn.innerText = '❌ Error, Click Again';
        btn.style.background = '#ff0000';
        btn.style.color = '#fff';
        setTimeout(() => {{ btn.innerText = '🎤 Click to Speak'; btn.style.background = '#000'; btn.style.color = '#4af626'; }}, 2000);
    }};
}} else {{
    btn.innerText = '❌ Browser Not Supported';
}}
</script>
"""
st.components.v1.html(js_code, height=0)

# ================= TEXT INPUT FORM =================
with st.form(key="form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        txt = st.text_input("Command:", placeholder="Type here...", label_visibility="collapsed")
    with col2:
        sub = st.form_submit_button("🚀 Send", use_container_width=True)
    if sub and txt:
        process_cmd(txt)
        st.rerun()

# Clear TTS after speaking
if "tts" in st.session_state:
    st.session_state.tts = ""
