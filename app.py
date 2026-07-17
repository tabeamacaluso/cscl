import streamlit as st
import random
import os
import urllib.parse

# Datei, in der die Antworten auf dem Server gespeichert werden
DATA_FILE = "submissions.txt"

# Hilfsfunktionen zum Lesen und Schreiben der geteilten Datei
def load_submissions():
    if not os.path.exists(DATA_FILE):
        return []
    submissions = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "||" in line:
                parts = line.split("||")
                if len(parts) == 2:
                    submissions.append({"nationality": parts[0], "text": parts[1]})
    return submissions

def save_submission(nationality, text):
    safe_nationality = nationality.replace("\n", " ").replace("||", " ").strip()
    safe_text = text.replace("\n", " ").replace("||", " ").strip()
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{safe_nationality}||{safe_text}\n")

# Streamlit Setup
st.set_page_config(page_title="Interactive Q&A", page_icon="🎲", layout="wide")

# --- ERKENNUNG DER ANSICHT (BEAMER VS. HANDY) ---
query_params = st.query_params
is_phone_view = query_params.get("view") == "phone"

# --- 📱 HANDY-ANSICHT ---
if is_phone_view:
    st.title("📝 Submit Your Answer")
    st.write("---")
    
    with st.form("survey_form", clear_on_submit=True):
        nationality = st.text_input("Your Nationality:", placeholder="e.g., German, Spanish, French...")
        answer = st.text_area("Your Answer:", placeholder="Type your answer here...")
        submitted = st.form_submit_button("Send Answer 🚀")
        
        if submitted:
            if not nationality.strip():
                st.error("Please enter your nationality!")
            elif not answer.strip():
                st.error("Please enter your answer!")
            else:
                save_submission(nationality, answer)
                st.success("Successfully submitted! Watch the presentation screen.")

# --- 🖥️ LAPTOP / BEAMER-ANSICHT ---
else:
    # 1. Große Frage ganz oben
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Today's Big Question:</h1>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: #f0f2f6; padding: 25px; border-radius: 10px; text-align: center; margin-bottom: 30px;'><h2 style='font-size: 2.2rem; color: #1f77b4; margin: 0;'>\"What is your favorite travel destination and why?\"</h2></div>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        st.write("### 📲 Scan to Participate")
        st.write("Scan this code with your smartphone to join the session:")
        
        # HIER DEINE ECHTE URL EINTRAGEN:
        # Ersetze das hier nach dem Deployen mit z.B.: "https://dein-projekt.streamlit.app"
        my_base_url = "[https://cscl.streamlit.app](https://cscl.streamlit.app)"
        
        app_url = f"{my_base_url}/?view=phone"
        
        # QR-Code über die kostenlose Google Chart API generieren (Keine Installation nötig!)
        encoded_url = urllib.parse.quote_plus(app_url)
        qr_api_url = f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={encoded_url}&choof=utf-8"
        
        # Bild direkt via URL anzeigen
        st.image(qr_api_url, width=280)
        st.caption(f"Direct link: {app_url}")
        
    with col_right:
        st.write("### 📊 Live Stats & Controls")
        
        all_answers = load_submissions()
        st.metric(label="Answers Received", value=len(all_answers))
        st.write("---")
        
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("Pick a Random Answer 🎲", use_container_width=True, type="primary"):
                if all_answers:
                    winner = random.choice(all_answers)
                    st.balloons()
                    st.session_state.current_winner = winner
                else:
                    st.warning("No answers submitted yet.")
                    
        with btn_col2:
            if st.button("Reset All Answers 🗑️", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                if "current_winner" in st.session_state:
                    del st.session_state.current_winner
                st.success("All answers cleared!")
                st.rerun()

        if "current_winner" in st.session_state:
            winner = st.session_state.current_winner
            st.markdown(
                f"""
                <div style='border: 2px solid #ff4b4b; padding: 20px; border-radius: 10px; margin-top: 20px; background-color: #fff2f2;'>
                    <h3 style='color: #ff4b4b; margin-top: 0;'>🎉 Selected Answer:</h3>
                    <p style='font-size: 1.2rem; margin-bottom: 8px;'>🌍 <b>Nationality:</b> {winner['nationality']}</p>
                    <p style='font-size: 1.4rem; font-style: italic; color: #333;'>"{winner['text']}"</p>
                </div>
                """, 
                unsafe_allow_html=True
            )