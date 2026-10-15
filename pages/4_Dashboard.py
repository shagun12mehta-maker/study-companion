import sys
from pathlib import Path
import streamlit as st

# Ensure repository root is on sys.path for shared imports
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from study_data import init_session_state, calculate_dashboard_metrics

st.set_page_config(
    page_title="Learning Analytics | AI Study Companion",
    page_icon="📊",
    layout="wide"
)

init_session_state()

# Safely load dashboard metrics
metrics = calculate_dashboard_metrics() or {}

materials_count = metrics.get("materials_count", 0)
quizzes_count = metrics.get("quizzes_count", 0)
average_mastery = metrics.get("average_mastery", 0)
streak_days = metrics.get("streak_days", 0)
mastery_breakdown = metrics.get("mastery_breakdown", {})

# --- Page styling ---
st.markdown("""
<style>
.dashboard-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.2rem;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
}
.action-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 1.5rem;
}
.tag-pill {
    background: #fee2e2;
    color: #991b1b;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown(
    '<div class="dashboard-title">📊 Learning Analytics & Growth</div>',
    unsafe_allow_html=True
)

student = st.session_state.get("student_name", "Student")
st.caption(
    f"Personal study metrics for **{student}** • "
    "Updated from your active session"
)

st.divider()

# --- Top Level Performance Metrics ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        label="📚 Study Materials",
        value=materials_count,
        help="Active documents indexed in your study library"
    )

with c2:
    st.metric(
        label="📝 Quizzes Taken",
        value=quizzes_count,
        help="Total assessment attempts logged"
    )

with c3:
    st.metric(
        label="🎯 Average Mastery",
        value=f"{average_mastery}%",
        delta=f"+{average_mastery}%" if average_mastery > 0 else None,
        help="Average score across completed quizzes"
    )

with c4:
    st.metric(
        label="🔥 Study Streak",
        value=f"{streak_days} Days",
        delta="Streak active" if streak_days > 0 else None,
        help="Consecutive days studying with the companion"
    )

st.write("")

# --- Mastery Breakdown & Recommendations ---
col_mastery, col_insights = st.columns([3, 2], gap="large")

with col_mastery:
    st.subheader("🎯 Topic Mastery Breakdown")
    st.caption("Mastery reflects scores across completed quizzes:")

    if mastery_breakdown:
        for topic, score in mastery_breakdown.items():
            score = max(0, min(100, float(score or 0)))

            st.markdown(f"**{topic}**")
            st.progress(score / 100.0)

            if score > 0:
                st.caption(f"Current Mastery: **{score:.0f}%**")
            else:
                st.caption(
                    "No quiz attempts yet • "
                    "*Take a quick test to establish baseline*"
                )
            st.write("")
    else:
        st.info(
            "Topic mastery will appear here after quiz results "
            "are recorded."
        )

with col_insights:
    st.subheader("⚠️ Focus & Review Areas")

    history = st.session_state.get("quiz_history", [])

    recent_weaknesses = []
    for quiz in history:
        for concept in quiz.get("weak_concepts", []):
            if concept not in recent_weaknesses:
                recent_weaknesses.append(concept)

    if recent_weaknesses:
        st.markdown(
            """
            <div class="action-box">
                <h4 style="margin-top:0; color:#b91c1c;">
                    Identified Review Concepts
                </h4>
                <p style="font-size:0.95rem; color:#475569;">
                    Questions on the following topics were recently missed:
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        for concept in recent_weaknesses[:4]:
            safe_concept = (
                str(concept)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            st.markdown(
                f'• <span class="tag-pill">{safe_concept}</span>',
                unsafe_allow_html=True
            )

        st.write("")

        if st.button(
            "💬 Ask Tutor to Explain Missed Concepts",
            use_container_width=True
        ):
            st.switch_page("pages/2_Chat.py")

    else:
        st.info(
            "No review areas recorded yet. Complete a quiz to identify "
            "topics that may need more practice."
        )

# --- Recent Quiz History Table ---
st.divider()
st.subheader("🕒 Recent Quiz History")

if not history:
    st.info(
        "No quiz history recorded yet. Complete a quiz in the "
        "Practice Quiz tab to populate this timeline."
    )
else:
    table_rows = []

    for item in reversed(history[-5:]):
        table_rows.append({
            "Date": item.get("date", "Recent"),
            "Topic": item.get("topic", "General"),
            "Score": (
                f"{item.get('score', 0)} / {item.get('total', 0)}"
            ),
            "Percentage": f"{item.get('percentage', 0)}%",
            "Difficulty": item.get("difficulty", "Standard"),
            "Review Needed": (
                ", ".join(item.get("weak_concepts", []))
                or "None recorded"
            )
        })

    st.dataframe(table_rows, use_container_width=True)

# --- Study Recommendation ---
st.markdown(
    """
    <div style="
        background:#f0fdf4;
        border:1px solid #bbf7d0;
        border-radius:12px;
        padding:16px 20px;
        margin-top:1.5rem;
    ">
        💡 <b>Spaced Repetition Advice:</b>
        Review topics with mastery under 75% within 48 hours.
    </div>
    """,
    unsafe_allow_html=True
)