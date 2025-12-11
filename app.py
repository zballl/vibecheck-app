import streamlit as st
import requests
import base64

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="centered")

# --- 2. FUNCTION TO LOAD LOCAL IMAGE ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. CUSTOM DESIGN (CSS) ---
# We use a try-except block in case the image hasn't uploaded yet
try:
    img_base64 = get_base64_of_bin_file("background.jpeg")
    background_style = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """
except:
    # Fallback if image is missing (prevents crash)
    background_style = """
        <style>
        .stApp {
            background-color: #0E1117;
        }
        </style>
    """

st.markdown(background_style, unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* BIGGER LOGO STYLE */
    .title-text {
        font-size: 80px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5); /* Cyan to Blue gradient matches equalizer */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        line-height: 1.1;
        padding-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .subtitle-text {
        text-align: center;
        font-size: 20px;
        color: #ddd;
        margin-bottom: 40px;
        text-shadow: 1px 1px 2px black;
    }
    
    /* Button Style */
    .stButton button {
        width: 100%;
        border-radius: 12px;
        height: 60px;
        font-size: 16px;
        font-weight: 600;
        border: 1px solid #333;
        background-color: rgba(0, 0, 0, 0.6); 
        color: white;
        transition: all 0.3s;
        backdrop-filter: blur(5px);
    }
    
    .stButton button:hover {
        border-color: #00d2ff;
        color: #00d2ff;
        transform: scale(1.02);
        background-color: rgba(0, 0, 0, 0.8);
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing! Check your Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. THE AI FUNCTION ---
def get_vibe_check(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = (
        f"User Input: '{user_prompt}'\n"
        "TASK: Recommend 5 songs if valid emotion. If gibberish, say 'ERROR_INVALID'.\n"
        "FORMAT: 1. **Song** - Artist [▶️ Listen](Link) *Desc*."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return "⚠️ Connection Error."
    except:
        return "⚠️ Network Error."

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("🎧 Control Panel")
    st.markdown("I am your personal AI DJ.")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 7. MAIN INTERFACE ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Your Personal AI Music Curator</p>', unsafe_allow_html=True)

# HERO SECTION
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #fff; text-shadow: 1px 1px 2px black;'>How are you feeling right now?</h4>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    clicked_mood = None
    
    with col1:
        if st.button("⚡ Energetic"): clicked_mood = "I'm feeling super energetic and hype!"
    with col2:
        if st.button("🌧️ Melancholy"): clicked_mood = "I'm feeling sad and melancholy."
    with col3:
        if st.button("🧘‍♂️ Chill"): clicked_mood = "I want to relax and chill."
    with col4:
        if st.button("💔 Heartbroken"): clicked_mood = "I'm heartbroken and need comfort."

    if clicked_mood:
        st.session_state.messages.append({"role": "user", "content": clicked_mood})
        st.rerun()

# CHAT HISTORY
for msg in st.session_state.messages:
    avatar = "👤

