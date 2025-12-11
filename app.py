import streamlit as st
import requests

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="centered")

# --- 2. CUSTOM DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- BACKGROUND IMAGE SETTINGS --- */
    .stApp {
        /* Replace the URL below with your own image link! */
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("https://images.unsplash.com/photo-1514525253440-b393452e8d26?q=80&w=2800&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* BIGGER LOGO STYLE */
    .title-text {
        font-size: 80px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #FF0080, #7928CA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        line-height: 1.1;
        padding-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5); /* Shadow for readability */
    }
    
    /* Subtitle Style */
    .subtitle-text {
        text-align: center;
        font-size: 20px;
        color: #ddd; /* Lighter text for dark background */
        margin-bottom: 40px;
        text-shadow: 1px 1px 2px black;
    }
    
    /* Quick Select Buttons */
    .stButton button {
        width: 100%;
        border-radius: 12px;
        height: 60px;
        font-size: 16px;
        font-weight: 600;
        border: 1px solid #333;
        background-color: rgba(14, 17, 23, 0.8); /* Semi-transparent */
        color: white;
        transition: all 0.3s;
        backdrop-filter: blur(5px); /* Cool blur effect */
    }
    
    .stButton button:hover {
        border-color: #FF0080;
        color: #FF0080;
        transform: scale(1.02);
        background-color: rgba(14, 17, 23, 1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing! Check your Secrets.")
    st.stop()

# --- 4. SESSION STATE ---
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
    st.info(
        "**How to use:**\n"
        "1. Select a mood or type your own.\n"
        "2. Click the links to listen."
    )
    st.write("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 7. MAIN INTERFACE ---

# A. BIGGER Title
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Your Personal AI Music Curator</p>', unsafe_allow_html=True)

# B. HERO SECTION
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

# C. CHAT HISTORY
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🎧"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# D. CHAT INPUT
if prompt := st.chat_input("Type your mood here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎧"):
        with st.spinner("Curating tracks..."):
            response = get_vibe_check(prompt)
            if "ERROR_INVALID" in response:
                response = "🚫 I didn't catch that vibe. Try telling me an emotion!"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
