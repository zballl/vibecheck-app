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
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

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
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# 3. CUSTOM CSS
# ======================================================
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.title-text {
    font-size: 70px; font-weight: 900; text-align: center;
    background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.song-card {
    background: white; border-radius: 12px; padding: 15px; margin-bottom: 15px;
    display: flex; align-items: center; color: #333;
}
.album-art {
    width: 60px; height: 60px; background: #f0f2f6; border-radius: 8px;
    margin-right: 15px; display: flex; align-items: center; justify-content: center; font-size: 30px;
}
.song-title { font-size: 18px; font-weight: 800; color: #000; }
.song-artist { font-size: 14px; color: #555; }
.listen-btn {
    border: 2px solid #00d2ff; color: #00d2ff; padding: 6px 16px;
    border-radius: 20px; text-decoration: none; font-weight: bold;
}
.listen-btn:hover { background: #00d2ff; color: white; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 4. API KEY & SESSION
# ======================================================
# Try to load key from secrets or environment
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif os.environ.get("GOOGLE_API_KEY"):
    api_key = os.environ.get("GOOGLE_API_KEY")
else:
    api_key = None

# Initialize Session State
if "playlist" not in st.session_state: st.session_state.playlist = None
if "current_mood" not in st.session_state: st.session_state.current_mood = ""
if "error" not in st.session_state: st.session_state.error = None

# ======================================================
# 5. INTELLIGENT AI CONNECTOR (The 404 Fix)
# ======================================================
def get_vibe_check(mood_text):
    if not api_key:
        return "⚠️ API Key Missing! Check .streamlit/secrets.toml"
        
    mood_text = mood_text.strip().lower()[:120]
    
    # LIST OF MODELS TO TRY (If one fails, it tries the next)
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-pro"
    ]

    prompt = (
        f"Recommend 5 songs for mood: '{mood_text}'. "
        "Return ONLY a JSON array. "
        "Each object must have 'title' and 'artist'. "
        "NO markdown."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    # Try each model until one works
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                # SUCCESS! Parse data
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                clean_text = text.replace("```json", "").replace("```", "").strip()
                match = re.search(r"\[.*\]", clean_text, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    # Add YouTube Links
                    for song in data:
                        query = f"{song.get('title')} {song.get('artist')}"
                        safe_query = urllib.parse.quote_plus(query)
                        song['link'] = f"https://www.youtube.com/results?search_query={safe_query}"
                    return data
            
            # If 404, loop will just try the next model
            
        except:
            continue
            
    return "Error: Could not connect. Please check your internet or API Key."

# ======================================================
# 6. SIDEBAR (DEBUGGER)
# ======================================================
with st.sidebar:
    st.title("🎧 Control Panel")
    
    # KEY CHECKER: This helps you see if the wrong key is loaded
    if api_key:
        masked = f"{api_key[:5]}...{api_key[-5:]}"
        st.caption(f"🔑 Key Loaded: {masked}")
        if api_key.startswith("AIzaSyCk"):
            st.error("⚠️ You are using the MAPS Key! Change it in secrets.toml")
        elif api_key.startswith("AIzaSyB6"):
            st.success("✅ Correct Key Loaded")
    else:
        st.error("❌ No Key Found")

    if st.button("🎲 Surprise Me"):
        mood = random.choice(["Chill", "Energetic", "Melancholy", "Focus"])
        st.session_state.current_mood = mood
        with st.spinner(f"Curating {mood}..."):
            res = get_vibe_check(mood)
            if isinstance(res, list): st.session_state.playlist = res
            else: st.session_state.error = res
        st.rerun()

    if st.button("🔄 Reset"):
        st.session_state.playlist = None
        st.session_state.current_mood = ""
        st.session_state.error = None
        st.rerun()

# ======================================================
# 7. MAIN UI
# ======================================================
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

# INPUT FORM (Pressing Enter works now!)
with st.form("mood_form"):
    user_input = st.text_input("How are you feeling?", placeholder="Type 'Happy', 'Sad', etc. and press Enter")
    submitted = st.form_submit_button("Analyze Mood 🎶")

if submitted and user_input:
    st.session_state.current_mood = user_input
    with st.spinner("Analyzing..."):
        res = get_vibe_check(user_input)
        if isinstance(res, list):
            st.session_state.playlist = res
            st.session_state.error = None
        else:
            st.session_state.error = res
            st.session_state.playlist = None
    st.rerun()

# RESULTS
if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.playlist:
    st.markdown(f"### 🎶 Recommended for: **{st.session_state.current_mood}**")
    emojis = ["🎵", "🎸", "🎧", "🎹", "🎷"]
    
    for song in st.session_state.playlist:
        st.markdown(
            f"""
            <div class="song-card">
                <div class="album-art">{random.choice(emojis)}</div>
                <div style="flex-grow:1;">
                    <div class="song-title">{song.get("title")}</div>
                    <div class="song-artist">{song.get("artist")}</div>
                </div>
                <a class="listen-btn" href="{song.get("link")}" target="_blank">▶ Listen</a>
            </div>
            """,
            unsafe_allow_html=True
        )
