import random
import streamlit as st

from study_data import init_session_state, AVAILABLE_TOPICS, QUESTION_BANK
from gemini_helper import generate_quiz_questions

st.set_page_config(
    page_title="Quiz | AI Study Companion",
    page_icon="📝",
    layout="wide"
)

init_session_state()

# Session state
defaults = {
    "quiz_questions": [],
    "quiz_submitted": False,
    "quiz_answers": {},
    "quiz_topic": "",
    "quiz_difficulty": "Easy",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def get_fallback_questions(topic, count):
    """Get predefined questions without using an AI API."""
    bank = QUESTION_BANK.get(topic, [])

    if not bank:
        return []

    questions = []

    for item in bank:
        if not isinstance(item, dict):
            continue

        question_text = item.get("question")
        options = item.get("options")

        # Support common answer-key formats.
        answer = item.get("answer", item.get("correct_answer"))
        explanation = item.get("explanation", "")

        if not question_text or not isinstance(options, list):
            continue

        if len(options) != 4:
            continue

        # Support answers stored as option indexes.
        if isinstance(answer, int) and 0 <= answer < len(options):
            answer = options[answer]

        if isinstance(answer, str) and answer.upper() in ("A", "B", "C", "D"):
            answer = options[ord(answer.upper()) - ord("A")]

        if answer not in options:
            continue

        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": explanation,
        })

    random.shuffle(questions)
    return questions[:count]


st.title("📝 AI Quiz")
st.write(
    "Test your knowledge using AI-generated questions "
    "or built-in practice questions."
)

selected_topic = st.selectbox("Select Topic", AVAILABLE_TOPICS)
selected_diff = st.selectbox(
    "Select Difficulty", ["Easy", "Medium", "Hard"]
)
num_questions = st.number_input(
    "Number of Questions",
    min_value=1,
    max_value=10,
    value=5,
    step=1
)

if st.button("Generate Quiz", type="primary"):
    materials = st.session_state.get("uploaded_materials", [])
    topic_texts = []

    for material in materials:
        if not isinstance(material, dict):
            continue

        material_topic = material.get("topic", "")
        content = material.get(
            "extracted_text",
            material.get("text", material.get("content", ""))
        )

        if (
            material_topic == selected_topic
            and isinstance(content, str)
            and content.strip()
        ):
            topic_texts.append(content.strip())

    study_text = "\n\n".join(topic_texts)
    questions = []
    used_fallback = False

    # Try AI first when matching material is available.
    if study_text:
        try:
            with st.spinner("Generating questions with AI..."):
                questions = generate_quiz_questions(
                    topic=selected_topic,
                    study_material=study_text,
                    num_questions=int(num_questions),
                    difficulty=selected_diff
                )
        except Exception as error:
            print("AI quiz unavailable; using fallback:", repr(error))
            used_fallback = True
    else:
        used_fallback = True

    # If AI is unavailable, use built-in questions.
    if not questions:
        questions = get_fallback_questions(
            selected_topic,
            int(num_questions)
        )
        used_fallback = True

    if questions:
        st.session_state["quiz_questions"] = questions
        st.session_state["quiz_topic"] = selected_topic
        st.session_state["quiz_difficulty"] = selected_diff
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_answers"] = {}

        if used_fallback:
            st.warning(
                "Built-in practice questions are being used. "
                "They may not be based on your uploaded PDF."
            )
        else:
            st.success("AI-generated questions are ready!")

    else:
        st.session_state["quiz_questions"] = []
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_submitted"] = False

        st.error(
            f"No usable questions found for '{selected_topic}'. "
            "Check QUESTION_BANK in study_data.py."
        )

questions = st.session_state.get("quiz_questions", [])

if questions:
    st.divider()
    st.subheader(f"Quiz: {st.session_state['quiz_topic']}")
    st.write(f"Difficulty: {st.session_state['quiz_difficulty']}")
    st.write(f"Total Questions: {len(questions)}")

    with st.form("quiz_form"):
        user_answers = {}

        for index, question in enumerate(questions):
            st.markdown(f"### Question {index + 1}")
            st.write(question.get("question", "Question unavailable"))

            options = question.get("options", [])

            if not isinstance(options, list) or not options:
                st.warning("Options are unavailable.")
                continue

            user_answers[index] = st.radio(
                "Choose your answer:",
                options,
                key=f"question_{index}",
                index=None
            )
            st.divider()

        submitted = st.form_submit_button("Submit Quiz")

    if submitted:
        st.session_state["quiz_answers"] = user_answers
        st.session_state["quiz_submitted"] = True

    if st.session_state.get("quiz_submitted"):
        answers = st.session_state.get("quiz_answers", {})
        score = 0
        total = len(questions)

        st.divider()
        st.header("📊 Your Results")

        for index, question in enumerate(questions):
            correct_answer = question.get("answer", "")
            user_answer = answers.get(index)

            st.markdown(f"**Question {index + 1}**")
            st.write(question.get("question", "Question unavailable"))

            if (
                isinstance(user_answer, str)
                and isinstance(correct_answer, str)
                and user_answer.strip().casefold()
                == correct_answer.strip().casefold()
            ):
                score += 1
                st.success("✅ Correct answer!")
            else:
                st.error("❌ Incorrect answer")
                st.write(f"Your answer: {user_answer or 'Not answered'}")
                st.info(f"Correct answer: {correct_answer}")

            explanation = question.get("explanation", "")
            if explanation:
                st.write(f"💡 Explanation: {explanation}")

            st.divider()

        percentage = (score / total * 100) if total else 0

        st.subheader("🏆 Final Score")
        col1, col2, col3 = st.columns(3)

        col1.metric("Your Score", f"{score}/{total}")
        col2.metric("Correct Answers", score)
        col3.metric("Percentage", f"{percentage:.1f}%")

        st.progress(percentage / 100)

        if percentage >= 80:
            st.success("🎉 Excellent! You have performed really well!")
        elif percentage >= 50:
            st.info("👍 Good job! Keep practising to improve your score.")
        else:
            st.warning(
                "💪 Keep learning! Revise your study material and try again."
            )

        if st.button("🔄 Retake Quiz"):
            st.session_state["quiz_submitted"] = False
            st.session_state["quiz_answers"] = {}
            st.rerun()