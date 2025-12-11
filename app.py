import streamlit as st
import requests
import json
import base64

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# --- 2. IMAGE LOADER ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. CUSTOM CSS ---
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

# --- 5. SESSION STATE ---
# We use 'view_mode' to switch between "Home", "Questions", and "Playlist"
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "home" 
if "playlist_data" not in st.session_state:
    st.session_state.playlist_data = None
if "questions_text" not in st.session_state:
    st.session_state.questions_text = ""
if "current_input_value" not in st.session_state:
    st.session_state.current_input_value = ""

# --- 6. THE BRAIN ---
def call_gemini(prompt, output_type="json"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    if output_type == "json":
        full_prompt = (
            f"{prompt}\n"
            "OUTPUT FORMAT: A raw JSON list only. No markdown. Example: \n"
            '[{"title": "Song", "artist": "Artist", "desc": "Reason", "link": "https://youtube..."}]'
        )
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
    st.markdown("*Your elegant AI music curator.*")
    st.write("---")
    if st.button("🏠 Reset App"):
        st.session_state.view_mode = "home"
        st.session_state.current_input_value = ""
        st.rerun()

# --- 8. MAIN DASHBOARD ---

st.markdown('<div class="main-title">VibeChecker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your Personal Mood-Based Music Curator</div>', unsafe_allow_html=True)
st.write("")

# --- BUTTON LOGIC (IMMEDIATE TRIGGER) ---
col1, col2, col3, col4 = st.columns(4)

# We use variables to capture clicks
click_energy = col1.button("⚡ Energetic")
click_sad = col2.button("☂️ Melancholy")
click_chill = col3.button("🧘 Chill")
click_heart = col4.button("💔 Heartbroken")

# Logic: If any button is clicked, FORCE immediate generation
if click_energy:
    st.session_state.current_input_value = "Energetic"
    with st.spinner("Generating Energetic Vibes..."):
        st.session_state.playlist_data = call_gemini("User feels Energetic. Recommend 5 songs.", "json")
        st.session_state.view_mode = "playlist"
    st.rerun()

if click_sad:
    st.session_state.current_input_value = "Melancholy"
    with st.spinner("Generating Melancholy Vibes..."):
        st.session_state.playlist_data = call_gemini("User feels Melancholy. Recommend 5 songs.", "json")
        st.session_state.view_mode = "playlist"
    st.rerun()

if click_chill:
    st.session_state.current_input_value = "Chill"
    with st.spinner("Generating Chill Vibes..."):
        st.session_state.playlist_data = call_gemini("User feels Chill. Recommend 5 songs.", "json")
        st.session_state.view_mode = "playlist"
    st.rerun()

if click_heart:
    st.session_state.current_input_value = "Heartbroken"
    with st.spinner("Generating Heartbroken Vibes..."):
        st.session_state.playlist_data = call_gemini("User feels Heartbroken. Recommend 5 songs.", "json")
        st.session_state.view_mode = "playlist"
    st.rerun()

# --- THE "NOT SURE" FEATURE ---
st.write("")
if st.button("🤔 Not sure how I feel? Help me."):
    with st.spinner("Consulting AI Therapist..."):
        # Ask AI for questions
        q_prompt = "The user is unsure of their mood. Ask exactly 3 short, creative questions to help determine their vibe. Format as a numbered list."
        st.session_state.questions_text = call_gemini(q_prompt, "text")
        st.session_state.view_mode = "questions"
        st.session_state.current_input_value = "" # Clear box for answer
    st.rerun()

# --- DYNAMIC INPUT BAR ---
# Placeholder changes based on mode
placeholder_text = "Type your mood here..."
if st.session_state.view_mode == "questions":
    placeholder_text = "Type your answers to the questions here..."

user_input = st.text_input("", placeholder=placeholder_text, value=st.session_state.current_input_value)

# Logic for Typing (Pressing Enter)
if user_input and user_input != st.session_state.current_input_value:
    st.session_state.current_input_value = user_input
    
    # If we are answering questions, include context
    if st.session_state.view_mode == "questions":
        prompt = f"User answered these questions: {user_input}. Determine mood and recommend 5 songs."
    else:
        prompt = f"User feels: {user_input}. Recommend 5 songs."
        
    with st.spinner("Curating..."):
        st.session_state.playlist_data = call_gemini(prompt, "json")
        st.session_state.view_mode = "playlist"
    st.rerun()

# --- DISPLAY SECTION ---

# MODE 1: QUESTIONS (AI Therapist)
if st.session_state.view_mode == "questions" and st.session_state.questions_text:
    st.info("Please answer these questions in the box above:")
    st.markdown(f"### 🤖 AI Questions:\n{st.session_state.questions_text}")

# MODE 2: PLAYLIST (Cards)
elif st.session_state.view_mode == "playlist" and st.session_state.playlist_data:
    st.write("---")
    st.markdown(f"### 🎶 Your Vibe Playlist")
    
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
