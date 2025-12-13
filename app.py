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
st.set_page_config(page_title="VibeChecker Debugger", page_icon="🔧", layout="wide")

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
# 4. SIDEBAR (THE FIX)
# ======================================================
with st.sidebar:
    st.title("🔧 Diagnostics Mode")
    st.write("Let's force the app to use the correct key.")
    
    # MANUAL INPUT - This overrides the secret file
    manual_key = st.text_input("👉 Paste 'API Key 3' here:", type="password")
    
    # Logic to pick the key
    if manual_key:
        api_key = manual_key
        st.success("Using Manual Key")
    elif "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.info("Using Key from Secrets file")
    else:
        api_key = None
        st.error("No key found.")

    # Show which key is active (First 8 chars only)
    if api_key:
        st.code(f"Active Key: {api_key[:8]}...")
        if api_key.startswith("AIzaSyCk"):
            st.error("❌ STOP! This is the MAPS key. It will not work.")
            st.error("Please paste the key starting with 'AIzaSyB6'")

# ======================================================
# 5. DIAGNOSTIC CONNECTOR
# ======================================================
def get_vibe_check_debug(mood_text):
    if not api_key:
        return "⚠️ No API Key provided."

    # We try the standard Flash model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"Recommend 5 songs for mood: {mood_text}. Return valid JSON."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        
        # IF IT WORKS
        if response.status_code == 200:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                for song in data:
                    q = urllib.parse.quote_plus(f"{song.get('title')} {song.get('artist')}")
                    song['link'] = f"https://www.youtube.com/results?search_query={q}"
                return data
                
        # IF IT FAILS - RETURN THE REAL REASON
        else:
            return f"❌ GOOGLE ERROR ({response.status_code}):\n{response.text}"
            
    except Exception as e:
        return f"❌ CONNECTION ERROR: {str(e)}"

# ======================================================
# 6. MAIN APP
# ======================================================
st.title("🎵 VibeChecker (Debug)")

with st.form("mood_form"):
    user_input = st.text_input("How are you feeling?", placeholder="Type 'Happy' and hit Enter")
    submitted = st.form_submit_button("Analyze Mood")

if submitted and user_input:
    with st.spinner("Testing connection..."):
        result = get_vibe_check_debug(user_input)
        
        if isinstance(result, list):
            st.success("✅ IT WORKS! Here is your playlist:")
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
            # SHOW THE RAW ERROR
            st.error("👇 READ THIS ERROR CAREFULLY 👇")
            st.code(result)
