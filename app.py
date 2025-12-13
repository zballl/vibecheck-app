import streamlit as st
import requests
import json
import base64
import random
import re
import os

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
# 3. CUSTOM CSS
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

.song-card {
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
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

.song-title { font-size: 18px; font-weight: 800; }
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
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is missing. Please set it in .streamlit/secrets.toml or environment variables.")
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

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-1.5-flash:generateContent?key={api_key}"
    )

    prompt = (
        "The user will give a mood. "
        "It can be a single word (sad, chill, melancholy) "
        "or a short sentence.\n\n"
        f"User mood: '{mood_text}'\n\n"
        "Recommend 5 songs that match this mood.\n\n"
        "Return ONLY valid JSON.\n"
        "Output a JSON array of exactly 5 objects.\n"
        "Each object must include: title, artist, link.\n"
        "No explanations or markdown."
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=payload)

    if response.status_code == 429:
        return "Too many requests. Please wait a few seconds."
    if response.status_code != 200:
        return f"API Error {response.status_code}: {response.text}"

    try:
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return f"Unexpected API response: {response.json()}"

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        match = re.search(r"

\[.*\]

", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return "Invalid AI response"

# ======================================================
# 7. SIDEBAR
# ======================================================
SURPRISE_MOODS = [
    "sad",
    "chill",
    "melancholy",
    "peaceful night vibes",
    "heartbroken but healing",
    "energetic motivation"
]

with st.sidebar:
    st.title("🎧 VibeChecker")
    st.info("VibeChecker AI")

    if st.button("🎲 Surprise Me"):
        mood = random.choice(SURPRISE_MOODS)
        st.session_state.current_mood = mood
        st.session_state.error = None

        with st.spinner("Surprising your vibe..."):
            result = get_vibe_check(mood)
            st.session_state.playlist = result if isinstance(result, list) else None
            st.session_state.error = None if isinstance(result, list) else result

    if st.button("🔄 Reset"):
        st.session_state.playlist = None
        st.session_state.error = None
        st.session_state.current_mood = None

# ======================================================
# 8. MAIN UI
# ======================================================
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center; max-width:800px; margin:auto; color:#dddddd;">
        <p style="font-size:18px;">
            <strong>VibeChecker</strong> is an AI-powered music recommendation system
            that suggests songs based on your current mood.
        </p>
        <p style="font-size:16px;">
            Simply type how you feel and VibeChecker will curate a playlist
            that matches your vibe.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

user_input = st.text_input(
    "Type your mood (e.g. sad, chill, melancholy, calm night vibes)"
)

if st.button("Analyze My Mood 🎶") and user_input.strip():
    st.session_state.current_mood = user_input.strip()
    st.session_state.error = None

    with st.spinner("Curating your vibe..."):
        result = get_vibe_check(user_input)
        st.session_state.playlist = result if isinstance(result, list) else None
        st.session_state.error = None if isinstance(result, list) else result

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
                <div>
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
