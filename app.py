If gibberish, return JSON: [{'error': 'invalid'}]\n"
        "2. Else, return JSON list of 5 songs (title, artist, link).\n"
        "OUTPUT JSON ONLY."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"
            
        try:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                clean_json = match.group(0)
                return json.loads(clean_json)
            else:
                return "Error: Could not find JSON data in response."
                
        except Exception as e:
            return f"Parsing Error: {str(e)}"
            
    except Exception as e:
        return f"Connection Error: {str(e)}"

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("🎧 Control Panel")
    st.info("VibeChecker AI")
    
    if st.button("🎲 Surprise Me"):
        vibe = random.choice(["Energetic", "Chill", "Melancholy", "Dreamy"])
        st.session_state.current_mood = vibe
        st.session_state.playlist = None  # Clear old
        st.session_state.error_debug = None
        
        with st.spinner(f"Curating {vibe}..."):
            result = get_vibe_check(vibe)
            if isinstance(result, list):
                st.session_state.playlist = result
            else:
                st.session_state.error_debug = result
        st.rerun()

    if st.button("🔄 Reset App"):
        st.session_state.playlist = None
        st.session_state.current_mood = ""
        st.session_state.error_debug = None
        st.session_state.questions_asked = False
        st.rerun()

# --- 8. MAIN UI ---
st.markdown('<p class="title-text">🎵 VibeChecker</p>', unsafe_allow_html=True)

# Mood Selection Buttons
c1, c2, c3, c4 = st.columns(4)
b1 = c1.button("⚡ Energetic")
b2 = c2.button("☂️ Melancholy")
b3 = c3.button("🧘 Chill")
b4 = c4.button("💔 Heartbroken")

# "Not Sure How I Feel" Button (Main UI)
not_sure_button = st.button("🤔 Not Sure How I Feel")

# Button Logic for Mood Selection
if b1:
    st.session_state.current_mood = "Energetic"
    with st.spinner(f"Analyzing mood: Energetic..."):
        result = get_vibe_check("Energetic")
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error_debug = result

if b2:
    st.session_state.current_mood = "Melancholy"
    with st.spinner(f"Analyzing mood: Melancholy..."):
        result = get_vibe_check("Melancholy")
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error_debug = result

if b3:
    st.session_state.current_mood = "Chill"
    with st.spinner(f"Analyzing mood: Chill..."):
        result = get_vibe_check("Chill")
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error_debug = result

if b4:
    st.session_state.current_mood = "Heartbroken"
    with st.spinner(f"Analyzing mood: Heartbroken..."):
        result = get_vibe_check("Heartbroken")
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error_debug = result

# "Not Sure How I Feel" - Trigger Questions Logic
if not_sure_button and not st.session_state.questions_asked:
    st.session_state.questions_asked = True

# Display questions only after button is clicked
if st.session_state.questions_asked:
    q1 = st.selectbox("1. How do you feel physically?", ["Energetic", "Tired", "Neutral", "Weak"], index=["Energetic", "Tired", "Neutral", "Weak"].index(st.session_state.q1))
    q2 = st.selectbox("2. How do you feel emotionally?", ["Happy", "Sad", "Anxious", "Relaxed"], index=["Happy", "Sad", "Anxious", "Relaxed"].index(st.session_state.q2))
    q3 = st.selectbox("3.How do you feel mentally?", ["Focused", "Distracted", "Overwhelmed", "Calm"], index=["Focused", "Distracted", "Overwhelmed", "Calm"].index(st.session_state.q3))

    # Save selected values to session state for next time
    st.session_state.q1 = q1
    st.session_state.q2 = q2
    st.session_state.q3 = q3

    # Trigger mood analysis after all questions are answered
    if st.button("Analyze Mood"):
        # Logic to determine mood based on responses
        if "Energetic" in q1 and "Happy" in q2 and "Focused" in q3:
            target_mood = "Energetic"
        elif "Tired" in q1 and "Sad" in q2:
            target_mood = "Melancholy"
        elif "Relaxed" in q2 and "Calm" in q3:
            target_mood = "Chill"
        else:
            target_mood = "Neutral"

        st.session_state.current_mood = target_mood
        st.session_state.playlist = None  # Clear old
        st.session_state.error_debug = None

        with st.spinner(f"Analyzing mood: {target_mood}..."):
            result = get_vibe_check(target_mood)
            if isinstance(result, list):
                st.session_state.playlist = result
            else:
                st.session_state.error_debug = result
        st.rerun()

# --- 9. USER INPUT FOR MOOD ---
user_input = st.text_input("Or type your exact mood here...")

if user_input:
    st.session_state.current_mood = user_input  # Update mood with user input
    st.session_state.playlist = None  # Clear old playlist
    st.session_state.error_debug = None  # Clear any errors

    with st.spinner(f"Analyzing mood: {user_input}..."):
        result = get_vibe_check(user_input)
        if isinstance(result, list):
            st.session_state.playlist = result
        else:
            st.session_state.error_debug = result

    st.rerun()

# --- 10. DISPLAY RESULTS ---

# Show Error (if any)
if st.session_state.error_debug:
    st.error(st.session_state.error_debug)

# Show Playlist (if valid)
if st.session_state.playlist:
    st.write("---")
    st.markdown(f"### 🎶 Recommended for {st.session_state.current_mood}")
    
    emojis = ["🎵", "🎸", "🎹", "🎷", "🎧"]
    for song in st.session_state.playlist:
        emo = random.choice(emojis)
        st.markdown(f"""
        <div class="song-card">
            <div class="album-art">{emo}</div>
            <div class="song-info">
                <div class="song-title">{song.get('title','Track')}</div>
                <div class="song-artist">{song.get('artist','Artist')}</div>
            </div>
            <a href="{song.get('link','https://www.youtube.com')}" target="_blank" class="listen-btn">▶️ Listen</a>
        </div>
        """, unsafe_allow_html=True)
