import streamlit as st
import requests
import json
import base64
import random
import re
import os
import urllib.parse

# ======================================================
# 1. PAGE CONFIG
# ======================================================
st.set_page_config(page_title="VibeChecker AI", page_icon="🎵", layout="wide")

# ======================================================
# 2. BACKGROUND IMAGE
# ======================================================
def get_base64_of_bin_file(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

img_base64 = get_base64_of_bin_file("background.jpeg")
if img_base64:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# 3. CSS
# ======================================================
st.markdown("""
<style>
.song-card { background: white; border-radius: 12px; padding: 15px; margin-bottom: 15px; display: flex; align-items: center; color: #333; }
.song-title { font-size: 18px; font-weight: 800; color: #000; }
.listen-btn { border: 2px solid #00d2ff; color: #00d2ff; padding: 6px 16px; border-radius: 20px; text-decoration: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 4. AUTO-DISCOVERY ENGINE (The Fix)
# ======================================================
def find_working_model(api_key):
    """Asks Google: 'What models can I use?' and picks the best one."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Filter for models that generate text
            valid_models = []
            for m in data.get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    valid_models.append(m['name'])
            
            # Prefer 1.5-flash, then pro, then anything else
            if not valid_models:
                return None
            
            # Return the first valid one found
            return valid_models[0]
            
        return None
    except:
        return None

# ======================================================
# 5. SIDEBAR SETUP
# ======================================================
with st.sidebar:
    st.title("🔧 System Check")
    
    # 1. GET KEY
    manual_key = st.text_input("🔑 Paste 'API Key 3' Here:", type="password")
    if manual_key:
        api_key = manual_key
    elif "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = None

    # 2. FIND MODEL AUTOMATICALLY
    if api_key:
        if "active_model" not in st.session_state or not st.session_state.active_model:
            with st.spinner("Finding best AI model for you..."):
                found_model = find_working_model(api_key)
                if found_model:
                    st.session_state.active_model = found_model
                    st.success(f"✅ Connected to: {found_model}")
                else:
                    st.error("❌ Key works, but no models found.")
        else:
            st.success(f"✅ Connected to: {st.session_state.active_model}")
    else:
        st.warning("Waiting for API Key...")

# ======================================================
# 6. MUSIC GENERATOR
# ======================================================
def get_vibe_check(mood_text):
    if not api_key: return "Please paste API Key first."
    
    # Use the model we discovered automatically
    model_name = st.session_state.get("active_model", "models/gemini-pro")
    
    # If the model name doesn't start with models/, add it (just in case)
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"

    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    
    prompt = f"Recommend 5 songs for mood: {mood_text}. Return valid JSON array with 'title' and 'artist'."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                for song in data:
                    q = urllib.parse.quote_plus(f"{song.get('title')} {song.get('artist')}")
                    song['link'] = f"https://www.youtube.com/results?search_query={q}"
                return data
        return f"Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# ======================================================
# 7. MAIN APP UI
# ======================================================
st.title("🎵 VibeChecker")

with st.form("mood_form"):
    user_input = st.text_input("How are you feeling?", placeholder="Type 'Chill' and press Enter")
    submitted = st.form_submit_button("Analyze Mood")

if submitted and user_input:
    if not api_key:
        st.error("⚠️ Please paste your API Key in the sidebar first!")
    else:
        with st.spinner("Curating playlist..."):
            result = get_vibe_check(user_input)
            
            if isinstance(result, list):
                for song in result:
                    st.markdown(
                        f"""
                        <div class="song-card">
                            <div style="font-size:30px; margin-right:15px;">🎵</div>
                            <div style="flex-grow:1;">
                                <div class="song-title">{song.get("title")}</div>
                                <div>{song.get("artist")}</div>
                            </div>
                            <a class="listen-btn" href="{song.get("link")}" target="_blank">▶ Listen</a>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                st.error(result)
