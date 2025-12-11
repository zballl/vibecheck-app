import streamlit as st
import requests
import json

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="VibeCheck", page_icon="🎵")
st.title("🎵 VibeCheck")
st.write("Tell me how you feel, and I'll generate a playlist.")

# --- 2. GET API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ API Key missing! Check your Secrets.")
    st.stop()

# --- 3. DIRECT CONNECTION FUNCTION ---
def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            return "Error parsing response."
    elif response.status_code == 429:
        return "⚠️ Quota Limit. Please wait 1 minute."
    else:
        return f"Google Error {response.status_code}"

# --- 4. THE APP UI ---
mood = st.text_input("How are you feeling?", placeholder="e.g. Happy, Anxious, Excited")

if st.button("Generate Playlist"):
    if not mood:
        st.warning("Please tell me your mood first!")
    else:
        with st.spinner("Analyzing your vibe... 🧐"):
            # --- INTELLIGENT PROMPT WITH GUARDRAILS ---
            dj_prompt = (
                f"User Input: '{mood}'\n\n"
                "TASK: Analyze if the User Input is a valid human emotion, mood, or vibe.\n"
                "RULES:\n"
                "1. IF the input is gibberish, random keys (like 'fajs;fhasf;', 'asdf'), or NOT a feeling: Output ONLY the word 'ERROR_INVALID'.\n"
                "2. IF the input is a valid emotion: Recommend 5 songs.\n\n"
                "FORMATTING FOR VALID SONGS:\n"
                "- No intro text.\n"
                "- Format: 1. **Song Title** - Artist\n"
                "   [▶️ Listen on YouTube](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
                "   *One short sentence description.*\n"
            )
            
            # Call the AI
            result = get_gemini_response(dj_prompt)
            
            # Check for our secret error code
            if "ERROR_INVALID" in result:
                st.error("🚫 That doesn't look like an emotion! Please try again.")
            else:
                st.markdown(result)
