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
# 2. STATE MANAGEMENT
# ======================================================
if "playlist" not in st.session_state: st.session_state.playlist = None
if "current_mood" not in st.session_state: st.session_state.current_mood = "Neutral"
if "error" not in st.session_state: st.session_state.error = None

# ======================================================
# 3. DYNAMIC CSS GENERATOR (THE VISUAL MAGIC)
# ======================================================
def get_dynamic_css(mood):
    # Default Gradient (Dark/Neutral)
    gradient = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    
    # Dynamic Mood Themes
    if "Energetic" in mood or "Happy" in mood:
        gradient = "linear-gradient(135deg, #fce38a, #f38181)" # Warm Orange/Pink
    elif "Melancholy" in mood or "Sad" in mood:
        gradient = "linear-gradient(135deg, #2b5876, #4e4376)" # Deep Blue/Purple
    elif "Chill" in mood or "Relaxed" in mood:
        gradient = "linear-gradient(135deg, #134e5e, #71b280)" # Teal/Green
    elif "Heartbroken" in mood:
        gradient = "linear-gradient(135deg, #4b1248, #f0c27b)" # Dark Red/Gold
    elif "Dreamy" in mood:
        gradient = "linear-gradient(135deg, #c33764, #1d2671)" # Pink/Deep Blue

    return f"""
    <style>
    /* 1. DYNAMIC BACKGROUND */
    .stApp {{
        background-image: {gradient};
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        background-attachment: fixed;
    }}
    
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* 2. ANIMATED TITLE */
    .big-title {{
        font-size: 90px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to right, #ffffff, #00d2ff, #ffffff);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: shine 3s linear infinite;
        margin-bottom: 10px;
        text-shadow: 0px 0px 20px rgba(0,210,255,0.3);
    }}
    
    @keyframes shine {{
        to {{ background-position: 200% center; }}
    }}
    
    .subtitle {{
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 20px;
        margin-bottom: 40px;
        font-weight: 300;
    }}

    /* 3. GLASSMORPHISM CARDS */
    .song-card {{
        background: rgba(255, 255, 255, 0.15); /* Semi-transparent white */
        backdrop-filter: blur(12px);            /* The Frost Effect */
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: white;
    }}
    
    .song-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        background: rgba(255, 255, 255, 0.25);
    }}

    .album-art {{
        width: 70px;
        height: 70px;
        background: rgba(0,0,0,0.2);
        border-radius: 12px;
        margin-right: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 35px;
    }}

    /* TEXT STYLES */
    .song-title {{ font-size: 20px; font-weight: 800; color: white; margin-bottom: 4px; }}
    .song-artist {{ font-size: 15px; color: rgba(255,255,255,0.8); }}
    
    /* BUTTON STYLES */
    .listen-btn {{
        background: white;
        color: #333;
        padding: 8px 24px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.2s;
        border: none;
    }}
    .listen-btn:hover {{
        background: #00d2ff;
        color: white;
        box-shadow: 0 0 15px #00d2ff;
    }}
    
    /* REMOVE DEFAULT STREAMLIT PADDING */
    #MainMenu, footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 2rem; }}
    </style>
    """

# Apply the CSS based on current state
st.markdown(get_dynamic_css(st.session_state.current_mood), unsafe_allow_html=True)

# ======================================================
# 4. ROBUST AI LOGIC (Auto-Discovery)
# ======================================================
# 1. Get Key
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif os.environ.get("GOOGLE_API_KEY"):
    api_key = os.environ.get("GOOGLE_API_KEY")
else:
    api_key = None

