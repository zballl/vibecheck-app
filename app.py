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
st.set_page_config(page_title="VibeChecker Auto-Fix", page_icon="🎵", layout="wide")

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
# 4. SIDEBAR - KEY INPUT
# ======================================================
with st.sidebar:
    st.title("🎧 Control Panel")
    
    # Allow manual key entry to override secrets
    manual_key = st.text_input("🔑 Paste 'API Key 3' Here:", type="password")
    
    if manual_key:
        api_key = manual_key
        st.success("✅ Using Manual Key")
    elif "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.info("✅ Using Secret Key")
    else:
        api_key = None
        st.warning("⚠️ Waiting for Key...")

# ======================================================
# 5. THE AUTO-DISCOVERY ENGINE (NO MORE 404s)
# ======================================================
def get_valid_model(key):
    """
    Asks Google for the list of available models and picks the best one.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # We look for models that support 'generateContent'
            for model in data.get('models', []):
                name = model.get('name')
                methods = model.get('supportedGenerationMethods', [])
                
                # Prefer the standard Flash model if available (it has high limits)
                if 'generateContent' in methods and 'flash' in name and 'gemini' in name:
                    return name
            
            # If no Flash found, take ANY gemini model that works
            for model in data.get('models', []):
                name = model.get('name')
                if 'generateContent' in model.get('supportedGenerationMethods', []) and 'gemini' in name:
                    return name
                    
        return None
    except:
        return None

# ======================================================
# 6. MUSIC GENERATOR
# ======================================================
def get_vibe_check(mood_text):
    if not api_key: return "Please paste API Key first."
    
    # STEP 1: Find a model that actually exists for this key
    model_name = get_valid_model(api_key)
    
    if not model_name:
        return "Error: Could not find ANY working model for this API key. Check permissions."

    # STEP 2: Use that exact model name
    # model_name already looks like "models/gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    
    prompt = f"Recommend 5 songs for mood: {mood_text}. Return JSON array with 'title' and 'artist'."
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
        elif response.status_code == 429:
            return "Quota Limit Reached. Please try again tomorrow or use a new key."
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Connection Error: {str(e)}"

# ======================================================
# 7. MAIN UI
# ======================================================
st.title("🎵 VibeChecker")

if api_key:
    # Small check to see if we are connected
    with st.sidebar:
        if st.button("Test Connection"):
            found = get_valid_model(api_key)
            if found:
                st.success(f"Connected to: {found}")
            else:
                st.error("Connection failed.")

with st.form("mood_form"):
    user_input = st.text_input("How are you feeling?", placeholder="Type 'Happy' and press Enter")
    submitted = st.form_submit_button("Analyze Mood")

if submitted and user_input:
    if not api_key:
        st.error("⚠️ Please paste your API Key in the sidebar!")
    else:
        with st.spinner("Finding the best model & curating tracks..."):
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
