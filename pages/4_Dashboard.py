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
metrics = calculate_dashboard_metrics()

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
st.markdown('<div class="dashboard-title">📊 Learning Analytics & Growth</div>', unsafe_allow_html=True)
student = st.session_state.get("student_name", "Student")
st.caption(f"Personal study metrics for **{student}** • Updated in real-time from your active sessions")

st.divider()

# --- Top Level Performance Metrics ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        label="📚 Study Materials",
        value=metrics["materials_count"],
        help="Active documents indexed in your study library"
    )

with c2:
    st.metric(
        label="📝 Quizzes Taken",
        value=metrics["quizzes_count"],
        help="Total assessment attempts logged"
    )

with c3:
    st.metric(
        label="🎯 Average Mastery",
        value=f"{metrics['average_mastery']}%",
        delta=f"+{metrics['average_mastery']}%" if metrics['average_mastery'] > 0 else None,
        help="Weighted average score across all completed quizzes"
    )

with c4:
    st.metric(
        label="🔥 Study Streak",
        value=f"{metrics['streak_days']} Days",
        delta="Streak active",
        help="Consecutive days studying with the companion"
    )

st.write("")

# --- Mastery Breakdown & Recommendations ---
col_mastery, col_insights = st.columns([3, 2], gap="large")

with col_mastery:
    st.subheader("🎯 Topic Mastery Breakdown")
    st.caption("Mastery reflects retention scores across completed quizzes:")

    for topic, score in metrics["mastery_breakdown"].items():
        st.markdown(f"**{topic}**")
        progress_val = score / 100.0
        st.progress(progress_val)

        if score > 0:
            st.caption(f"Current Mastery: **{score}%**")
        else:
            st.caption("No quiz attempts yet • *Take a quick test to establish baseline*")
        st.write("")

with col_insights:
    st.subheader("⚠️ Focus & Review Areas")

    # Detect topics needing attention
    history = st.session_state.get("quiz_history", [])
    recent_weaknesses = []
    for q in history:
        for c in q.get("weak_concepts", []):
            if c not in recent_weaknesses:
                recent_weaknesses.append(c)

    if recent_weaknesses:
        st.markdown(
            """
            <div class="action-box">
                <h4 style="margin-top:0; color:#b91c1c;">Identified Review Concepts</h4>
                <p style="font-size:0.95rem; color:#475569;">
                    Questions on the following topics were recently missed:
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        for concept in recent_weaknesses[:4]:
            st.markdown(f"• <span class=\"tag-pill\">{concept}</span>", unsafe_allow_html=True)

        st.write("")
        if st.button("💬 Ask Tutor to Explain Missed Concepts", use_container_width=True):
            st.switch_page("pages/2_Chat.py")
    else:
        st.success("🎉 No active weak areas detected! All tested concepts are performing strongly.")

# --- Recent Quiz History Table ---
st.divider()
st.subheader("🕒 Recent Quiz History")

if not history:
    st.info("No quiz history recorded yet. Complete a quiz in the Practice Quiz tab to populate this timeline.")
else:
    table_rows = []
    for item in reversed(history[-5:]):
        table_rows.append({
            "Date": item.get("date", "Recent"),
            "Topic": item.get("topic", "General"),
            "Score": f"{item.get('score', 0)} / {item.get('total', 0)}",
            "Percentage": f"{item.get('percentage', 0)}%",
            "Difficulty": item.get("difficulty", "Standard"),
            "Review Needed": ", ".join(item.get("weak_concepts", [])) or "None (Clean Run)"
        })

    st.dataframe(table_rows, use_container_width=True)

# Study recommendation banner
st.markdown(
    """
    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:16px 20px; margin-top:1.5rem;">
        💡 <b>Spaced Repetition Advice:</b>
        Review topics with mastery under 75% within 48 hours to flatten the Ebbinghaus forgetting curve.
    </div>
    """,
    unsafe_allow_html=True
)