# 2. Find Working Model
def get_valid_model(key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for model in data.get('models', []):
                if 'generateContent' in model.get('supportedGenerationMethods', []) and 'gemini' in model.get('name'):
                    return model.get('name')
        return "models/gemini-pro" # Fallback
    except:
        return "models/gemini-pro"

# 3. Generate Music
def get_vibe_playlist(mood_text):
    if not api_key: return "⚠️ API Key Missing. Check .streamlit/secrets.toml"
    
    model_name = get_valid_model(api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    
    prompt = (
        f"Recommend 5 songs for mood: '{mood_text}'. "
        "Return ONLY a JSON array. "
        "Format: [{'title': 'Song', 'artist': 'Artist', 'desc': 'Short reason'}]. "
        "NO markdown."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            clean_text = text.replace("```json", "").replace("```", "").strip()
            match = re.search(r"\[.*\]", clean_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                for song in data:
                    q = urllib.parse.quote_plus(f"{song.get('title')} {song.get('artist')}")
                    song['link'] = f"https://www.youtube.com/results?search_query={q}"
                return data
        elif response.status_code == 429:
            return "Quota Limit Reached. Please try again later."
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# ======================================================
# 5. SIDEBAR (Enhanced)
# ======================================================
with st.sidebar:
    st.title("🎧 Control Center")
    
    # 1. Brief Description
    st.markdown("""
    **VibeChecker** is your intelligent music companion. 
    It uses Google's Gemini AI to analyze your emotions and curate 
    the perfect playlist instantly.
    """)
    
    st.write("---")

    # 2. "How It Works" Expander
    with st.expander("ℹ️ How it works"):
        st.write("""
        1. **Select a Mood:** Choose a preset or type your own.
        2. **AI Analysis:** Gemini scans millions of tracks to match your feeling.
        3. **Listen:** Get instant YouTube links for 5 curated songs.
        """)
    
    st.write("---")
    
    # 3. Controls
    if st.button("🎲 Surprise Me"):
        vibe = random.choice(["Energetic", "Chill", "Melancholy", "Dreamy", "Hyped"])
        st.session_state.current_mood = vibe
        with st.spinner(f"Curating {vibe} vibes..."):
            res = get_vibe_playlist(vibe)
            if isinstance(res, list): st.session_state.playlist = res
            else: st.session_state.error = res
        st.rerun()

    if st.button("🔄 Reset App"):
        st.session_state.playlist = None
        st.session_state.current_mood = "Neutral"
        st.session_state.error = None
        st.rerun()

# ======================================================
# 6. MAIN UI
# ======================================================
# Big Animated Title
st.markdown('<div class="big-title">VibeChecker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Mood Curation</div>', unsafe_allow_html=True)

# Mood Buttons
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

clicked_mood = None
if b1: clicked_mood = "Energetic"
if b2: clicked_mood = "Melancholy"
if b3: clicked_mood = "Chill"
if b4: clicked_mood = "Heartbroken"

# Handle Button Click
if clicked_mood:
    st.session_state.current_mood = clicked_mood
    with st.spinner(f"Connecting to the VibeStream ({clicked_mood})..."):
        res = get_vibe_playlist(clicked_mood)
        if isinstance(res, list): st.session_state.playlist = res
        else: st.session_state.error = res
    st.rerun()

# Input Bar
with st.form("mood_form"):
    user_input = st.text_input("", placeholder="Or describe your exact vibe here...")
    submitted = st.form_submit_button("Analyze My Vibe ✨")

if submitted and user_input:
    st.session_state.current_mood = user_input
    with st.spinner("Analyzing emotional frequencies..."):
        res = get_vibe_playlist(user_input)
        if isinstance(res, list): st.session_state.playlist = res
        else: st.session_state.error = res
    st.rerun()

# ======================================================
# 7. OUTPUT AREA (Glassmorphism Cards)
# ======================================================
if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.playlist:
    st.markdown(f"### 🎶 Selected for: **{st.session_state.current_mood}**")
    
    emojis = ["🎵", "🎸", "🎧", "🎹", "🎷", "💿"]
    
    for song in st.session_state.playlist:
        st.markdown(
            f"""
            <div class="song-card">
                <div class="album-art">{random.choice(emojis)}</div>
                <div style="flex-grow:1;">
                    <div class="song-title">{song.get('title')}</div>
                    <div class="song-artist">{song.get('artist')}</div>
                    <div style="font-size:12px; opacity:0.7;">{song.get('desc','')}</div>
                </div>
                <a class="listen-btn" href="{song.get('link')}" target="_blank">▶ Play</a>
            </div>
            """,
            unsafe_allow_html=True
        )

