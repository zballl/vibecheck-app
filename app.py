import streamlit as st
import requests
import base64

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="centered")

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
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{img_base64}");
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
    
    .title-text {
        font-size: 80px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
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
    
    /* Make buttons huge and symmetric */
    .stButton button {
        width: 100%;
        border-radius: 15px;
        height: 70px; /* Taller buttons */
        font-size: 18px;
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
        transform: translateY(-3px); /* Pop up effect */
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

# --- 5. THE BRAIN ---
def get_vibe_check():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    conversation_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        conversation_history.append({"role": role, "parts": [{"text": msg["content"]}]})

    system_prompt = (
        "You are DJ VibeCheck. Recommend 5 songs based on mood.\n"
        "RULES:\n"
        "1. IF user says 'I'm not sure': Ask 3 short questions.\n"
        "2. IF user answers/states mood: State the mood, then list songs.\n"
        "3. IF gibberish: Say 'ERROR_INVALID'.\n\n"
        "FORMAT: 1. **Song** - Artist [▶️ Listen](Link) *Desc*."
    )

    data = {
        "contents": conversation_history,
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
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
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 7. MAIN INTERFACE ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Your Personal AI Music Curator</p>', unsafe_allow_html=True)

# HERO SECTION (SYMMETRIC LAYOUT)
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #fff; text-shadow: 1px 1px 2px black;'>How are you feeling right now?</h4>", unsafe_allow_html=True)
    
    # We use a placeholder to capture clicks
    clicked_mood = None

    # ROW 1: 3 Buttons (Symmetric Top)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚡ Energetic"): clicked_mood = "I'm feeling super energetic!"
    with col2:
        if st.button("🧘‍♂️ Chill"): clicked_mood = "I want to relax and chill."
    with col3:
        if st.button("🌧️ Melancholy"): clicked_mood = "I'm feeling sad and melancholy."

    # ROW 2: 2 Buttons (Symmetric Bottom)
    col4, col5 = st.columns(2)
    with col4:
        if st.button("💔 Heartbroken"): clicked_mood = "I'm heartbroken."
    with col5:
        # The AI Question feature
        if st.button("🤔 Not sure?"): 
            clicked_mood = "I'm not sure how I feel. Ask me 3 simple questions to figure it out."

    if clicked_mood:
        st.session_state.messages.append({"role": "user", "content": clicked_mood})
        st.rerun()

# CHAT HISTORY
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🎧"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# INPUT
if prompt := st.chat_input("Type your mood or answer here..."):
    st.session_state.messages.append({"role": "user", "content
