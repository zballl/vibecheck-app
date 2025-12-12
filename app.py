import streamlit as st
import requests
import json
import base64
import random

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="wide")

# --- 2. GET API KEY ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        # Fallback for local testing or Render
        import os
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ API Key missing! Check your Secrets.")
        st.stop()
except:
    st.error("⚠️ Error finding API Key.")
    st.stop()

# --- 3. CSS & DESIGN ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

img_base64 = get_base64_of_bin_file("background.jpeg")
if img_base64:
    background_css = f"""background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("data:image/jpeg;base64,{img_base64}");"""
else:
    background_css = "background-color: #0E1117;"

st.markdown(f"""
    <style>
    .stApp {{
        {background_css}
        background-size: cover;
        background-attachment: fixed;
    }}
    .title-text {{
        font-size: 70px; font-weight: 900; text-align: center;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding-bottom: 20px;
    }}
    .song-card {{
        background-color: white; color: black; border-radius: 12px; padding: 15px;
        margin-bottom: 15px; display: flex; align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    .album-art {{
        width: 60px; height: 60px; background-color: #eee; border-radius: 8px;
        margin-right: 15px; display: flex; align-items: center; justify-content: center;
        font-size: 30px;
    }}
    .listen-btn {{
        background-color: white; color: #00d2ff; border: 2px solid #00d2ff;
        padding: 5px 15px; border-radius: 20px; text-decoration: none;
        font-weight: bold; font-size: 12px; white-space: nowrap;
    }}
    .stButton button {{
        width: 100%; height: 50px; border-radius: 10px; font-weight: 600;
        border: 1px solid #444; background-color: rgba(20,20,20,0.8); color: white;
    }}
    .stButton button:hover {{ border-color: #00d2ff; color: #00d2ff; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. THE BRAIN (SIMPLE VERSION) ---
def get_playlist(user_input, is_questions=False):
    # Using 'gemini-flash-latest' which is the safest bet for your account
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    if is_questions:
        prompt = "Ask 3 short questions to help determine mood. Return ONLY the questions as a numbered list."
    else:
        prompt = (
            f"User Input: '{user_input}'.\n"
            "1. If gibberish/nonsense -> Return JSON [{'error': 'true'}]\n"
            "2. If valid -> Return JSON list of 5 songs with title, artist, desc, and link.\n"
            "Output JSON ONLY."
        )

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return None
        
        text = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        if is_questions:
            return text # Return the text questions directly
            
        # Clean JSON for playlist
        clean_json = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except:
        return None

# --- 5. APP LOGIC ---

# Initialize State (Memory)
if 'page_mode' not in st.session_state: st.session_state.page_mode = 'home'
if 'playlist' not in st.session_state: st.session_state.playlist = None
if 'questions' not in st.session_state: st.session_state.questions = ""
if 'mood_name' not in st.session_state: st.session_state.mood_name = ""

# SIDEBAR
with st.sidebar:
    st.title("🎧 Control Panel")
    st.info("VibeChecker AI Curator")
    
    if st.button("🎲 Surprise Me"):
        vibe = random.choice(["Energetic", "Chill", "Melancholy", "Dreamy"])
        st.session_state.mood_name = vibe
        with st.spinner(f"Curating {vibe}..."):
            data = get_playlist(vibe)
            st.session_state.playlist = data
            st.session_state.page_mode = 'playlist'
        st.rerun()

    if st.button("🔄 Reset App"):
        st.session_state.page_mode = 'home'
        st.session_state.playlist = None
        st.rerun()

# MAIN UI
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

# MODE: HOME (Buttons)
if st.session_state.page_mode == 'home':
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("⚡ Energetic"):
        st.session_state.mood_name = "Energetic"
        with st.spinner("Curating..."):
            st.session_state.playlist = get_playlist("Energetic")
            st.session_state.page_mode = 'playlist'
        st.rerun()
        
    if c2.button("☂️ Melancholy"):
        st.session_state.mood_name = "Melancholy"
        with st.spinner("Curating..."):
            st.session_state.playlist = get_playlist("Melancholy")
            st.session_state.page_mode = 'playlist'
        st.rerun()

    if c3.button("🧘 Chill"):
        st.session_state.mood_name = "Chill"
        with st.spinner("Curating..."):
            st.session_state.playlist = get_playlist("Chill")
            st.session_state.page_mode = 'playlist'
        st.rerun()

    if c4.button("💔 Heartbroken"):
        st.session_state.mood_name = "Heartbroken"
        with st.spinner("Curating..."):
            st.session_state.playlist = get_playlist("Heartbroken")
            st.session_state.page_mode = 'playlist'
        st.rerun()

    st.write("")
    if st.button("🤔 Not sure how I feel?"):
        with st.spinner("Thinking..."):
            q = get_playlist("", is_questions=True)
            st.session_state.questions = q
            st.session_state.page_mode = 'questions'
        st.rerun()

    # Manual Input
    user_text = st.text_input("", placeholder="Or type your exact mood here...")
    if user_text:
        st.session_state.mood_name = user_text
        with st.spinner("Analyzing..."):
            data = get_playlist(user_text)
            if data and isinstance(data, list) and 'error' not in data[0]:
                st.session_state.playlist = data
                st.session_state.page_mode = 'playlist'
            else:
                st.error("🚫 That doesn't look like a valid mood.")
        if st.session_state.page_mode == 'playlist':
            st.rerun()

# MODE: QUESTIONS
elif st.session_state.page_mode == 'questions':
    st.info("Answer these questions to help us find your vibe:")
    st.markdown(f"**{st.session_state.questions}**")
    
    ans = st.text_input("Your Answers:", placeholder="Type here...")
    if ans:
        st.session_state.mood_name = "Your Vibe"
        with st.spinner("Analyzing your answers..."):
            data = get_playlist(f"User answers: {ans}. Recommend songs.")
            st.session_state.playlist = data
            st.session_state.page_mode = 'playlist'
        st.rerun()
        
    if st.button("Back"):
        st.session_state.page_mode = 'home'
        st.rerun()

# MODE: PLAYLIST (Results)
elif st.session_state.page_mode == 'playlist':
    st.markdown(f"### 🎶 Recommended for {st.session_state.mood_name}")
    
    if st.session_state.playlist:
        emojis = ["🎵", "🎸", "🎹", "🎷", "🎧"]
        for song in st.session_state.playlist:
            emo = random.choice(emojis)
            st.markdown(f"""
            <div class="song-card">
                <div class="album-art">{emo}</div>
                <div style="flex-grow:1; margin-right:15px;">
                    <div style="font-weight:800; font-size:18px;">{song.get('title','Track')}</div>
                    <div style="color:#555;">{song.get('artist','Artist')}</div>
                    <div style="font-size:12px; font-style:italic; color:#777;">"{song.get('desc','Vibe check passed.')}"</div>
                </div>
                <a href="{song.get('link','#')}" target="_blank" class="listen-btn">▶ Listen</a>
            </div>
            """, unsafe_allow_html=True)
            
    if st.button("Start Over"):
        st.session_state.page_mode = 'home'
        st.session_state.playlist = None
        st.rerun()
