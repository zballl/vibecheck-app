import streamlit as st
import requests

# --- 1. SETUP PAGE CONFIG ---
st.set_page_config(page_title="VibeChecker", page_icon="🎵", layout="centered")

# --- 2. GET API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing! Check your Secrets.")
    st.stop()

# --- 3. HEADER (Simple Text as requested) ---
st.title("🎵 VibeChecker")
st.write("Your personal mood music curator.")

# --- 4. INITIALIZE CHAT HISTORY ---
# This remembers the chat so it looks like a real conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages (The Chat Bubbles)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. THE BRAIN (Direct Connection) ---
def get_vibechecker_response(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # The DJ Persona & Instructions
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

# --- 6. THE CHAT INPUT (Bottom Bar) ---
# This creates the text bar at the bottom like WhatsApp/Math Buddy
if prompt := st.chat_input("How are you feeling right now?"):
    
    # 1. Show User Message Immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    # Save to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. VibeChecker Thinks...
    with st.chat_message("assistant"):
        with st.spinner("VibeChecker is curating... 🎧"):
            response_text = get_vibechecker_response(prompt)
            
            # Check for the Gibberish Error
            if "ERROR_INVALID" in response_text:
                error_msg = "🚫 I can only read human emotions. Please tell me how you feel!"
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
