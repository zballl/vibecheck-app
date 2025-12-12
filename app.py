import streamlit as st
import requests
import json
import base64

# --- 1. SETUP PAGE (Wide Layout for Cards) ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# --- 2. IMAGE LOADER ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. CUSTOM CSS (The White Card Style) ---
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
    
    /* MAIN TITLE */
    .title-text {
        font-size: 70px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
    }
    
    /* CARD STYLING (Matches your screenshot) */
    .song-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .song-card:hover {
        transform: scale(1.01);
    }
    
    /* The Grey Album Placeholder */
    .album-art {
        width: 80px;
        height: 80px;
        background-color: #e0e0e0; /* Grey box */
        border-radius: 8px;
        margin-right: 20px;
        flex-shrink: 0;
    }
    
    /* Text Info */
    .song-info {
        flex-grow: 1;
        color: #333;
    }
    .song-title {
        font-size: 22px;
        font-weight: 800;
        margin: 0;
        color: #000;
    }
    .song-artist {
        font-size: 16px;
        color: #666;
        margin: 5px 0 0 0;
    }
    
    /* The Listen Button */
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
    .listen-btn:hover {
        background-color: #00d2ff;
        color: white;
    }
    
    /* Button Styling */
    .stButton button {
        width: 100%;
        height: 50px;
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #444;
        background-color: rgba(20,20,20,0.8);
        color: white;
    }
    .stButton button:hover {
        border-color: #00d2ff;
        color: #00d2ff;
    }
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

# --- 6. THE BRAIN (Generates JSON for Cards) ---
def get_vibe_check(mood):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # We ask for JSON format to build the cards
    prompt = (
        f"Recommend 5 songs for mood: '{mood}'.\n"
        "OUTPUT FORMAT: Return ONLY a raw JSON list. No markdown.\n"
        "Example: [{'title': 'Song Name', 'artist': 'Artist Name', 'link': 'https://youtube...'}]"
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            text = res.json()['candidates'][0]['content']['parts'][0]['text']
            # Clean JSON
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
        st.rerun()

# --- 8. MAIN INTERFACE ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

# Quick Mood Buttons
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

# Logic
clicked_mood = None
if b1: clicked_mood = "Energetic"
if b2: clicked_mood = "Melancholy"
if b3: clicked_mood = "Chill"
if b4: clicked_mood = "Heartbroken"

# "Not Sure" Button
st.write("")
if st.button("🤔 Not sure how I feel?"):
    clicked_mood = "Surprise me with a random mix"

# Input Bar
user_input = st.text_input("", placeholder="Or type your exact mood here...", value=st.session_state.current_mood)

# Trigger Generation
final_mood = clicked_mood if clicked_mood else (user_input if user_input != st.session_state.current_mood else None)

if final_mood:
    st.session_state.current_mood = final_mood
    with st.spinner(f"Curating tracks for {final_mood}..."):
        data = get_vibe_check(final_mood)
        if data:
            st.session_state.playlist = data
        else:
            st.error("Could not connect to AI. Try again.")
    st.rerun()

# --- 9. DISPLAY CARDS (The Specific Output You Wanted) ---
if st.session_state.playlist:
    st.write("---")
    st.markdown(f"### 🎶 Recommended for {st.session_state.current_mood}")
    
    for song in st.session_state.playlist:
        # This HTML creates the exact card look from your screenshot
        st.markdown(f"""
        <div class="song-card">
            <div class="album-art"></div>
            <div class="song-info">
                <div class="song-title">{song.get('title', 'Unknown Title')}</div>
                <div class="song-artist">{song.get('artist', 'Unknown Artist')}</div>
            </div>
            <a href="{song.get('link', '#')}" target="_blank" class="listen-btn">Listen</a>
        </div>
        """, unsafe_allow_html=True)
