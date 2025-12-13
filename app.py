import streamlit as st
import requests
import json
import base64
import random
import re
import os

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

# --- 4. API SETUP (DEBUG MODE) ---
api_key = None
source = "Unknown"

# Try loading from Secrets first
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    source = "Secrets"
# Fallback to Environment Variable
elif os.environ.get("GOOGLE_API_KEY"):
    api_key = os.environ.get("GOOGLE_API_KEY")
    source = "Env Var"

if not api_key:
    st.error("⚠️ API Key missing! Check your Secrets or Render Environment.")
    st.stop()

# --- 5. STATE MANAGEMENT ---
if 'playlist' not in st.session_state: st.session_state.playlist = None
if 'error_debug' not in st.session_state: st.session_state.error_debug = None
if 'current_mood' not in st.session_state: st.session_state.current_mood = ""
if 'questions_asked' not in st.session_state: st.session_state.questions_asked = False
if 'q1' not in st.session_state: st.session_state.q1 = "Neutral"
if 'q2' not in st.session_state: st.session_state.q2 = "Relaxed"
if 'q3' not in st.session_state: st.session_state.q3 = "Calm"
if 'used_model' not in st.session_state: st.session_state.used_model = ""

# --- 6. THE BRAIN (AGGRESSIVE CONNECTION) ---
def get_vibe_check(mood):
    # EXTENSIVE MODEL LIST: Hits every possible variation to find one that works
    models_to_try = [
        "gemini-2.0-flash-exp",     # Newest (likely works for new keys)
        "gemini-1.5-flash",         # Standard
        "gemini-1.5-flash-001",     # Specific Version
        "gemini-1.5-flash-latest",  # Alias
        "gemini-1.5-pro",           # Pro Version
        "gemini-pro"                # Oldest/Stable fallback
    ]
    
    prompt = (
        f"Analyze mood: '{mood}'.\n"
        "RULES:\n"
        "1.If gibberish/nonsense, return JSON: [{'error': 'invalid'}]\n"
        "2. Else, return JSON list of 5 songs (title, artist, link).\n"
        "OUTPUT JSON ONLY."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    
    error_log = []

    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            response = requests.post(url, headers=headers, json=data)
            
            # If 200 OK, we found a winner!
            if response.status_code == 200:
                try:
                    text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    match = re.search(r"\[.*\]", text, re.DOTALL)
                    if match:
                        clean_json = match.group(0)
                        st.session_state.used_model = model_name # Save which one worked
                        return json.loads(clean_json) 
                except:
                    error_log.append(f"{model_name} (Parse Fail)")
                    continue
            else:
                error_log.append(f"{model_name} ({response.status_code})")
                continue

        except Exception as e:
            error_log.append(f"{model_name} (Conn Error)")
            continue

    return f"ALL Models Failed. Logs: {', '.join(error_log)}"

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("🎧 Control Panel")
    st.info("VibeChecker AI")
    
    # DEBUG INFO
    st.caption(f"🔑 Key Source: {source}")
    st.caption(f"🆔 Key ID: {api_key[:4]}...{api_key[-4:]}")
    if st.session_state.used_model:
        st.success(f"✅ Connected to: {st.session_state.used_model}")
    
    if st.button("🎲 Surprise Me"):
        vibe = random.choice(["Energetic", "Chill", "Melancholy", "Dreamy"])
        st.session_state.current_mood = vibe
        st.session_state.playlist = None
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
        st.session_state.questions_asked = False
        st.rerun()

# --- 8. MAIN UI ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

# Buttons
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")
not_sure_button = st.button("🤔 Not Sure How I Feel")

# Logic
target_mood = None
if b1: target_mood = "Energetic"
if b2: target_mood = "Melancholy"
if b3: target_mood = "Chill"
if b4: target_mood = "Heartbroken"

if target_mood:
    st.session_state.current_mood = target_mood
    with st.spinner(f"Analyzing mood: {target_mood}..."):
        result = get_vibe_check(target_mood)
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error_debug = result

# Questions
if not_sure_button and not st.session_state.questions_asked:
    st.session_state.questions_asked = True

if st.session_state.questions_asked:
    st.info("Answer these questions:")
    q1 = st.selectbox("1. Physical feeling?", ["Energetic", "Tired", "Neutral", "Weak"], index=["Energetic", "Tired", "Neutral", "Weak"].index(st.session_state.q1))
    q2 = st.selectbox("2. Emotional state?", ["Happy", "Sad", "Anxious", "Relaxed"], index=["Happy", "Sad", "Anxious", "Relaxed"].index(st.session_state.q2))
    q3 = st.selectbox("3. Mental state?", ["Focused", "Distracted", "Overwhelmed", "Calm"], index=["Focused", "Distracted", "Overwhelmed", "Calm"].index(st.session_state.q3))

    st.session_state.q1 = q1
    st.session_state.q2 = q2
    st.session_state.q3 = q3

    if st.button("Analyze Mood"):
        inferred_mood = "Neutral"
        if "Energetic" in q1 and "Happy" in q2: inferred_mood = "Energetic"
        elif "Tired" in q1 and "Sad" in q2: inferred_mood = "Melancholy"
        elif "Relaxed" in q2: inferred_mood = "Chill"
        
        st.session_state.current_mood = inferred_mood
        st.session_state.playlist = None
        st.session_state.error_debug = None

        with st.spinner(f"Analyzing mood: {inferred_mood}..."):
            result = get_vibe_check(inferred_mood)
            if isinstance(result, list):
                st.session_state.playlist = result
            else:
                st.session_state.error_debug = result
        st.rerun()

# --- 9. USER INPUT ---
user_input = st.text_input("Or type your exact mood here...")

if user_input and user_input != st.session_state.current_mood:
    st.session_state.current_mood = user_input
    st.session_state.playlist = None
    st.session_state.error_debug = None

    with st.spinner(f"Analyzing mood: {user_input}..."):
        result = get_vibe_check(user_input)
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error_debug = result

# --- 10. DISPLAY RESULTS ---
if st.session_state.error_debug:
    st.error(st.session_state.error_debug)

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
            <a href="{song.get('link','https://www.youtube.com')}" target="_blank" class="listen-btn">▶️ Listen</a>
        </div>
        """, unsafe_allow_html=True)
