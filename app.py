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
    # UPDATED: Using 'gemini-flash-latest'.
    # This automatically finds the working version for your account.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    # Send request
    response = requests.post(url, headers=headers, json=data)
    
    # Handle response
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            return "Error parsing response. Try again."
    else:
        # Fallback: If Flash limit is 0, try Pro
        if response.status_code == 429:
             return "⚠️ Quota Limit. Please wait 1 minute and try again, or create a new Key."
        return f"Google Error {response.status_code}: {response.text}"


# --- 4. THE APP UI ---
mood = st.text_input("How are you feeling?", placeholder="e.g. Happy, Anxious, Excited")


if st.button("Generate Playlist"):
    if not mood:
        st.warning("Please tell me your mood first!")
    else:
        with st.spinner("Mixing tracks... 🎧"):
            # DJ Instructions
            dj_prompt = (
                f"You are DJ VibeCheck. Recommend 5 songs for this mood: '{mood}'.\n"
                "For EACH song, provide a clickable YouTube Search link in this format:\n"
                "1. **Song Title** - Artist [▶️ Listen](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
                "   *Reason for choosing this song.*"
            )
            
            # Call the function
            result = get_gemini_response(dj_prompt)
            st.markdown(result)



