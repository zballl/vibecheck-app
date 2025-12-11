import streamlit as st
import google.generativeai as genai
import os

# --- 1. SETUP API KEY ---
# We get the key securely from Streamlit Secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Key missing! Please go to 'Settings > Secrets' and set GOOGLE_API_KEY.")

# --- 2. DJ INSTRUCTIONS ---
dj_instructions = (
    "You are DJ VibeCheck. Recommend 5 songs based on the mood. "
    "For EACH song, provide a clickable YouTube Search link in this format:\n"
    "1. **Song Title** - Artist [▶️ Listen](https://www.youtube.com/results?search_query=Song+Title+Artist)\n"
    "   *Reason for choosing this song.*"
)

# --- 3. MODEL SETUP (Using 'gemini-pro') ---
# We use 'gemini-pro' because it is 100% compatible with Streamlit Cloud
try:
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    # Send instructions immediately since Pro doesn't support 'system_instructions' nicely in old versions
    chat.send_message(dj_instructions) 
except Exception as e:
    st.error(f"Model Error: {e}")

# --- 4. THE APP INTERFACE ---
st.set_page_config(page_title="VibeCheck", page_icon="🎵")
st.title("🎵 VibeCheck")
st.write("Tell me how you feel, and I'll generate a playlist.")

mood = st.text_input("How are you feeling?", placeholder="e.g. Happy, Anxious, Excited")

if st.button("Generate Playlist"):
    if not mood:
        st.warning("Please tell me your mood first!")
    else:
        with st.spinner("Mixing tracks... 🎧"):
            try:
                # Add a prompt prefix to remind it to act like a DJ
                prompt = f"{dj_instructions}\n\nUser Mood: {mood}"
                response = chat.send_message(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
