import sys
from pathlib import Path
from datetime import datetime
import streamlit as st

# Ensure repository root is on sys.path for shared imports
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from study_data import init_session_state, AVAILABLE_TOPICS, QUESTION_BANK

st.set_page_config(
    page_title="Practice Quiz | AI Study Companion",
    page_icon="📝",
    layout="wide"
)

init_session_state()

# --- Page styling ---
st.markdown("""
<style>
.quiz-header-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.2rem;
}
.score-badge {
    padding: 20px;
    border-radius: 14px;
    text-align: center;
    margin: 1.5rem 0;
}
.score-good { background: #dcfce7; border: 1px solid #86efac; color: #166534; }
.score-avg  { background: #fef9c3; border: 1px solid #fde047; color: #854d0e; }
.score-low  { background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b; }
.review-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="quiz-header-title">📝 Practice & Assessment Quiz</div>', unsafe_allow_html=True)
st.caption("Challenge your recall, understand common pitfalls, and measure your concept retention.")

student = st.session_state.get("student_name", "Student")

# --- Quiz Setup Section ---
with st.container():
    col1, col2, col3 = st.columns([2, 1, 1], gap="medium")
    with col1:
        selected_topic = st.selectbox("Select Study Topic", AVAILABLE_TOPICS)
    with col2:
        selected_diff = st.selectbox("Difficulty Level", ["All Difficulties", "Easy", "Medium", "Hard"])
    with col3:
        target_count = st.slider("Questions", min_value=3, max_value=5, value=5)

# Filter questions based on topic and difficulty
all_topic_questions = QUESTION_BANK.get(selected_topic, [])
if selected_diff != "All Difficulties":
    filtered_questions = [q for q in all_topic_questions if q["difficulty"] == selected_diff]
    if not filtered_questions:
        filtered_questions = all_topic_questions
else:
    filtered_questions = all_topic_questions

filtered_questions = filtered_questions[:target_count]

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🚀 Start New Quiz", use_container_width=True):
        st.session_state["active_quiz"] = {
            "topic": selected_topic,
            "difficulty": selected_diff,
            "questions": filtered_questions,
            "submitted": False,
            "results": None
        }
        st.rerun()

st.divider()

# --- Active Quiz Session Handling ---
quiz_state = st.session_state.get("active_quiz")

if not quiz_state:
    st.info("Select your topic and settings above, then click **Start New Quiz** to begin.")
elif quiz_state.get("submitted") and quiz_state.get("results"):
    # --- Display Evaluation Results ---
    res = quiz_state["results"]
    pct = res["percentage"]

    if pct >= 80:
        badge_class = "score-good"
        message = "🌟 Excellent mastery! You have a strong grasp of these concepts."
    elif pct >= 60:
        badge_class = "score-avg"
        message = "👍 Good effort! A quick review of the missed points will solidify your knowledge."
    else:
        badge_class = "score-low"
        message = "📚 Needs review. Revisit lecture notes and ask the AI Tutor for clarification."

    st.markdown(
        f"""
        <div class="score-badge {badge_class}">
            <h2 style="margin:0;">Score: {res['score']} / {res['total']} ({pct}%)</h2>
            <p style="margin: 8px 0 0 0; font-size:1.05rem;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🔍 Question-by-Question Review")
    for i, item in enumerate(res["eval"]):
        if item["is_correct"]:
            st.success(
                f"**Q{i + 1}: {item['question']}**\n\n"
                f"✓ Your answer: `{item['chosen']}` (Correct)\n\n"
                f"*Explanation:* {item['explanation']}"
            )
        else:
            st.error(
                f"**Q{i + 1}: {item['question']}**\n\n"
                f"✗ Your answer: `{item['chosen']}`\n\n"
                f"**Correct answer:** `{item['correct']}`\n\n"
                f"*Explanation:* {item['explanation']}"
            )

    st.write("")
    c_act1, c_act2, c_act3 = st.columns(3)
    with c_act1:
        if st.button("🔄 Retake or Choose Another Topic", use_container_width=True):
            st.session_state["active_quiz"] = None
            st.rerun()
    with c_act2:
        if st.button("📊 View Progress on Dashboard", use_container_width=True):
            st.switch_page("pages/4_Dashboard.py")
    with c_act3:
        if st.button("💬 Ask Tutor About Missed Concepts", use_container_width=True):
            st.switch_page("pages/2_Chat.py")

else:
    # --- In-Progress Quiz Form ---
    active_questions = quiz_state["questions"]
    st.markdown(f"### 📋 {quiz_state['topic']} Quiz ({len(active_questions)} Questions)")

    with st.form("quiz_submission_form"):
        user_answers = {}

        for i, q in enumerate(active_questions):
            st.markdown(f"**Q{i + 1}: {q['question']}**")
            st.caption(f"Difficulty: {q['difficulty']} • Concept: {q['concept']}")

            user_answers[q["id"]] = st.radio(
                label=f"Options for Q{i + 1}",
                options=range(len(q["options"])),
                format_func=lambda idx, opts=q["options"]: opts[idx],
                key=f"q_radio_{q['id']}",
                label_visibility="collapsed"
            )
            st.write("")

        submitted = st.form_submit_button("🏁 Submit Answers & Check Score", use_container_width=True)

        if submitted:
            correct_count = 0
            weak_concepts = []
            detailed_eval = []

            for q in active_questions:
                chosen = user_answers.get(q["id"])
                is_correct = (chosen == q["answer_index"])
                if is_correct:
                    correct_count += 1
                else:
                    weak_concepts.append(q["concept"])

                detailed_eval.append({
                    "question": q["question"],
                    "chosen": q["options"][chosen] if chosen is not None else "None",
                    "correct": q["options"][q["answer_index"]],
                    "is_correct": is_correct,
                    "explanation": q["explanation"],
                    "concept": q["concept"]
                })

            total = len(active_questions)
            percentage = round((correct_count / total) * 100, 1)

            # Record quiz attempt
            quiz_record = {
                "topic": quiz_state["topic"],
                "difficulty": quiz_state.get("difficulty", "Standard"),
                "score": correct_count,
                "total": total,
                "percentage": percentage,
                "date": datetime.now().strftime("%b %d, %Y"),
                "weak_concepts": weak_concepts
            }
            st.session_state["quiz_history"].append(quiz_record)
            st.session_state["active_quiz"]["submitted"] = True
            st.session_state["active_quiz"]["results"] = {
                "score": correct_count,
                "total": total,
                "percentage": percentage,
                "eval": detailed_eval
            }
            st.rerun()