import streamlit as st
import requests

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="centered")

# --- 2. CUSTOM CSS (THE "PRETTY" PART) ---
# This hides the default menus and styles the title
st.markdown("""
    <style>
    /* Hide the default Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style the Chat Input to look cleaner */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    
    /* Custom Title Style */
    .custom-title {
        font-size: 50px;
        font-weight: bold;
        background: -webkit-linear-gradient(45deg, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 10px;
    }
    .custom-subtitle {
        text-align: center;
        color: #b0b0b0;
        font-size: 18px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. GET API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing! Check your Secrets.")
    st.stop()

# --- 4. SIDEBAR (Keeps main screen clean) ---
with st.sidebar:
    st.header("About VibeChecker")
    st.info(
        "I am an AI DJ trained to understand human emotions.\n\n"
        "**How to use:**\n"
        "1. Type how you feel below.\n"
        "2. Get 5 hand-picked songs.\n"
        "3. Click the links to listen."
    )
    st.write("---")
    st.caption("Powered by Gemini 2.0 Flash")

# --- 5. MAIN HEADER (With Custom Style) ---
st.markdown('<p class="custom-title">🎵 VibeChecker</p>', unsafe_allow_html=True)
st.markdown('<p class="custom-subtitle">Tell me your mood. I\'ll drop the beat.</p>', unsafe_allow_html=True)

# --- 6. INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. THE BRAIN ---
def get_vibechecker_response(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    full_prompt = (
        f"User Input: '{user_prompt}'\n\n"
        "TASK: Analyze if the input is a valid emotion/mood.\n"
        "1. IF GIBBERISH/RANDOM: Output exactly 'ERROR_INVALID'.\n"
        "2. IF VALID: Recommend 5 songs.\n"
        "FORMAT:\n"
        "- No intro/outro text.\n"
        "- 1. **Song Title** - Artist\n"
        "  [▶️ Listen](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
        "  *One short sentence description.*"
    )

    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return "⚠️ I'm having trouble connecting to the vibe stream. Try again."
    except:
        return "⚠️ Connection error."

# --- 8. CHAT INPUT ---
if prompt := st.chat_input("How are you feeling right now?"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Curating tracks... 🎧"):
            response_text = get_vibechecker_response(prompt)
            
            if "ERROR_INVALID" in response_text:
                error_msg = "🚫 I can't read that emotion. Try telling me how you feel (e.g., 'Sad', 'Hyped')."
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
