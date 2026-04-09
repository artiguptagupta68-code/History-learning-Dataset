import streamlit as st
import pandas as pd
import joblib
import random

import os
import urllib.request

if not os.path.exists("model.pkl"):
    url = "PASTE_DIRECT_DOWNLOAD_LINK"
    urllib.request.urlretrieve(url, "model.pkl")

bundle = joblib.load("model.pkl")
model = bundle["model"]
encoders = bundle["encoders"]
target_encoder = bundle["target_encoder"]
features = bundle["features"]

# Load dataset
df = pd.read_csv("gamified_history_dataset_500.csv")

question_df = df[[
    'event_name','topic','difficulty_level',
    'content_type','question','correct_answer'
]].drop_duplicates()

# ------------------------
# Functions
# ------------------------

def get_question():
    row = question_df.sample(1).iloc[0]
    return row.to_dict()

def evaluate_answer(user_answer, correct_answer, content_type):
    user_answer = user_answer.lower().strip()
    correct_answer = correct_answer.lower().strip()

    if content_type == "Quiz":
        return int(user_answer == correct_answer)
    elif content_type == "Simulation":
        return int(correct_answer in user_answer)
    elif content_type == "Challenge":
        keywords = correct_answer.split()
        match = sum([1 for word in keywords if word in user_answer])
        return int(match >= len(keywords)*0.5)
    return 0

def generate_feedback(is_correct):
    if is_correct:
        return "✅ Great job! Ready for next level."
    else:
        return "❌ Review this topic and try again."

def predict(sample):
    input_df = pd.DataFrame([sample])

    for col in encoders:
        try:
            input_df[col] = encoders[col].transform(input_df[col])
        except:
            input_df[col] = 0

    pred = model.predict(input_df[features])
    return target_encoder.inverse_transform(pred)[0]

# ------------------------
# UI
# ------------------------

st.title("📚 AI Gamified History Learning")

# User Profile
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
            'event_name': q['event_name'],
            'topic': q['topic'],
            'difficulty_level': q['difficulty_level'],
            'content_type': q['content_type'],
            'accuracy_flag': is_correct,
            'fast_response': 1,
            'used_hint': 0,
            'attempts': 1
        }

        difficulty = predict(sample)
        feedback = generate_feedback(is_correct)

        st.write("### Result")
        st.write("Correct Answer:", q['correct_answer'])
        st.write("Your Answer:", answer)
        st.write("Recommended Level:", difficulty)
        st.write("Feedback:", feedback)
