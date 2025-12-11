import streamlit as st
import requests
import json

# --- 1. SETUP ---
st.set_page_config(page_title="VibeCheck", page_icon="🎵")
st.title("🎵 VibeCheck")
st.write("Tell me how you feel, and I'll generate a playlist.")

# Get API Key
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ API Key missing! Set GOOGLE_API_KEY in Secrets.")
    st.stop()

# --- 2. THE DIRECT API FUNCTION ---
# This bypasses the library error by calling Google manually
def get_gemini_response(prompt):
    # We try Gemini 1.5 Flash first
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    
    # If 1.5 Flash fails (404), fallback to Gemini Pro
    if response.status_code != 200:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.text}"

# --- 3. THE APP INTERFACE ---
mood = st.text_input("How are you feeling?", placeholder="e.g. Happy, Anxious, Excited")

if st.button("Generate Playlist"):
    if not mood:
        st.warning("Please tell me your mood first!")
    else:
        with st.spinner("Mixing tracks... 🎧"):
            # DJ Instructions
            dj_prompt = (
                "You are DJ VibeCheck. Recommend 5 songs based on this mood: " + mood + "\n"
                "For EACH song, provide a clickable YouTube Search link in this format:\n"
                "1. **Song Title** - Artist [▶️ Listen](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
                "   *Reason for choosing this song.*"
            )
            
            # Call the manual function
            try:
                result = get_gemini_response(dj_prompt)
                st.markdown(result)
            except Exception as e:
                st.error(f"Connection Error: {e}")
