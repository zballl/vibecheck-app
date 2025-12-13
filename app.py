import streamlit as st
import requests
import json
import base64
import random
import re
import os
import urllib.parse
import ast

# ======================================================
# 1. PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="VibeChecker", 
    page_icon="🎵", 
    layout="wide"
)

# ======================================================
# 2. BACKGROUND IMAGE
# ======================================================
def get_base64_of_bin_file(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

img_base64 = get_base64_of_bin_file("background.jpeg")

if img_base64:
    bg_style = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
else:
    bg_style = "<style>.stApp { background-color: #0E1117; }</style>"

st.markdown(bg_style, unsafe_allow_html=True)

# ======================================================
# 3. CSS STYLING
# ======================================================
st.markdown("""
<style>
/* Animated Title */
.big-title {
    font-size: 80px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(to right, #ffffff, #00d2ff, #ffffff);
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    animation: shine 3s linear infinite;
    text-shadow: 0px 0px 30px rgba(0,210,255,0.4);
}
@keyframes shine { to { background-position: 200% center; } }

.subtitle { text-align: center; color: rgba(255,255,255,0.8); margin-bottom: 40px; font-weight: 300; letter-spacing: 1px; }

/* Glassmorphism Cards */
.song-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    color: white;
    transition: transform 0.2s;
}
.song-card:hover { transform: translateY(-3px); background: rgba(255,255,255,0.2); }

.album-art { font-size: 30px; margin-right: 20px; width: 60px; text-align: center; }

.listen-btn {
    background: white; color: #333; padding: 8px 20px;
    border-radius: 20px; text-decoration: none; font-weight: bold;
}
.listen-btn:hover { background: #00d2ff; color: white; }

/* Hide Streamlit Elements */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 4. ROBUST API LOGIC (Vision-Proof)
# ======================================================
if "playlist" not in st.session_state: st.session_state.playlist = None
if "current_mood" not in st.session_state: st.session_state.current_mood = "Neutral"
if "error" not in st.session_state: st.session_state.error = None
if "show_quiz" not in st.session_state: st.session_state.show_quiz = False

# Get Key
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif os.environ.get("GOOGLE_API_KEY"):
    api_key = os.environ.get("GOOGLE_API_KEY")
else:
    api_key = None

def get_valid_model(key):
    """
    Finds a TEXT model. Explicitly avoids VISION models to prevent 400 Errors.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            # 1. First choice: Gemini 1.5 Flash (Fast, Free, Text)
            for m in models:
                name = m.get('name')
                if 'flash' in name and 'vision' not in name: return name
            
            # 2. Second choice: Gemini Pro (Standard Text)
            for m in models:
                name = m.get('name')
                if 'pro' in name and 'vision' not in name: return name
                    
            # 3. Last Resort: Any Gemini that is NOT vision
            for m in models:
                name = m.get('name')
                if 'gemini' in name and 'vision' not in name: return name

        return "models/gemini-pro"
    except:
        return "models/gemini-pro"

def get_vibe_playlist(mood_text):
    if not api_key: return "⚠️ API Key Missing."
    
    model_name = get_valid_model(api_key)
    # Double check: Ensure we didn't accidentally grab a vision model
    if 'vision' in model_name:
        model_name = "models/gemini-pro"

    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    
    # Use DOUBLE QUOTES in the example to prevent JSON errors
    prompt = (
        f"Recommend 5 songs for mood: '{mood_text}'. "
        "Return ONLY a JSON array. "
        "Format: [{\"title\": \"Song Name\", \"artist\": \"Artist Name\", \"desc\": \"Short reason\"}]. "
        "NO markdown."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            clean_text = text.replace("```json", "").replace("```", "").strip()
            match = re.search(r"\[.*\]", clean_text, re.DOTALL)
            if match: clean_text = match.group(0)
            
            # Robust Parsing (JSON -> AST Backup)
            try:
                data = json.loads(clean_text)
            except:
                try:
                    data = ast.literal_eval(clean_text)
                except:
                    return "AI Error: Could not read data."

            if isinstance(data, list):
                for song in data:
                    q = urllib.parse.quote_plus(f"{song.get('title')} {song.get('artist')}")
                    song['link'] = f"https://www.youtube.com/results?search_query={q}"
                return data
            return "AI Error: Not a list."

        elif response.status_code == 400:
            return f"Error 400: Bad Request. (Model: {model_name})"
        elif response.status_code == 429:
            return "Quota Limit Reached. Try later."
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Connection Error: {str(e)}"

# ======================================================
# 5. SIDEBAR (RESTORED INFO)
# ======================================================
with st.sidebar:
    st.title("🎧 Control Center")
    
    st.markdown("""
    **VibeChecker** detects your mood and curates the perfect playlist using AI.
    """)
    
    st.write("---")

    # Expander for cleaner UI
    with st.expander("ℹ️ How it works"):
        st.write("""
        1. **Mood Input:** Type how you feel or pick a preset.
        2. **AI Processing:** We analyze emotional context.
        3. **Curation:** You get 5 perfect songs with direct links.
        """)
    
    st.write("---")
    
    if st.button("🎲 Surprise Me"):
        vibe = random.choice(["Energetic", "Chill", "Dreamy", "Focus", "Melancholy"])
        st.session_state.current_mood = vibe
        st.session_state.show_quiz = False
        with st.spinner(f"Curating {vibe}..."):
            res = get_vibe_playlist(vibe)
            if isinstance(res, list): st.session_state.playlist = res
            else: st.session_state.error = res
        st.rerun()
        
    if st.button("🔄 Reset App"):
        st.session_state.playlist = None
        st.session_state.error = None
        st.session_state.show_quiz = False
        st.session_state.current_mood = "Neutral"
        st.rerun()

# ======================================================
# 6. MAIN UI
# ======================================================
st.markdown('<div class="big-title">VibeChecker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Mood Curation</div>', unsafe_allow_html=True)

# Mood Buttons
c1, c2, c3, c4 = st.columns(4)
if c1.button("⚡ Energetic"): 
    st.session_state.current_mood = "Energetic"
    st.session_state.show_quiz = False
    with st.spinner("Curating..."):
        res = get_vibe_playlist("Energetic")
        if isinstance(res, list): st.session_state.playlist = res
        else: st.session_state.error = res
    st.rerun()

if c2.button("☂️ Melancholy"): 
    st.session_state.current_mood = "Melancholy"
    st.session_state.show_quiz = False
    with st.spinner("Curating..."):
        res = get_vibe_playlist("Melancholy")
        if isinstance(res, list): st.session_state.playlist = res
        else: st.session_state.error = res
    st.rerun()
    
if c3.button("🧘 Chill"): 
    st.session_state.current_mood = "Chill"
    st.session_state.show_quiz = False
    with st.spinner("Curating..."):
        res = get_vibe_playlist("Chill")
        if isinstance(res, list): st.session_state.playlist = res
        else: st.session_state.error = res
    st.rerun()
    
if c4.button("💔 Heartbroken"): 
    st.session_state.current_mood = "Heartbroken"
    st.session_state.show_quiz = False
    with st.spinner("Curating..."):
        res = get_vibe_playlist("Heartbroken")
        if isinstance(res, list): st.session_state.playlist = res
        else: st.session_state.error = res
    st.rerun()

# Quiz Toggle
if st.button("🤔 Not sure? Help me decide"):
    st.session_state.show_quiz = not st.session_state.show_quiz
    st.session_state.playlist = None 

# INPUTS (Quiz vs Text)
final_query = None
if st.session_state.show_quiz:
    st.markdown("### 📝 Answer these 3 questions:")
    with st.form("quiz"):
        c1, c2, c3 = st.columns(3)
        q1 = c1.selectbox("Energy", ["High", "Low", "Neutral"])
        q2 = c2.selectbox("Social", ["Social", "Alone", "Need Comfort"])
        q3 = c3.selectbox("Emotion", ["Happy", "Sad", "Calm", "Anxious"])
        if st.form_submit_button("Analyze"):
            final_query = f"Energy: {q1}, Social: {q2}, Emotion: {q3}"
            st.session_state.current_mood = f"{q3} & {q1}"
            st.session_state.show_quiz = False
else:
    with st.form("text"):
        txt = st.text_input("", placeholder="Or describe your exact vibe...")
        if st.form_submit_button("Analyze"):
            final_query = txt
            st.session_state.current_mood = txt

if final_query:
    with st.spinner("Analyzing..."):
        res = get_vibe_playlist(final_query)
        if isinstance(res, list): 
            st.session_state.playlist = res
            st.session_state.error = None
        else: 
            st.session_state.error = res
    st.rerun()

# RESULTS
if st.session_state.error: st.error(st.session_state.error)
if st.session_state.playlist:
    st.markdown(f"### 🎶 Playlist for: {st.session_state.current_mood}")
    emojis = ["🎵", "🎸", "🎧", "🎹", "🎷"]
    for song in st.session_state.playlist:
        st.markdown(f"""
        <div class="song-card">
            <div class="album-art">{random.choice(emojis)}</div>
            <div style="flex-grow:1;">
                <div style="font-weight:bold; font-size:20px;">{song.get('title')}</div>
                <div>{song.get('artist')}</div>
                <div style="font-size:12px; opacity:0.8;">{song.get('desc')}</div>
            </div>
            <a class="listen-btn" href="{song.get('link')}" target="_blank">▶ Play</a>
        </div>
        """, unsafe_allow_html=True)
