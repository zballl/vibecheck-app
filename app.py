import streamlit as st
import requests
import json
import base64

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# --- 2. IMAGE LOADER ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. CSS DESIGN ---
try:
    img_base64 = get_base64_of_bin_file("background.jpeg")
    background_style = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """
except:
    background_style = "<style>.stApp { background-color: #0E1117; }</style>"

st.markdown(background_style, unsafe_allow_html=True)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-title {
        font-size: 60px;
        font-weight: 800;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #ffffff, #a0a0a0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 18px;
        margin-bottom: 40px;
    }

    /* CARD STYLE */
    .song-card {
        background-color: white;
        color: black;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 10px solid #FF0080;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .song-title { font-size: 20px; font-weight: bold; margin: 0; }
    .song-artist { color: #555; font-size: 16px; margin-bottom: 10px; }
    .song-desc { font-style: italic; color: #333; font-size: 14px; }
    .listen-btn {
        display: inline-block;
        background-color: #00d2ff;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: bold;
        font-size: 12px;
        margin-top: 5px;
    }
    
    /* BUTTONS STYLE */
    .stButton button {
        border-radius: 25px;
        height: 50px;
        font-weight: 600;
        border: none;
        background-color: #1F2937;
        color: white;
        transition: 0.2s;
    }
    .stButton button:hover {
        background-color: #FF0080;
        color: white;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing!")
    st.stop()

# --- 5. SIMPLE STATE MANAGEMENT ---
# No complex history, just holding the current data
if "playlist_data" not in st.session_state:
    st.session_state.playlist_data = None
if "questions_mode" not in st.session_state:
    st.session_state.questions_mode = False
if "questions_text" not in st.session_state:
    st.session_state.questions_text = ""

# --- 6. THE BRAIN ---
def call_gemini(prompt, output_type="json"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    if output_type == "json":
        full_prompt = f"{prompt}\nOUTPUT FORMAT: A raw JSON list only. Example: [{{'title': 'X', 'artist': 'Y', 'desc': 'Z', 'link': 'http'}}] "
    else:
        full_prompt = prompt

    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
    
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            text = res.json()['candidates'][0]['content']['parts'][0]['text']
            if output_type == "json":
                clean_json = text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_json)
            return text
    except:
        return None
    return None

# --- 7. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🎧 VibeChecker")
    st.markdown("### How to Use")
    st.info("1. Click a mood button.\n2. OR type your feeling.\n3. OR click 'Not Sure' to get help.")
    if st.button("🏠 Reset App"):
        st.session_state.playlist_data = None
        st.session_state.questions_mode = False
        st.rerun()

# --- 8. MAIN DASHBOARD ---
st.markdown('<div class="main-title">VibeChecker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your Personal Mood-Based Music Curator</div>', unsafe_allow_html=True)

# BUTTONS ROW
col1, col2, col3, col4 = st.columns(4)
b1 = col1.button("⚡ Energetic")
b2 = col2.button("☂️ Melancholy")
b3 = col3.button("🧘 Chill")
b4 = col4.button("💔 Heartbroken")

# BUTTON LOGIC
if b1:
    with st.spinner("Curating Energetic playlist..."):
        st.session_state.playlist_data = call_gemini("User is Energetic. 5 songs.", "json")
        st.session_state.questions_mode = False
    st.rerun()

if b2:
    with st.spinner("Curating Melancholy playlist..."):
        st.session_state.playlist_data = call_gemini("User is Melancholy. 5 songs.", "json")
        st.session_state.questions_mode = False
    st.rerun()

if b3:
    with st.spinner("Curating Chill playlist..."):
        st.session_state.playlist_data = call_gemini("User is Chill. 5 songs.", "json")
        st.session_state.questions_mode = False
    st.rerun()

if b4:
    with st.spinner("Curating Heartbroken playlist..."):
        st.session_state.playlist_data = call_gemini("User is Heartbroken. 5 songs.", "json")
        st.session_state.questions_mode = False
    st.rerun()

# "NOT SURE" BUTTON LOGIC
st.write("")
if st.button("🤔 Not sure how I feel? Help me."):
    with st.spinner("Consulting AI..."):
        q = call_gemini("Ask 3 short questions to determine mood.", "text")
        st.session_state.questions_text = q
        st.session_state.questions_mode = True
        st.session_state.playlist_data = None # Clear old songs
    st.rerun()

# DISPLAY QUESTIONS (If mode is active)
if st.session_state.questions_mode:
    st.info("Answer these questions below to find your vibe:")
    st.markdown(st.session_state.questions_text)

# INPUT BAR
placeholder = "Type your answers here..." if st.session_state.questions_mode else "Type your mood here..."
user_input = st.text_input("", placeholder=placeholder)

# INPUT LOGIC (Trigger on Enter)
if user_input:
    with st.spinner("Analyzing..."):
        if st.session_state.questions_mode:
            prompt = f"User answers: {user_input}. Recommend 5 songs."
        else:
            prompt = f"User mood: {user_input}. Recommend 5 songs."
            
        st.session_state.playlist_data = call_gemini(prompt, "json")
        st.session_state.questions_mode = False # Reset mode
    st.rerun()

# RESULT DISPLAY (THE CARDS)
if st.session_state.playlist_data:
    st.write("---")
    st.markdown("### 🎶 Recommended for You")
    for song in st.session_state.playlist_data:
        st.markdown(f"""
        <div class="song-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p class="song-title">{song.get('title', 'Unknown')}</p>
                    <p class="song-artist">{song.get('artist', 'Unknown')}</p>
                    <p class="song-desc">"{song.get('desc', 'Great vibe')}"</p>
                </div>
                <div>
                    <a href="{song.get('link', '#')}" target="_blank" class="listen-btn">▶ Listen</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
