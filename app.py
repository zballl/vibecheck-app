import streamlit as st
import requests
import json
import base64
import random

# --- 1. SETUP PAGE ---
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
            background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{img_base64}");
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
    
    /* TITLE */
    .title-text {
        font-size: 70px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
    }
    
    /* SONG CARD CONTAINER */
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
    
    /* EMOJI ART BOX */
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
    
    /* TEXT INFO */
    .song-info { flex-grow: 1; color: #333; margin-right: 15px; }
    .song-title { font-size: 20px; font-weight: 800; margin: 0; color: #000; line-height: 1.2; }
    .song-artist { font-size: 16px; font-weight: 600; color: #555; margin: 2px 0 5px 0; }
    .song-desc { font-size: 14px; color: #666; font-style: italic; margin: 0; line-height: 1.4; }
    
    /* LISTEN BUTTON */
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
        height: 40px;
        line-height: 20px;
        display: flex;
        align-items: center;
    }
    .listen-btn:hover { background-color: #00d2ff; color: white; }
    
    /* BUTTON STYLING */
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

# --- 5. SESSION STATE ---
if "playlist" not in st.session_state:
    st.session_state.playlist = None
if "current_mood" not in st.session_state:
    st.session_state.current_mood = ""
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None
if "questions_mode" not in st.session_state:
    st.session_state.questions_mode = False
if "questions_text" not in st.session_state:
    st.session_state.questions_text = ""

# --- 6. AI FUNCTIONS ---

# Function A: Generate Playlist (JSON)
def get_vibe_playlist(prompt_input):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    final_prompt = (
        f"Input: '{prompt_input}'\n"
        "TASK: Recommend 5 songs.\n"
        "RULES:\n"
        "1. STRICT: If input is gibberish/nonsense -> RETURN JSON: [{'error': 'invalid'}]\n"
        "2. Include 'desc' (short reason) and 'link' (YouTube Search).\n"
        "OUTPUT FORMAT (Raw JSON only):\n"
        "[{\"title\": \"Song\", \"artist\": \"Artist\", \"desc\": \"Reason.\", \"link\": \"https://youtube...\"}]"
    )
    
    data = {"contents": [{"parts": [{"text": final_prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            text = res.json()['candidates'][0]['content']['parts'][0]['text']
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
    except:
        return None
    return None

# Function B: Generate Questions (Text)
def get_therapy_questions():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = "Ask 3 short, creative questions to help a user figure out their mood. Format as a numbered list."
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "1. Do you have energy? 2. Do you want to be alone? 3. Happy or Sad?"
    return "Error generating questions."

# --- 7. SIDEBAR (With Surprise Me) ---
with st.sidebar:
    st.title("🎧 Control Panel")
    st.markdown("### ℹ️ About VibeChecker")
    st.info("Your personal AI Music Curator.")
    
    st.write("---")
    
    # 1. NEW SURPRISE BUTTON
    if st.button("🎲 Surprise Me"):
        random_vibe = random.choice(["Energetic", "Melancholy", "Chill", "Heartbroken"])
        st.session_state.current_mood = random_vibe
        st.session_state.questions_mode = False # Turn off questions if active
        
        with st.spinner(f"Surprise! Curating {random_vibe} tracks..."):
            data = get_vibe_playlist(random_vibe)
            st.session_state.playlist = data
            st.session_state.error_msg = None
        st.rerun()

    if st.button("🔄 Reset App"):
        st.session_state.playlist = None
        st.session_state.current_mood = ""
        st.session_state.questions_mode = False
        st.session_state.questions_text = ""
        st.session_state.error_msg = None
        st.rerun()

# --- 8. MAIN UI ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

# Mood Buttons
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

# Button Logic
clicked_mood = None
if b1: clicked_mood = "Energetic"
if b2: clicked_mood = "Melancholy"
if b3: clicked_mood = "Chill"
if b4: clicked_mood = "Heartbroken"

# "Not Sure" Button -> Triggers Question Mode
st.write("")
if st.button("🤔 Not sure how I feel?"):
    with st.spinner("Consulting AI Therapist..."):
        questions = get_therapy_questions()
        st.session_state.questions_text = questions
        st.session_state.questions_mode = True
        st.session_state.playlist = None # Hide old playlist
        st.session_state.error_msg = None
    st.rerun()

# --- 9. DISPLAY SECTION ---

# A. Show Questions (If Mode Active)
if st.session_state.questions_mode:
    st.info("Answer these 3 questions in the box below:")
    st.markdown(f"**{st.session_state.questions_text}**")
    placeholder_text = "Type your answers here..."
else:
    placeholder_text = "Or type your exact mood here..."

# B. Input Bar
user_input = st.text_input("", placeholder=placeholder_text)

# Logic to Handle Input (Enter Key)
if user_input:
    # If we were in Question Mode, we use the input as the ANSWER
    if st.session_state.questions_mode:
        final_prompt = f"User answered these questions: {user_input}. Determine mood and recommend songs."
        display_mood = "your custom vibe"
        st.session_state.questions_mode = False # Turn off questions now
    else:
        # Normal Mode
        final_prompt = user_input
        display_mood = user_input

    # Generate
    st.session_state.current_mood = display_mood
    st.session_state.error_msg = None
    
    with st.spinner("Curating tracks..."):
        data = get_vibe_playlist(final_prompt)
        
        # Error Checking
        if not data:
             st.session_state.error_msg = "⚠️ Connection Error. Try again."
             st.session_state.playlist = None
        elif isinstance(data, list) and len(data) > 0 and "error" in data[0]:
             st.session_state.error_msg = "🚫 That doesn't look like a real emotion! Please try again."
             st.session_state.playlist = None
        else:
             st.session_state.playlist = data
    st.rerun()

# Logic to Handle Button Clicks (Immediate)
if clicked_mood:
    st.session_state.current_mood = clicked_mood
    st.session_state.questions_mode = False
    st.session_state.error_msg = None
    
    with st.spinner(f"Curating tracks for {clicked_mood}..."):
        data = get_vibe_playlist(clicked_mood)
        st.session_state.playlist = data
    st.rerun()

# --- 10. RENDER RESULTS ---

# Show Error
if st.session_state.error_msg:
    st.error(st.session_state.error_msg)

# Show Playlist
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
                <p class="song-desc">"{song.get('desc', 'A great track for this vibe.')}"</p>
            </div>
            <a href="{song.get('link', 'https://www.youtube.com')}" target="_blank" class="listen-btn">▶ Listen</a>
        </div>
        """, unsafe_allow_html=True)
