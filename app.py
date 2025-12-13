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
st.set_page_config(page_title="VibeChecker Unlimited", page_icon="🎵", layout="wide")

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
# 4. SIDEBAR (KEY INPUT)
# ======================================================
with st.sidebar:
    st.title("🎧 Control Panel")
    
    # MANUAL KEY OVERRIDE
    manual_key = st.text_input("🔑 Paste 'API Key 3' Here:", type="password")
    
    if manual_key:
        api_key = manual_key
        st.success("✅ Key Loaded")
    elif "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.info("✅ Using Secret Key")
    else:
        api_key = None
        st.warning("⚠️ Waiting for Key...")

# ======================================================
# 5. ROBUST AI CONNECTOR
# ======================================================
def get_vibe_check(mood_text):
    if not api_key: return "Please paste API Key in sidebar."
    
    # ---------------------------------------------------------
    # THE FIX: WE TRY STABLE MODELS FIRST (Avoids the 2.5 limit)
    # ---------------------------------------------------------
    priority_models = [
        "gemini-1.5-flash",          # High Quota (1500/day)
        "gemini-1.5-flash-latest",   # High Quota Backup
        "gemini-1.5-pro",            # Medium Quota
        "gemini-pro"                 # Old Reliable
    ]
    
    prompt = f"Recommend 5 songs for mood: {mood_text}. Return JSON array with 'title' and 'artist'."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    last_error = ""

    # Try each model in order. If one fails, try the next.
    for model in priority_models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            response = requests.post(url, json=payload)
            
            # IF SUCCESS (200 OK)
            if response.status_code == 200:
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                match = re.search(r"\[.*\]", text, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    for song in data:
                        q = urllib.parse.quote_plus(f"{song.get('title')} {song.get('artist')}")
                        song['link'] = f"https://www.youtube.com/results?search_query={q}"
                    return data
            
            # IF QUOTA ERROR (429), just skip to the next model!
            elif response.status_code == 429:
                last_error = f"Quota hit on {model}, switching..."
                continue
            
            else:
                last_error = f"Error {response.status_code} on {model}"
                
        except:
            continue
            
    return f"All models failed. Last error: {last_error}"

# ======================================================
# 6. MAIN APP UI
# ======================================================
st.title("🎵 VibeChecker")

with st.form("mood_form"):
    user_input = st.text_input("How are you feeling?", placeholder="Type 'Happy' and press Enter")
    submitted = st.form_submit_button("Analyze Mood")

if submitted and user_input:
    if not api_key:
        st.error("⚠️ Please paste your API Key in the sidebar!")
    else:
        with st.spinner("Curating playlist (avoiding limits)..."):
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
