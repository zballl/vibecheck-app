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
    header {visibility: hidden;}
    
    /* Gradient Title */
    .title-text {
        font-size: 50px;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF0080, #7928CA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* Subtitle */
    .subtitle-text {
        text-align: center;
        font-size: 18px;
        color: #888;
        margin-bottom: 30px;
    }
    
    /* Style the Quick-Select Buttons to look like cards */
    .stButton button {
        width: 100%;
        border-radius: 12px;
        height: 60px;
        font-size: 16px;
        font-weight: 600;
        border: 1px solid #333;
        background-color: #0E1117;
        color: white;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        border-color: #FF0080;
        color: #FF0080;
        transform: scale(1.02);
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
    st.markdown("### 🎧 DJ Control Panel")
    st.write("This AI curates music based on your exact emotional state.")
    st.write("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 7. MAIN INTERFACE ---

# A. Show Title
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Your personal AI Music Curator</p>', unsafe_allow_html=True)

# B. HERO SECTION (Only shows if chat is empty)
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>How are you feeling right now?</h3>", unsafe_allow_html=True)
    
    # 4 Columns for Quick Buttons
    col1, col2, col3, col4 = st.columns(4)
    
    # We use a placeholder variable to capture button clicks
    clicked_mood = None
    
    with col1:
        if st.button("⚡ Energetic"): clicked_mood = "I'm feeling super energetic and hype!"
    with col2:
        if st.button("🌧️ Melancholy"): clicked_mood = "I'm feeling sad and melancholy."
    with col3:
        if st.button("🧘‍♂️ Chill"): clicked_mood = "I want to relax and chill."
    with col4:
        if st.button("💔 Heartbroken"): clicked_mood = "I'm heartbroken and need comfort."

    # If a button was clicked, add it to chat immediately
    if clicked_mood:
        st.session_state.messages.append({"role": "user", "content": clicked_mood})
        st.rerun() # Refresh to show the chat UI

# C. CHAT HISTORY (Shows messages)
for msg in st.session_state.messages:
    # We use specific avatars here
    avatar = "👤" if msg["role"] == "user" else "🎧"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# D. CHAT INPUT
if prompt := st.chat_input("Type your mood here..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. AI Response
    with st.chat_message("assistant", avatar="🎧"):
        with st.spinner("Spinning the tracks..."):
            response = get_vibe_check(prompt)
            
            if "ERROR_INVALID" in response:
                response = "🚫 I didn't catch that vibe. Try telling me an emotion!"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
