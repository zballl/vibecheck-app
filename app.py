import streamlit as st
import google.generativeai as genai
import os
import streamlit as st
st.write("👀 Debug Mode: Here are the secrets I can see:")
st.write(st.secrets)

# --- 1. SETUP API KEY SECURELY ---
# We get the key from Streamlit Secrets (not hardcoded!)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Key missing! Set it in Streamlit Secrets.")

# --- 2. APP LOGIC ---
dj_instructions = (
    "You are DJ VibeCheck. Recommend 5 songs based on the mood. "
    "For EACH song, provide a clickable YouTube Search link in this format:\n"
    "1. **Song Title** - Artist [▶️ Listen](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
    "   *Reason for choosing this song.*"
)

# Model setup
try:
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=dj_instructions)
except:
    model = genai.GenerativeModel('gemini-pro')

chat = model.start_chat(history=[])

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="VibeCheck", page_icon="🎵")
st.title("🎵 VibeCheck")
st.write("Tell me how you feel, and I'll generate a playlist.")

mood = st.text_input("Current Mood:", placeholder="e.g. Happy, Stressed, Excited")

if st.button("Generate Playlist"):
    if not mood:
        st.warning("Please enter a mood first!")
    else:
        with st.spinner("Mixing tracks... 🎧"):
            try:
                # Check for system instruction support
                if hasattr(model, 'count_tokens'):
                    response = chat.send_message(mood)
                else:
                    response = chat.send_message(dj_instructions + "\nUser Mood: " + mood)
                st.markdown(response.text)
            except Exception as e:

                st.error(f"Error: {e}")
