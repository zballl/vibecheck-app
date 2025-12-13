import streamlit as st
import requests
import json
import base64
import random
import re
import os
import urllib.parse  # Added to help make valid YouTube links

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
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)),
                url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown("<style>.stApp { background-color: #0E1117; }</style>",
                unsafe_allow_html=True)

# ======================================================
# 3. CUSTOM CSS (FIXED VISIBILITY)
# ======================================================
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}

.title-text {
    font-size: 70px;
    font-weight: 900;
    text-align: center;
    background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Added color: #333 to force black text on white cards */
.song-card {
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    color: #333 !important; 
}

.album-art {
    width: 60px;
    height: 60px;
    background: #f0f2f6;
    border-radius: 8px;
    margin-right: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
}

/* Force specific colors for text */
.song-title { font-size: 18px; font-weight: 800; color: #000; }
.song-artist { font-size: 14px; color: #555; }

.listen-btn {
    border: 2px solid #00d2ff;
    color: #00d2ff;
    padding: 6px 16px;
    border-radius: 20px;
    text-decoration: none;
    font-weight: bold;
}
.listen-btn:hover { background: #00d2ff; color: white; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 4. API KEY
# ======================================================
# Check secrets first, then environment
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif os.environ.get("GOOGLE_API_KEY"):
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is missing. Please add it to .streamlit/secrets.toml")
    st.stop()

# ======================================================
# 5. SESSION STATE
# ======================================================
for key in ["playlist", "error", "current_mood"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ======================================================
# 6. AI FUNCTION
# ======================================================
def get_vibe_check(mood_text):
    mood_text = mood_text.strip().lower()[:120]

    # Trying the most reliable free model endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    prompt = (
        f"User mood: '{mood_text}'\n"
        "Recommend 5 songs.\n"
        "Return ONLY valid JSON array.\n"
        "Each object must have keys: 'title', 'artist'.\n"
        "DO NOT invent links. Just title and artist."
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            # Fallback to Pro if Flash fails (Fail-safe)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            response = requests.post(url, json=payload)

        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Clean up json format
            clean_text = text.replace("```json", "").replace("```", "").strip()
            # Regex to find the list [...]
            match = re.search(r"\[.*\]", clean_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                # AUTOMATICALLY BUILD YOUTUBE LINKS HERE
                for song in data:
                    query = f"{song.get('title')} {song.get('artist')}"
                    # Converts "Song Name" to "Song+Name" for URL
                    safe_query = urllib.parse.quote_plus(query)
                    song['link'] = f"https://www.youtube.com/results?search_query={safe_query}"
                return data
                
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# ======================================================
# 7. SIDEBAR
# ======================================================
SURPRISE_MOODS = ["sad", "chill", "melancholy", "energetic", "focus"]

with st.sidebar:
    st.title("🎧 VibeChecker")
    st.info("VibeChecker AI")

    if st.button("🎲 Surprise Me"):
        mood = random.choice(SURPRISE_MOODS)
        st.session_state.current_mood = mood
        st.session_state.error = None

        with st.spinner(f"Curating {mood}..."):
            result = get_vibe_check(mood)
            st.session_state.playlist = result if isinstance(result, list) else None
            st.session_state.error = None if isinstance(result, list) else result
        st.rerun()

    if st.button("🔄 Reset"):
        st.session_state.playlist = None
        st.session_state.error = None
        st.session_state.current_mood = None
        st.rerun()

# ======================================================
# 8. MAIN UI
# ======================================================
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center; max-width:800px; margin:auto; color:#dddddd;">
        <p style="font-size:18px;">
            <strong>VibeChecker</strong> is an AI-powered music recommendation system.
        </p>
    </div>
    <br>
    """,
    unsafe_allow_html=True
)

# --- FORM FIX: This makes "Enter" key work! ---
with st.form(key='mood_form'):
    user_input = st.text_input("Type your mood (e.g. sad, chill, melancholy)", 
                               placeholder="Type here and press Enter...")
    submit_button = st.form_submit_button("Analyze My Mood 🎶")

if submit_button and user_input:
    st.session_state.current_mood = user_input.strip()
    st.session_state.error = None

    with st.spinner("Curating your vibe..."):
        result = get_vibe_check(user_input)
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error = result
            st.session_state.playlist = None
    st.rerun()

# ======================================================
# 9. OUTPUT
# ======================================================
if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.playlist:
    st.markdown(f"### 🎶 Recommended for {st.session_state.current_mood}")
    emojis = ["🎵", "🎸", "🎧", "🎹", "🎷"]

    for song in st.session_state.playlist:
        st.markdown(
            f"""
            <div class="song-card">
                <div class="album-art">{random.choice(emojis)}</div>
                <div style="flex-grow:1;">
                    <div class="song-title">{song.get("title","Track")}</div>
                    <div class="song-artist">{song.get("artist","Artist")}</div>
                </div>
                <a class="listen-btn" href="{song.get("link","#")}" target="_blank">
                    ▶️ Listen
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
