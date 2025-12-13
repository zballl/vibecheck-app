import streamlit as st
import requests
import json
import base64
import random

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# --- 2. IMAGE LOADER ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# --- 3. CUSTOM CSS ---
img_base64 = get_base64_of_bin_file("background.jpeg")
if img_base64:
    background_style = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """
else:
    background_style = "<style>.stApp { background-color: #0E1117; }</style>"

st.markdown(background_style, unsafe_allow_html=True)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .title-text {
        font-size: 70px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
    }
    
    .song-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .song-card:hover { transform: scale(1.01); }
    
    .album-art {
        width: 80px;
        height: 80px;
        background-color: #f0f2f6;
        border-radius: 8px;
        margin-right: 20px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px; 
    }
    
    .song-info { flex-grow: 1; color: #333; }
    .song-title { font-size: 20px; font-weight: 800; margin: 0; color: #000; }
    .song-artist { font-size: 16px; color: #666; margin: 5px 0 0 0; }
    
    .listen-btn {
        background-color: white;
        color: #00d2ff;
        border: 2px solid #00d2ff;
        padding: 8px 20px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        white-space: nowrap;
        transition: all 0.2s;
    }
    .listen-btn:hover { background-color: #00d2ff; color: white; }
    
    .stButton button {
        width: 100%;
        height: 50px;
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #444;
        background-color: rgba(20,20,20,0.8);
        color: white;
    }
    .stButton button:hover { border-color: #00d2ff; color: #00d2ff; }
    </style>
""", unsafe_allow_html=True)

# --- 4. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing!")
    st.stop()

# --- 5. STATE MANAGEMENT ---
if "playlist" not in st.session_state:
    st.session_state.playlist = None
if "current_mood" not in st.session_state:
    st.session_state.current_mood = ""
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None

# --- 6. API FUNCTION ---
def get_vibe_check(mood):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = (
        f"Analyze user input: '{mood}'.\n"
        "RULES:\n"
        "1. IF input is gibberish/nonsense, return JSON: [{'error': 'invalid'}]\n"
        "2. IF valid mood, return JSON list of 5 songs.\n"
        "3. FOR EACH SONG, generate a YouTube Search URL.\n\n"
        "OUTPUT FORMAT (Raw JSON only):\n"
        "[{\"title\": \"Song Name\", \"artist\": \"Artist\", \"link\": \"https://www.youtube.com/results?search_query=Song+Artist\"}]"
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            text = res.json()['candidates'][0]['content']['parts'][0]['text']
            clean_json = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
    except:
        return None
    return None

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("🎧 Control Panel")
    st.markdown("### ℹ️ About VibeChecker")
    st.info("VibeChecker uses AI to curate the perfect playlist for your current mood.")
    st.write("---")
    if st.button("🔄 Reset App"):
        st.session_state.playlist = None
        st.session_state.current_mood = ""
        st.session_state.error_msg = None
        st.rerun()

# --- 8. MAIN UI ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

# BUTTONS
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

# CAPTURE CLICK
clicked_mood = None
if b1: clicked_mood = "Energetic"
if b2: clicked_mood = "Melancholy"
if b3: clicked_mood = "Chill"
if b4: clicked_mood = "Heartbroken"

st.write("")
if st.button("🤔 Not sure how I feel?"):
    clicked_mood = "Surprise me with a random mix"

# INPUT BAR
user_input = st.text_input("", placeholder="Or type your exact mood here...")

# DETERMINE FINAL MOOD
final_mood = None

# Priority: Button Click > Text Input
if clicked_mood:
    final_mood = clicked_mood
elif user_input and user_input != st.session_state.current_mood:
    final_mood = user_input

# --- 9. LOGIC EXECUTION ---
if final_mood:
    st.session_state.current_mood = final_mood
    st.session_state.error_msg = None
    st.session_state.playlist = None  # Clear old results while loading

    with st.spinner(f"Curating tracks for {final_mood}..."):
        data = get_vibe_check(final_mood)
        
        if not data:
             st.session_state.error_msg = "⚠️ Connection Error. Try again."
        elif isinstance(data, list) and len(data) > 0 and "error" in data[0]:
             st.session_state.error_msg = "🚫 That doesn't look like a real emotion! Please try again."
        else:
             st.session_state.playlist = data

# --- 10. DISPLAY RESULTS ---
if st.session_state.error_msg:
    st.error(st.session_state.error_msg)

if st.session_state.playlist:
    st.write("---")
    st.markdown(f"### 🎶 Recommended for {st.session_state.current_mood}")
    
    music_emojis = ["🎵", "🎧", "🎸", "🎹", "🎷", "🥁", "🎤", "🎼", "💿", "📻", "🎹", "🎻"]
    
    for song in st.session_state.playlist:
        random_emoji = random.choice(music_emojis)
        
        st.markdown(f"""
        <div class="song-card">
            <div class="album-art">{random_emoji}</div>
            <div class="song-info">
                <div class="song-title">{song.get('title', 'Unknown')}</div>
                <div class="song-artist">{song.get('artist', 'Unknown')}</div>
            </div>
            <a href="{song.get('link', 'https://www.youtube.com')}" target="_blank" class="listen-btn">▶ Listen</a>
        </div>
        """, unsafe_allow_html=True)


