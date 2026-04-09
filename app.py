import streamlit as st
import pandas as pd
import joblib
import random
import os

st.title("📚 AI Gamified History Learning")

# ------------------------
# Debug check
# ------------------------
st.write("Files:", os.listdir())

# ------------------------
# Load model safely
# ------------------------
if not os.path.exists("model.pkl"):
    st.error("❌ model.pkl not found")
    st.stop()

bundle = joblib.load("model.pkl")
model = bundle["model"]
encoders = bundle["encoders"]
target_encoder = bundle["target_encoder"]
features = bundle["features"]

# ------------------------
# Load dataset
# ------------------------
if not os.path.exists("gamified_history_dataset_500.csv"):
    st.error("❌ Dataset not found")
    st.stop()

df = pd.read_csv("gamified_history_dataset_500.csv")

question_df = df[[
    'event_name','topic','difficulty_level',
    'content_type','question','correct_answer'
]].drop_duplicates()

# ------------------------
# Functions
# ------------------------

def get_question():
    return question_df.sample(1).iloc[0].to_dict()

def evaluate_answer(user_answer, correct_answer, content_type):
    user_answer = user_answer.lower().strip()
    correct_answer = correct_answer.lower().strip()

    if content_type == "MCQ":
        return int(user_answer == correct_answer)
    elif content_type == "True-False":
        return int(user_answer == correct_answer)
    elif content_type == "Short":
        return int(correct_answer in user_answer)
    return 0

def predict(sample):
    input_df = pd.DataFrame([sample])

    for col in encoders:
        if col in input_df:
            try:
                input_df[col] = encoders[col].transform(input_df[col])
            except:
                input_df[col] = 0

    pred = model.predict(input_df[features])
    return target_encoder.inverse_transform(pred)[0]

def generate_feedback(is_correct):
    return "✅ Great job!" if is_correct else "❌ Try again!"

# ------------------------
# UI
# ------------------------

age = st.selectbox("Age Group", ["Child", "Teen", "Adult"])
level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])

if st.button("🎯 Get Question"):
    st.session_state.q = get_question()

if "q" in st.session_state:
    q = st.session_state.q

    st.subheader(q['question'])
    answer = st.text_input("Your Answer")

    if st.button("Submit"):
        is_correct = evaluate_answer(answer, q['correct_answer'], q['content_type'])

        sample = {
    'age_group': age,
    'proficiency_level': level,
    'topic': q['topic'],
    'difficulty_level': q['difficulty_level'],
    'content_type': q['content_type'],
    'response_time_sec': 10,
    'is_correct': is_correct,   
    'hint_used': 0,
    'attempts': 1,
    'score': 50,
    'engagement_level': "Medium"

    }
        difficulty = predict(sample)

        st.write("### Result")
        st.write("Correct Answer:", q['correct_answer'])
        st.write("Your Answer:", answer)
        st.write("Recommended Level:", difficulty)
        st.write("Feedback:", generate_feedback(is_correct))
