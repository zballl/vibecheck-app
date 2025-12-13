import streamlit as st
import requests
import json
import base64
import random
import re
import os
import urllib.parse

# ======================================================
# 1. PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="VibeChecker", 
    page_icon="🎵", 
    layout="wide"
)

# ======================================================
# 2. LOAD EXISTING BACKGROUND IMAGE
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
# 3. ADVANCED STYLING (Glassmorphism & Animation)
# ======================================================
st.markdown("""
<style>
/* 1. ANIMATED HUGE TITLE */
.big-title {
    font-size: 90px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(to right, #ffffff, #00d2ff, #ffffff);
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    animation: shine 3s linear infinite;
    margin-bottom: 5px;
    text-shadow: 0px 0px 30px rgba(0,210,255,0.4);
}

@keyframes shine {
    to { background-position: 200% center; }
}

.subtitle {
    text-align: center;
    color: rgba(255, 255, 255, 0.85);
    font-size: 22px;
    margin-bottom: 50px;
    font-weight: 300;
    letter-spacing: 1px;
}

/* 2. GLASSMORPHISM CARDS */
.song-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    color: white;
}

.song-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 40px 0 rgba(0, 0, 0, 0.5);
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
}

.album-art {
    width: 75px;
    height: 75px;
    background: rgba(0,0,0,0.3);
    border-radius: 15px;
    margin-right: 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 35px;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
}

/* TEXT STYLES */
.song-title { font-size: 22px; font-weight: 800; color: white; margin-bottom: 4px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
.song-artist { font-size: 16px; color: rgba(255,255,255,0.9); font-weight: 500; }
.song-desc { font-size: 13px; color: rgba(255,255,255,0.6); margin-top: 5px; font-style: italic; }

/* 3. BUTTON STYLES */
.listen-btn {
    background: white;
    color: #333;
    padding: 10px 25px;
    border-radius: 30px;
    text-decoration: none;
    font-weight: 800;
    transition: all 0.2s;
    border: none;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.listen-btn:hover {
    background: #00d2ff;
    color: white;
    box-shadow: 0 0 20px #00d2ff;
    transform: translateY(-2px);
}

/* HIDE STREAMLIT ELEMENTS */
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 4. STATE & API LOGIC
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

# Find Model
def get_valid_model(key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for model in data.get('models', []):
                if 'generateContent' in model.get('supportedGenerationMethods', []) and 'gemini' in model.get('name'):
                    return model.get('name')
        return "models/gemini-pro"
    except:
        return "models/gemini-pro"

# Generate Playlist
def get_vibe_playlist(mood_text):
    if not api_key: return "⚠️ API Key Missing. Check .streamlit/secrets.toml"
    
    model_name = get_valid_model(api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    
    prompt = (
        f"Recommend 5 songs for mood: '{mood_text}'. "
        "Return ONLY a JSON array. "
        "Format: [{'title': 'Song', 'artist': 'Artist', 'desc': 'Very short reason (5 words)'}]. "
        "NO markdown."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            # --- JSON REPAIR ENGINE ---
            # 1. Remove markdown backticks
            clean_text = text.replace("```json", "").replace("```", "").strip()
            
            # 2. Extract only the list part [ ... ]
            match = re.search(r"\[.*\]", clean_text, re.DOTALL)
            if match:
                clean_text = match.group(0)
            
            # 3. Parse JSON
            try:
                data = json.loads(clean_text)
                for song in data:
                    q = urllib.parse.quote_plus(f"{song.get('title')} {song.get('artist')}")
                    song['link'] = f"https://www.youtube.com/results?search_query={q}"
                return data
            except json.JSONDecodeError as e:
                return f"AI Error: Invalid JSON Format ({str(e)})"
                
        elif response.status_code == 429:
            return "Quota Limit Reached. Please try again later."
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# ======================================================
# 5. SIDEBAR
# ======================================================
with st.sidebar:
    st.title("🎧 Control Center")
    
    st.markdown("""
    **VibeChecker** detects your mood and curates the perfect playlist using advanced AI.
    """)
    
    st.write("---")

    with st.expander("ℹ️ How it works"):
        st.write("""
        1. **Mood Input:** Type how you feel or pick a preset.
        2. **AI Processing:** We analyze emotional context.
        3. **Curation:** You get 5 perfect songs with direct links.
        """)
    
    st.write("---")
    
    if st.button("🎲 Surprise Me"):
        vibe = random.choice(["Energetic", "Chill", "Melancholy", "Dreamy", "Hyped", "Focus"])
        st.session_state.current_mood = vibe
        st.session_state.show_quiz = False
        with st.spinner(f"Curating {vibe} vibes..."):
            res = get_vibe_playlist(vibe)
            if isinstance(res, list): st.session_state.playlist = res
            else: st.session_state.error = res
        st.rerun()

    if st.button("🔄 Reset App"):
        st.session_state.playlist = None
        st.session_state.current_mood = "Neutral"
        st.session_state.error = None
        st.session_state.show_quiz = False
        st.rerun()

# ======================================================
# 6. MAIN UI
# ======================================================
st.markdown('<div class="big-title">VibeChecker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Mood Curation</div>', unsafe_allow_html=True)

# Mood Buttons
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

# Logic: Buttons
clicked_mood = None
if b1: clicked_mood = "Energetic"
if b2: clicked_mood = "Melancholy"
if b3: clicked_mood = "Chill"
if b4: clicked_mood = "Heartbroken"

if clicked_mood:
    st.session_state.current_mood = clicked_mood
    st.session_state.show_quiz = False
    with st.spinner(f"Connecting to the VibeStream ({clicked_mood})..."):
        res = get_vibe_playlist(clicked_mood)
        if isinstance(res, list): st.session_state.playlist = res
        else: st.session_state.error = res
    st.rerun()

# Logic: Quiz Toggle
if st.button("🤔 Not sure? Help me decide"):
    st.session_state.show_quiz = not st.session_state.show_quiz
    st.session_state.playlist = None 

# ------------------------------------------------------
# INPUT SECTION (Quiz vs Text)
# ------------------------------------------------------
final_mood_query = None

if st.session_state.show_quiz:
    st.markdown("### 📝 Answer these 3 questions:")
    with st.form("quiz_form"):
        c_q1, c_q2, c_q3 = st.columns(3)
        q1 = c_q1.selectbox("Current Energy?", ["High Energy", "Low Energy", "Neutral"])
        q2 = c_q2.selectbox("Social Battery?", ["Party Mode", "Leave me alone", "Need comfort"])
        q3 = c_q3.selectbox("Emotional Tone?", ["Happy", "Sad", "Angry", "Calm", "Anxious"])
        
        submitted_quiz = st.form_submit_button("Analyze My Answers ✨")
    
    if submitted_quiz:
        final_mood_query = f"User has {q1}, feels {q2}, and is emotionally {q3}"
        st.session_state.current_mood = f"{q3} & {q1}" 
        st.session_state.show_quiz = False

else:
    with st.form("mood_form"):
        user_input = st.text_input("", placeholder="Or describe your exact vibe here...")
        submitted_text = st.form_submit_button("Analyze My Vibe ✨")
    
    if submitted_text and user_input:
        final_mood_query = user_input
        st.session_state.current_mood = user_input

# ------------------------------------------------------
# EXECUTE SEARCH
# ------------------------------------------------------
if final_mood_query:
    with st.spinner("Analyzing emotional frequencies..."):
        res = get_vibe_playlist(final_mood_query)
        if isinstance(res, list): 
            st.session_state.playlist = res
            st.session_state.error = None
        else: 
            st.session_state.error = res
    st.rerun()

# ======================================================
# 7. OUTPUT AREA
# ======================================================
if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.playlist:
    st.markdown(f"### 🎶 Selected for: **{st.session_state.current_mood}**")
    
    emojis = ["🎵", "🎸", "🎧", "🎹", "🎷", "💿", "🎤", "🎻"]
    
    for song in st.session_state.playlist:
        st.markdown(
            f"""
            <div class="song-card">
                <div class="album-art">{random.choice(emojis)}</div>
                <div style="flex-grow:1;">
                    <div class="song-title">{song.get('title')}</div>
                    <div class="song-artist">{song.get('artist')}</div>
                    <div class="song-desc">{song.get('desc','')}</div>
                </div>
                <a class="listen-btn" href="{song.get('link')}" target="_blank">▶ Play</a>
            </div>
            """,
            unsafe_allow_html=True
        )
