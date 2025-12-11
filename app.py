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
    # Using 'gemini-flash-latest' as it works for you
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            return "Error parsing response. Try again."
    elif response.status_code == 429:
        return "⚠️ Quota Limit. Please wait 1 minute and try again."
    else:
        return f"Google Error {response.status_code}: {response.text}"

# --- 4. THE APP UI ---
mood = st.text_input("How are you feeling?", placeholder="e.g. Happy, Anxious, Excited")

if st.button("Generate Playlist"):
    if not mood:
        st.warning("Please tell me your mood first!")
    else:
        with st.spinner("Curating tracks... 🎧"):
            # --- UPDATED INSTRUCTIONS FOR SIMPLE OUTPUT ---
            dj_prompt = (
                f"You are DJ VibeCheck. Recommend 5 songs for this mood: '{mood}'.\n"
                "STRICT FORMATTING RULES:\n"
                "- Do NOT write an intro or outro.\n"
                "- Only list the 5 songs.\n"
                "- Use exactly this format for each song:\n\n"
                "1. **Song Title** - Artist\n"
                "   [▶️ Listen on YouTube](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
                "   *One short sentence explaining the vibe.*\n"
            )
            
            result = get_gemini_response(dj_prompt)
            st.markdown(result)
