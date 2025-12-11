import streamlit as st
import requests
import json

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="VibeCheck", page_icon="🎵")
st.title("🎵 VibeCheck")
st.write("Tell me how you feel, and I'll generate a playlist.")

# --- 2. GET API KEY SECURELY ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ API Key missing! Please set GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

# --- 3. THE "DIRECT" FUNCTION (Bypasses the library) ---
def get_gemini_response(prompt):
    # We use the REST API URL directly. This ALWAYS works if the key is valid.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    # Send the request
    response = requests.post(url, headers=headers, json=data)
    
    # Check if successful
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        # If 1.5-flash fails, try the older 'gemini-pro' automatically
        url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        response_fallback = requests.post(url_fallback, headers=headers, json=data)
        
        if response_fallback.status_code == 200:
            return response_fallback.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: {response.text}"

# --- 4. THE APP INTERFACE ---
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
            
            # Call the function
            try:
                result = get_gemini_response(dj_prompt)
                st.markdown(result)
            except Exception as e:
                st.error(f"Connection Error: {e}")
