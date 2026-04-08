import streamlit as st
import pandas as pd
import joblib

# -------------------------
# Load Model + Assets
# -------------------------
@st.cache_resource
def load_model():
    bundle = joblib.load("model.pkl")
    return bundle

bundle = load_model()
model = bundle["model"]
encoders = bundle["encoders"]
target_encoder = bundle["target_encoder"]
features = bundle["features"]

# -------------------------
# Load Dataset
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("history_gamified_dataset_production_15000.csv")
    df = df[[
        'event_name','topic','difficulty_level',
        'content_type','question','correct_answer'
    ]].drop_duplicates()
    return df

question_df = load_data()

# -------------------------
# Functions
# -------------------------
def get_question():
    return question_df.sample(1).iloc[0].to_dict()

def evaluate_answer(user_answer, correct_answer, content_type):
    user_answer = user_answer.lower().strip()
    correct_answer = correct_answer.lower().strip()

    if content_type == "Quiz":
        return int(user_answer == correct_answer)

    elif content_type == "Simulation":
        return int(correct_answer in user_answer)

    elif content_type == "Challenge":
        keywords = correct_answer.split()
        match = sum(word in user_answer for word in keywords)
        return int(match >= len(keywords) * 0.5)

    return 0

def generate_feedback(is_correct, attempts, used_hint):
    if is_correct:
        if attempts == 1 and used_hint == 0:
            return "🌟 Excellent! You're mastering this topic."
        elif used_hint == 1:
            return "👍 Good job! Try solving without hints next time."
        else:
            return "✅ Well done! Keep progressing."
    else:
        if attempts > 2:
            return "📘 You seem to be struggling. Let's revise basics."
        elif used_hint == 1:
            return "💡 Hints helped. Try reviewing the concept."
        else:
            return "❌ Incorrect. Review and try again."

def predict(sample):
    input_df = pd.DataFrame([sample])

    # Encode safely
    for col in encoders:
        if col in input_df.columns:
            try:
                input_df[col] = encoders[col].transform(input_df[col])
            except:
                input_df[col] = 0  # unseen category fallback

    input_df = input_df[features]

    pred = model.predict(input_df)
    return target_encoder.inverse_transform(pred)[0]

# -------------------------
# UI
# -------------------------
st.set_page_config(page_title="AI History Learning", layout="centered")

st.title("📚 AI Gamified History Learning Platform")

# User Profile
st.sidebar.header("👤 User Profile")

age = st.sidebar.selectbox("Age Group", ["Child", "Teen", "Adult"])
level = st.sidebar.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
used_hint = st.sidebar.selectbox("Used Hint?", [0, 1])
attempts = st.sidebar.slider("Attempts", 1, 3, 1)
fast_response = st.sidebar.selectbox("Fast Response?", [0, 1])

# Initialize session
if "question" not in st.session_state:
    st.session_state.question = None

# Get Question
if st.button("🎯 Get Question"):
    st.session_state.question = get_question()

# Display Question
if st.session_state.question:
    q = st.session_state.question

    st.subheader(f"📌 {q['question']}")
    st.caption(f"Type: {q['content_type']} | Topic: {q['topic']}")

    user_answer = st.text_input("✏️ Your Answer")

    if st.button("Submit Answer"):

        is_correct = evaluate_answer(
            user_answer,
            q['correct_answer'],
            q['content_type']
        )

        sample = {
            'age_group': age,
            'proficiency_level': level,
            'event_name': q['event_name'],
            'topic': q['topic'],
            'difficulty_level': q['difficulty_level'],
            'content_type': q['content_type'],
            'accuracy_flag': is_correct,
            'fast_response': fast_response,
            'used_hint': used_hint,
            'attempts': attempts
        }

        difficulty = predict(sample)
        feedback = generate_feedback(is_correct, attempts, used_hint)

        # Output
        st.markdown("### 🤖 Result")
        st.write("✅ Correct Answer:", q['correct_answer'])
        st.write("🧠 Your Answer:", user_answer)
        st.write("🎯 Recommended Level:", difficulty)
        st.write("💬 Feedback:", feedback)

# Footer
st.markdown("---")
st.caption("🚀 AI-powered adaptive learning system")
