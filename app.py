import streamlit as st
st.title("✅ SUCCESS: The app is updating!")
st.write("If you see this, the connection to GitHub is working.")
st.write(f"My Secret Key starts with: {st.secrets['GOOGLE_API_KEY'][:5]}...")
