import sys
from pathlib import Path
from datetime import datetime
import streamlit as st

# Ensure repository root is on sys.path for shared imports
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from study_data import init_session_state, format_file_size, AVAILABLE_TOPICS

st.set_page_config(
    page_title="Study Materials | AI Study Companion",
    page_icon="📤",
    layout="wide"
)

init_session_state()

# --- Page styling ---
st.markdown("""
<style>
.page-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.2rem;
}
.page-subtitle {
    font-size: 1.05rem;
    color: #64748b;
    margin-bottom: 1.5rem;
}
.upload-card-wrapper {
    background: #ffffff;
    padding: 24px;
    border-radius: 14px;
    border: 1px dashed #cbd5e1;
    margin-bottom: 1.5rem;
}
.doc-item {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.badge-ready {
    background-color: #dcfce7;
    color: #15803d;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="page-title">📤 Study Materials & Notes</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Upload your course lecture slides and reference notes to build your personal knowledge base.</div>',
    unsafe_allow_html=True
)

student_name = st.session_state.get("student_name", "Student")
st.caption(f"Currently managing library for **{student_name}**")
st.divider()

# --- File Uploader Section ---
col_upload, col_meta = st.columns([2, 1], gap="medium")

with col_upload:
    uploaded_file = st.file_uploader(
        "Choose lecture slides or notes",
        type=["pdf", "pptx", "ppt", "txt", "docx"],
        help="Upload files up to 50MB. Text will be parsed and indexed for tutor reference."
    )

with col_meta:
    doc_topic = st.selectbox("Associated Topic", AVAILABLE_TOPICS)
    doc_notes = st.text_input("Optional Tag / Chapter", placeholder="e.g. Chapter 3, Midterm Review")

# Process uploaded file into session state
if uploaded_file is not None:
    # Check if file is already added to prevent duplicate appends
    existing_names = [d["name"] for d in st.session_state["uploaded_materials"]]
    if uploaded_file.name not in existing_names:
        new_doc = {
            "id": f"doc_{len(st.session_state['uploaded_materials']) + 1}",
            "name": uploaded_file.name,
            "size_kb": round(uploaded_file.size / 1024, 1),
            "upload_time": datetime.now().strftime("%b %d, %I:%M %p"),
            "topic": doc_topic,
            "tag": doc_notes.strip() if doc_notes else "General",
            "page_count": max(1, int(uploaded_file.size / (1024 * 45))), # Approximate page estimate
            "status": "Indexed"
        }
        st.session_state["uploaded_materials"].append(new_doc)
        st.success(f"Successfully added **{uploaded_file.name}** ({format_file_size(uploaded_file.size)}) to your library!")
    else:
        st.info(f"**{uploaded_file.name}** is already in your study library.")

# --- Document Library View ---
st.write("")
st.subheader("📚 Your Indexed Library")

materials = st.session_state.get("uploaded_materials", [])

if not materials:
    st.info("Your library is currently empty. Upload your first course note above to get started!")
else:
    st.write(f"Showing **{len(materials)}** active study documents:")

    # Render each document with metadata and management actions
    for index, doc in enumerate(materials):
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                st.markdown(f"📄 **{doc['name']}**")
                st.caption(f"Topic: {doc.get('topic', 'General')} • {doc.get('tag', '')}")
            with c2:
                st.write(f"Size: `{doc['size_kb']} KB` (~{doc.get('page_count', 1)} pages)")
                st.caption(f"Added: {doc.get('upload_time', 'Recently')}")
            with c3:
                st.markdown('<span class="badge-ready">✓ Ready for Tutor</span>', unsafe_allow_html=True)
            with c4:
                # Remove button per item
                if st.button("Delete", key=f"del_doc_{index}", help="Remove from library"):
                    st.session_state["uploaded_materials"].pop(index)
                    st.rerun()
            st.divider()

# Quick action shortcut
st.write("")
col_cta1, col_cta2 = st.columns(2)
with col_cta1:
    if st.button("💬 Ask AI Tutor About These Notes", use_container_width=True):
        st.switch_page("pages/2_Chat.py")
with col_cta2:
    if st.button("📝 Generate Quiz From This Material", use_container_width=True):
        st.switch_page("pages/3_Quiz.py")