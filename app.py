import streamlit as st
import requests
import json
import base64
import random
import re

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# --- 2. API KEY SETUP (From Secrets) ---
try:
    # This command looks inside .streamlit/secrets.toml
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ The .streamlit/secrets.toml file was not found.")
    st.stop()
except KeyError:
    st.error("⚠️ The secret file exists, but it doesn't have a 'GOOGLE_API_KEY' inside.")
    st.stop()

# --- 3. IMAGE LOADER ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# --- 4. CUSTOM CSS ---
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
    </style>
""", unsafe_allow_html=True)

# --- 5. THE BRAIN ---
def get_vibe_check(mood):
    # Using the safest stable model endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    prompt = (
        f"Analyze mood: '{mood}'. Return JSON list of 5 songs (title, artist, link). "
        "OUTPUT JSON ONLY."
    )
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        return f"Error: {response.status_code} (Check if API Key is correct)"
    except Exception as e:
        return f"Connection Failed: {str(e)}"

# --- 6. MAIN UI ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

if 'playlist' not in st.session_state: st.session_state.playlist = None
if 'current_mood' not in st.session_state: st.session_state.current_mood = ""

# Buttons
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

# Logic
target_mood = None
if b1: target_mood = "Energetic"
if b2: target_mood = "Melancholy"
if b3: target_mood = "Chill"
if b4: target_mood = "Heartbroken"

if target_mood:
    st.session_state.current_mood = target_mood
    with st.spinner(f"Curating {target_mood} tracks..."):
        res = get_vibe_check(target_mood)
        if isinstance(res, list): 
            st.session_state.playlist = res
        else: 
            st.error(res)

# Display
if st.session_state.playlist:
    st.write("---")
    st.markdown(f"### 🎶 Recommended for {st.session_state.current_mood}")
    for song in st.session_state.playlist:
        st.markdown(f"""
        <div class="song-card">
            <div class="album-art">🎵</div>
            <div style="flex-grow:1; margin-right:15px; color:black;">
                <div style="font-weight:800; font-size:18px;">{song.get('title','Track')}</div>
                <div>{song.get('artist','Artist')}</div>
            </div>
            <a href="{song.get('link','#')}" target="_blank" class="listen-btn">▶ Listen</a>
        </div>
        """, unsafe_allow_html=True)
