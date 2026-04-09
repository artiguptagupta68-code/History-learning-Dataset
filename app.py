import streamlit as st
import pandas as pd
import random

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Ancient_Civilizations_50Q_Dataset.xlsx", skiprows=1)
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates(subset=['Question'])
    df = df.dropna(subset=['Question'])
    return df

df = load_data()

# -----------------------------
# INIT SESSION STATE
# -----------------------------
if "score" not in st.session_state:
    st.session_state.score = 0

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "questions" not in st.session_state:
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)

if "selected" not in st.session_state:
    st.session_state.selected = None

if "answered" not in st.session_state:
    st.session_state.answered = False

# -----------------------------
# APP UI
# -----------------------------
st.title("🏛️ Ancient Civilizations Quiz Game")

TOTAL_QUESTIONS = min(10, len(df))

# End game
if st.session_state.q_index >= TOTAL_QUESTIONS:
    st.success(f"🎯 Game Over! Your Score: {st.session_state.score}/{TOTAL_QUESTIONS}")
    
    if st.button("🔄 Restart"):
        st.session_state.score = 0
        st.session_state.q_index = 0
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
        st.session_state.answered = False
        st.rerun()
    
    st.stop()

# -----------------------------
# CURRENT QUESTION
# -----------------------------
row = st.session_state.questions.iloc[st.session_state.q_index]

st.subheader(f"Q{st.session_state.q_index + 1}: {row['Question']}")
st.caption(f"🌍 {row['Civilization']} | ⚡ {row['Difficulty']}")

# Options
options = {
    "A": row.get("Option A"),
    "B": row.get("Option B"),
    "C": row.get("Option C"),
    "D": row.get("Option D"),
}

# Remove None values
options = {k: v for k, v in options.items() if pd.notna(v)}

# Radio buttons
choice = st.radio("Choose your answer:", list(options.keys()),
                  format_func=lambda x: f"{x}. {options[x]}")

# -----------------------------
# SUBMIT BUTTON
# -----------------------------
if st.button("Submit Answer") and not st.session_state.answered:
    
    st.session_state.answered = True
    correct = str(row['Correct Answer']).strip().upper()
    
    if choice == correct:
        st.success("✅ Correct!")
        st.session_state.score += 1
    else:
        st.error(f"❌ Wrong! Correct Answer: {correct}")
    
    # Explanation
    st.info(f"📘 Explanation: {row['Explanation']}")

# -----------------------------
# NEXT BUTTON
# -----------------------------
if st.session_state.answered:
    if st.button("Next Question"):
        st.session_state.q_index += 1
        st.session_state.answered = False
        st.rerun()

# -----------------------------
# SCORE DISPLAY
# -----------------------------
st.sidebar.header("📊 Score")
st.sidebar.write(f"{st.session_state.score} / {TOTAL_QUESTIONS}")
