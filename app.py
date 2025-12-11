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

# --- 3. CUSTOM CSS (The Dashboard Look) ---
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
    /* Clean up UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TITLE STYLE */
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

    /* CARD STYLE (The White Boxes) */
    .song-card {
        background-color: white;
        color: black;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 10px solid #FF0080; /* Pink accent strip */
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
    
    /* BUTTONS STYLE (Pill Shape) */
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
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111;
        border-right: 1px solid #333;
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
if "past_moods" not in st.session_state:
    st.session_state.past_moods = []
if "current_playlist" not in st.session_state:
    st.session_state.current_playlist = None
if "current_mood_text" not in st.session_state:
    st.session_state.current_mood_text = ""

# --- 6. THE BRAIN (Now outputs JSON for Cards) ---
def get_music_data(mood):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # We ask for JSON format to build the cards
    prompt = (
        f"User Mood: '{mood}'\n"
        "TASK: detailed analysis of mood. If valid, return a JSON list of 5 songs.\n"
        "OUTPUT FORMAT: A raw JSON list only. No markdown. Example: \n"
        '[{"title": "Song Name", "artist": "Artist", "desc": "Why it fits.", "link": "https://youtube.com..."}]'
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            text_response = res.json()['candidates'][0]['content']['parts'][0]['text']
            # Clean up response to ensure valid JSON
            clean_json = text_response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json) # Convert text to Python List
    except:
        return None
    return None

# --- 7. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🎧 VibeChecker")
    st.markdown("*Your elegant AI music curator.*")
    st.write("---")
    
    st.markdown("### How to Use")
    st.markdown("1. Select a mood\n2. View recommendations\n3. Click to listen")
    
    st.write("---")
    st.markdown("### Past Moods")
    for m in st.session_state.past_moods[-5:]: # Show last 5
        st.caption(f"• {m}")
        
    st.write("---")
    if st.button("🎲 Surprise Me"):
        st.session_state.current_mood_text = "Surprise me with something random but amazing"
        # Trigger generation immediately
        data = get_music_data("Surprise me with something random")
        if data:
            st.session_state.current_playlist = data
            st.session_state.past_moods.append("Surprise Me")
            st.rerun()

# --- 8. MAIN DASHBOARD ---

# Header
st.markdown('<div class="main-title">VibeChecker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your Personal Mood-Based Music Curator</div>', unsafe_allow_html=True)
st.write("")

# Button Row
col1, col2, col3, col4 = st.columns(4)
selected_mood = None

with col1:
    if st.button("⚡ Energetic"): selected_mood = "Energetic"
with col2:
    if st.button("☂️ Melancholy"): selected_mood = "Melancholy"
with col3:
    if st.button("🧘 Chill"): selected_mood = "Chill"
with col4:
    if st.button("💔 Heartbroken"): selected_mood = "Heartbroken"

# Handle Button Clicks
if selected_mood:
    st.session_state.current_mood_text = selected_mood
    with st.spinner(f"Curating {selected_mood} vibes..."):
        data = get_music_data(selected_mood)
        if data:
            st.session_state.current_playlist = data
            st.session_state.past_moods.append(selected_mood)

# Input Bar (Centered)
user_input = st.text_input("", placeholder="Type your mood here...", value=st.session_state.current_mood_text)

# Logic for typing in the box
if user_input and user_input != st.session_state.current_mood_text:
    st.session_state.current_mood_text = user_input
    with st.spinner(f"Analyzing '{user_input}'..."):
        data = get_music_data(user_input)
        if data:
            st.session_state.current_playlist = data
            st.session_state.past_moods.append(user_input)
            st.rerun()

# --- 9. RESULTS SECTION (THE CARDS) ---
st.write("")
if st.session_state.current_playlist:
    st.markdown(f"### Recommended for {st.session_state.current_mood_text}")
    
    # Loop through the data and create White Cards
    for song in st.session_state.current_playlist:
        # We use HTML to style the card exactly like the image
        st.markdown(f"""
        <div class="song-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p class="song-title">{song['title']}</p>
                    <p class="song-artist">{song['artist']}</p>
                    <p class="song-desc">"{song['desc']}"</p>
                </div>
                <div>
                    <a href="{song.get('link', '#')}" target="_blank" class="listen-btn">▶ Listen</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Question Feature (Kept as requested)
st.write("---")
if st.button("🤔 Not sure how I feel? Help me."):
    st.info("Ask yourself: Do you want high energy or low energy? Do you want lyrics or instrumental?")
