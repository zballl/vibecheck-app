import streamlit as st
import requests

st.title("🔧 VibeCheck Diagnostic Tool")

# 1. Get the Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ API Key found in Secrets.")
except:
    st.error("❌ API Key missing.")
    st.stop()

# 2. Ask Google what models are available
st.write("Testing connection to Google...")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    st.success("✅ Connection Successful! Here are the models your Key can access:")
    models = response.json().get('models', [])
    found_gemini = False
    
    for m in models:
        # Check if we have gemini-pro or gemini-1.5-flash
        if 'gemini' in m['name']:
            st.write(f"- `{m['name']}`")
            found_gemini = True
    
    if found_gemini:
        st.balloons()
        st.info("👇 **NEXT STEP:** Go back to GitHub and paste the 'Final Working Code' I gave you previously. It will work now!")
    else:
        st.warning("⚠️ Connected to Google, but no Gemini models found. (Region locked?)")

else:
    st.error(f"❌ Connection Failed. Error {response.status_code}:")
    st.code(response.text)
    st.write("This means the API Key is invalid or the API is disabled for this project.")
