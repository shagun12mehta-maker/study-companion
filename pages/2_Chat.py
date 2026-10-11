import sys
from pathlib import Path
import streamlit as st

# Ensure repository root is on sys.path for shared imports
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from study_data import init_session_state, generate_tutor_response

st.set_page_config(
    page_title="AI Tutor | AI Study Companion",
    page_icon="💬",
    layout="wide"
)

init_session_state()

# --- Page header ---
st.title("💬 Concept AI Tutor")
st.markdown("Ask conceptual questions, request code walk-throughs, or clarify doubts from your lecture notes.")

student = st.session_state.get("student_name", "Student")
docs = st.session_state.get("uploaded_materials", [])

# Context pill bar showing active materials
with st.expander("📁 Active Study Context", expanded=False):
    if docs:
        st.write(f"The tutor is referencing **{len(docs)} document(s)** in your library:")
        for d in docs:
            st.markdown(f"- **{d['name']}** *({d.get('topic', 'General')} • {d.get('size_kb')} KB)*")
    else:
        st.info("No documents uploaded yet. You can still ask general CS and engineering questions!")

# Quick suggestion prompt chips
st.markdown("##### ✨ Quick Questions")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

suggested_query = None
with q_col1:
    if st.button("🥞 Explain Stack vs Queue", use_container_width=True):
        suggested_query = "Explain the difference between a Stack and a Queue in simple terms with Python examples."
with q_col2:
    if st.button("🌳 Binary Search Trees", use_container_width=True):
        suggested_query = "How does searching work in a balanced Binary Search Tree, and what is its time complexity?"
with q_col3:
    if st.button("🔒 4 Deadlock Conditions", use_container_width=True):
        suggested_query = "What are the four Coffman conditions required for deadlock in Operating Systems?"
with q_col4:
    if st.button("🌐 TCP 3-Way Handshake", use_container_width=True):
        suggested_query = "Explain the TCP 3-way handshake step-by-step with packet types."

st.divider()

# --- Render Conversation History ---
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Handle User Input ---
user_input = st.chat_input("Ask a question about your study material...")

# If student clicked a suggested prompt chip or typed into chat input
prompt_to_process = suggested_query or user_input

if prompt_to_process:
    # 1. Display and record student message
    st.session_state["chat_messages"].append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)

    # 2. Generate and display tutor response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing study context..."):
            response_text = generate_tutor_response(prompt_to_process)
            st.markdown(response_text)

    # 3. Save assistant response into session state
    st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})

# Sidebar tools for the chat page
with st.sidebar:
    st.markdown("### 🛠️ Chat Controls")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": f"Hi {student}! Chat history cleared. What would you like to review next?"
            }
        ]
        st.rerun()

    st.markdown("---")
    st.caption("💡 Tip: Ask the tutor to 'quiz me on this concept' or 'write a small test script' for hands-on practice.")