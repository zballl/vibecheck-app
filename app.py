import streamlit as st
import requests
import json
import base64
import random
import re

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
        font-size: 70px; font-weight: 900; text-align: center;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding-bottom: 20px;
    }
    
    .song-card {
        background-color: white; border-radius: 12px; padding: 15px;
        margin-bottom: 15px; display: flex; align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s;
    }
    .song-card:hover { transform: scale(1.01); }
    
    .album-art {
        width: 60px; height: 60px; background-color: #f0f2f6; border-radius: 8px;
        margin-right: 15px; flex-shrink: 0; display: flex;
        align-items: center; justify-content: center; font-size: 30px;
    }
    
    .song-info { flex-grow: 1; color: #333; margin-right: 15px; }
    .song-title { font-size: 18px; font-weight: 800; margin: 0; color: #000; line-height: 1.2; }
    .song-artist { font-size: 14px; font-weight: 600; color: #555; margin: 2px 0 0 0; }
    
    .listen-btn {
        background-color: white; color: #00d2ff; border: 2px solid #00d2ff;
        padding: 5px 15px; border-radius: 20px; text-decoration: none;
        font-weight: bold; font-size: 12px; white-space: nowrap; transition: all 0.2s;
    }
    .listen-btn:hover { background-color: #00d2ff; color: white; }
    
    .stButton button {
        width: 100%; height: 50px; border-radius: 10px; font-weight: 600;
        border: 1px solid #444; background-color: rgba(20,20,20,0.8); color: white;
    }
    .stButton button:hover { border-color: #00d2ff; color: #00d2ff; }
    </style>
""", unsafe_allow_html=True)

# --- 4. API SETUP ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        import os
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ API Key missing! Check your Secrets.")
        st.stop()
except:
    st.error("⚠️ Error loading API Key.")
    st.stop()

# --- 5. STATE MANAGEMENT ---
if 'playlist' not in st.session_state: st.session_state.playlist = None
if 'error_debug' not in st.session_state: st.session_state.error_debug = None
if 'current_mood' not in st.session_state: st.session_state.current_mood = ""

# --- 6. THE BRAIN (ROBUST VERSION) ---
def get_vibe_check(mood):
    # Try the most standard model alias first
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = (
        f"Analyze mood: '{mood}'.\n"
        "RULES:\n"
        "1. If gibberish, return JSON: [{'error': 'invalid'}]\n"
        "2. Else, return JSON list of 5 songs (title, artist, link).\n"
        "OUTPUT JSON ONLY."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        # 1. Catch HTTP Errors (404, 400, 500)
        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"
            
        # 2. Parse Response
        try:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            
            # 3. Robust JSON Extraction (Finds the list [...] inside text)
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                clean_json = match.group(0)
                return json.loads(clean_json)
            else:
                return "Error: Could not find JSON data in response."
                
        except Exception as e:
            return f"Parsing Error: {str(e)}"
            
    except Exception as e:
        return f"Connection Error: {str(e)}"

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("🎧 Control Panel")
    st.info("VibeChecker AI")
    
    if st.button("🎲 Surprise Me"):
        vibe = random.choice(["Energetic", "Chill", "Melancholy", "Dreamy"])
        st.session_state.current_mood = vibe
        st.session_state.playlist = None # Clear old
        st.session_state.error_debug = None
        
        with st.spinner(f"Curating {vibe}..."):
            result = get_vibe_check(vibe)
            if isinstance(result, list):
                st.session_state.playlist = result
            else:
                st.session_state.error_debug = result
        st.rerun()

    if st.button("🔄 Reset App"):
        st.session_state.playlist = None
        st.session_state.current_mood = ""
        st.session_state.error_debug = None
        st.rerun()

# --- 8. MAIN UI ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

# Button Logic
target_mood = None
if b1: target_mood = "Energetic"
if b2: target_mood = "Melancholy"
if b3: target_mood = "Chill"
if b4: target_mood = "Heartbroken"

# Text Logic
user_input = st.text_input("", placeholder="Or type your exact mood here...")
if user_input and user_input != st.session_state.current_mood:
    target_mood = user_input

# EXECUTION
if target_mood:
    st.session_state.current_mood = target_mood
    st.session_state.playlist = None # Clear old
    st.session_state.error_debug = None
    
    with st.spinner(f"Analyzing {target_mood}..."):
        result = get_vibe_check(target_mood)
        
        # If it's a List, it's a Playlist!
        if isinstance(result, list):
            # Check for logic error (gibberish)
            if len(result) > 0 and 'error' in result[0]:
                st.session_state.error_debug = "🚫 That doesn't look like a valid mood!"
            else:
                st.session_state.playlist = result
        # If it's a String, it's an Error Message!
        else:
            st.session_state.error_debug = result

# --- 9. DISPLAY RESULTS ---

# Show Error (if any)
if st.session_state.error_debug:
    st.error(st.session_state.error_debug)

# Show Playlist (if valid)
if st.session_state.playlist:
    st.write("---")
    st.markdown(f"### 🎶 Recommended for {st.session_state.current_mood}")
    
    emojis = ["🎵", "🎸", "🎹", "🎷", "🎧"]
    for song in st.session_state.playlist:
        emo = random.choice(emojis)
        st.markdown(f"""
        <div class="song-card">
            <div class="album-art">{emo}</div>
            <div class="song-info">
                <div class="song-title">{song.get('title','Track')}</div>
                <div class="song-artist">{song.get('artist','Artist')}</div>
            </div>
            <a href="{song.get('link','https://www.youtube.com')}" target="_blank" class="listen-btn">▶ Listen</a>
        </div>
        """, unsafe_allow_html=True)
