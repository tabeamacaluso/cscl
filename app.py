import streamlit as st
import random
import os

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
    # Ersetze Zeilenumbüche im Text, damit das Dateiformat sauber bleibt
    safe_text = text.replace("\n", " ").replace("||", " ")
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nationality}||{safe_text}\n")

# Streamlit Layout
st.set_page_config(page_title="Interactive Q&A", page_icon="🎲")
st.title("Interactive Presentation")

# --- USER SECTION (What people see on their phones) ---
st.write("### 📝 Submit Your Answer")
st.info("**Question:** What is your favorite travel destination and why?")

with st.form("survey_form", clear_on_submit=True):
    nationality = st.selectbox(
        "Your Nationality:", 
        ["Germany", "Austria", "Switzerland", "Spain", "Italy", "France", "USA", "United Kingdom", "Turkey", "Other"]
    )
    answer = st.text_area("Your Answer:", placeholder="Type your answer here...")
    submitted = st.form_submit_button("Send Answer 🚀")
    
    if submitted:
        if answer.strip() == "":
            st.error("Please enter an answer before submitting!")
        else:
            save_submission(nationality, answer)
            st.success("Successfully submitted! Watch the presentation screen.")

st.write("---")

# --- ADMIN SECTION (What you show on the projector/beamer) ---
st.write("### 🖥️ Admin Console (Projector View)")

# Lade die aktuellen Antworten live aus der gemeinsamen Datei
all_answers = load_submissions()
st.write(f"Total answers received so far: **{len(all_answers)}**")

# Button, um die Antworten zurückzusetzen (falls du die App neu starten willst)
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Pick a Random Answer 🎲", use_container_width=True):
        if all_answers:
            winner = random.choice(all_answers)
            st.balloons()
            st.info(f"🌍 **Nationality:** {winner['nationality']}\n\n💬 **Answer:** {winner['text']}")
        else:
            st.warning("No answers submitted yet.")

with col2:
    if st.button("Reset All Answers 🗑️", use_container_width=True):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.success("All answers cleared!")
        st.rerun()