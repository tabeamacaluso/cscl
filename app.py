import streamlit as st
import random
import os
import urllib.parse
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Dateipfade für den Datenaustausch ---
DATA_FILE = "submissions.json"
STATE_FILE = "app_state.json"

# Die drei auswählbaren Fragen
QUESTIONS = [
    "What is your favorite travel destination and why?",
    "Which programming language do you prefer?",
    "How are you feeling today?"
]

# --- Hilfsfunktionen für Speichern & Laden ---
def load_submissions():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_submission(question, nationality, text):
    data = load_submissions()
    if question not in data:
        data[question] = []
    
    # Speichert Nationalität und Text als Dictionary ab
    data[question].append({
        "nationality": nationality.strip(),
        "text": text.strip()
    })
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_active_question():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("active_question", QUESTIONS[0])
        except:
            return QUESTIONS[0]
    return QUESTIONS[0]

def save_active_question(question):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"active_question": question}, f, ensure_ascii=False, indent=4)

# Streamlit Setup (Breitbild für Beamer)
st.set_page_config(page_title="Interactive Presentation", page_icon="🎲", layout="wide")

# --- ERKENNUNG DER ANSICHT (BEAMER VS. HANDY) ---
query_params = st.query_params
is_phone_view = query_params.get("view") == "phone"

# --- 📱 HANDY-ANSICHT ---
if is_phone_view:
    st.title("📝 Submit Your Answer")
    st.write("---")
    
    # Aktualisiert die Frage alle 2 Sekunden im Hintergrund, falls der Beamer sie wechselt
    @st.fragment(run_every=2)
    def live_question_for_user():
        active_q = load_active_question()
        st.subheader("Current Question:")
        st.info(f"**{active_q}**")
        return active_q

    current_q = live_question_for_user()
    
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
                save_submission(current_q, nationality, answer)
                st.success("Successfully submitted! Watch the presentation screen.")

# --- 🖥️ LAPTOP / BEAMER-ANSICHT ---
else:
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem; margin-bottom: 20px;'>Interactive Presentation Panel</h1>", unsafe_allow_html=True)
    
    # 1. Fragenauswahl oben für den Präsentator
    current_active = load_active_question()
    try:
        start_index = QUESTIONS.index(current_active)
    except ValueError:
        start_index = 0

    selected_q = st.selectbox(
        "Select the active question for your audience:", 
        QUESTIONS, 
        index=start_index
    )
    
    if selected_q != current_active:
        save_active_question(selected_q)
        st.rerun()

    st.markdown("---")
    
    # Zweispaltiges Layout: Links QR-Code & Controls, rechts Live-Wordcloud
    col_left, col_right = st.columns([1, 1.3])
    
    with col_left:
        st.write("### 📲 Scan to Participate")
        st.write("Scan this code with your phone to join and answer:")
        
        # HIER DEINE ECHTE URL EINTRAGEN:
        my_base_url = "https://cujzkogtgshddpta5j2adk.streamlit.app/" 
        app_url = f"{my_base_url}/?view=phone"
        
        # QR-Code über die api.qrserver.com API generieren
        encoded_url = urllib.parse.quote_plus(app_url)
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_url}"
        
        st.image(qr_api_url, width=240)
        st.caption(f"Direct link: [Link]({app_url})")
        st.write("---")
        
        # Controls & Buttons
        st.write("### ⚙️ Controls")
        
        all_data = load_submissions()
        current_answers = all_data.get(selected_q, [])
        st.metric(label="Answers for this question", value=len(current_answers))
        
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("Pick Random 🎲", use_container_width=True, type="primary"):
                if current_answers:
                    winner = random.choice(current_answers)
                    st.balloons()
                    st.session_state.current_winner = winner
                else:
                    st.warning("No answers yet.")
                    
        with btn_col2:
            if st.button("Reset Answers 🗑️", use_container_width=True):
                # Löscht nur die Antworten der AKTUELLEN Frage
                all_data = load_submissions()
                if selected_q in all_data:
                    del all_data[selected_q]
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=4)
                
                if "current_winner" in st.session_state:
                    del st.session_state.current_winner
                st.success("Answers cleared!")
                st.rerun()
        
        # Gewinneranzeige
        if "current_winner" in st.session_state:
            winner = st.session_state.current_winner
            st.markdown(
                f"""
                <div style='border: 2px solid #ff4b4b; padding: 15px; border-radius: 10px; margin-top: 15px; background-color: #fff2f2;'>
                    <h4 style='color: #ff4b4b; margin: 0;'>🎉 Selected Answer:</h4>
                    <p style='font-size: 1.1rem; margin: 5px 0;'>🌍 <b>From:</b> {winner['nationality']}</p>
                    <p style='font-size: 1.2rem; font-style: italic; color: #333;'>"{winner['text']}"</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col_right:
        st.write("### ☁️ Live Word Cloud")
        
        # Aktualisiert die Wordcloud alle 3 Sekunden live
        @st.fragment(run_every=3)
        def live_wordcloud(question):
            all_data = load_submissions()
            current_answers = [ans["text"] for ans in all_data.get(question, [])]
            
            if current_answers:
                # Füge alle Texte zusammen
                text = " ".join(current_answers)
                
                # Wordcloud generieren
                wordcloud = WordCloud(
                    width=800, 
                    height=450, 
                    background_color="white",
                    colormap="viridis",
                    collocations=False
                ).generate(text)
                
                fig, ax = plt.subplots(figsize=(10, 5.5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                plt.tight_layout(pad=0)
                st.pyplot(fig)
            else:
                st.info("Waiting for submissions... The word cloud will appear here once participants send their answers.")
        
        live_wordcloud(selected_q)