import sys
import re
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from study_data import init_session_state
from gemini_helper import generate_tutor_answer


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Concept AI Tutor",
    page_icon="💬",
    layout="wide"
)

init_session_state()

st.title("💬 Concept AI Tutor")
st.caption(
    "Ask questions about your uploaded notes "
    "and get direct answers."
)


# --------------------------------------------------
# 2. SESSION STATE
# --------------------------------------------------

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

if "selected_source" not in st.session_state:
    st.session_state["selected_source"] = None

if "uploaded_materials" not in st.session_state:
    st.session_state["uploaded_materials"] = []


# --------------------------------------------------
# 3. EXTRACT PAGE-WISE TEXT
# --------------------------------------------------

def get_page_records(document):
    records = document.get("page_records", [])

    if isinstance(records, list) and records:
        result = []

        for record in records:
            if not isinstance(record, dict):
                continue

            page = record.get(
                "page",
                record.get("page_number", 1)
            )

            text = record.get(
                "text",
                record.get("content", "")
            )

            if text and str(text).strip():
                try:
                    page = int(page)
                except (ValueError, TypeError):
                    page = 1

                result.append({
                    "page": page,
                    "text": str(text).strip()
                })

        if result:
            return result

    extracted_text = document.get("extracted_text", "")

    if not extracted_text:
        return []

    sections = re.split(
        r"---\s*Page\s+(\d+)\s*---",
        extracted_text,
        flags=re.IGNORECASE
    )

    if len(sections) >= 3:
        result = []

        for i in range(1, len(sections), 2):
            page_text = (
                sections[i + 1]
                if i + 1 < len(sections)
                else ""
            )

            if page_text.strip():
                result.append({
                    "page": int(sections[i]),
                    "text": page_text.strip()
                })

        return result

    return [{
        "page": 1,
        "text": extracted_text.strip()
    }]


# --------------------------------------------------
# 4. FIND RELEVANT PAGES
# --------------------------------------------------

def find_relevant_context(question, documents):
    stop_words = {
        "what", "is", "are", "the", "a", "an", "in",
        "on", "of", "to", "for", "and", "explain",
        "tell", "me", "about", "how", "why", "does",
        "do", "can", "you", "please", "define",
        "difference", "between", "happens", "when"
    }

    question_words = set(
        re.findall(r"\b[a-zA-Z0-9]+\b", question.lower())
    )

    question_words -= stop_words

    synonym_groups = [
        {"prediction", "predict", "predicts", "predicting"},
        {"branch", "branches"},
        {"pipeline", "pipelines"},
        {"misprediction", "mispredict", "wrong", "guess"},
        {"target", "address", "jump"},
        {"static", "dynamic"},
        {"buffer", "btb"},
    ]

    for group in synonym_groups:
        if question_words.intersection(group):
            question_words.update(group)

    matches = []

    for doc in documents:
        for record in get_page_records(doc):
            page_text = record["text"]

            page_words = set(
                re.findall(
                    r"\b[a-zA-Z0-9]+\b",
                    page_text.lower()
                )
            )

            score = len(
                question_words.intersection(page_words)
            )

            if score > 0:
                matches.append({
                    "score": score,
                    "text": page_text,
                    "document": doc.get(
                        "name",
                        "Uploaded document"
                    ),
                    "document_id": doc.get("id"),
                    "page": record["page"]
                })

    matches.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return matches[:3]


# --------------------------------------------------
# 5. SOURCE VIEWER
# --------------------------------------------------

def show_source_viewer():
    selected = st.session_state.get("selected_source")

    if not selected:
        return

    st.divider()
    st.subheader("📚 Source Viewer")

    documents = st.session_state.get(
        "uploaded_materials",
        []
    )

    source_doc = next(
        (
            doc for doc in documents
            if doc.get("id") == selected.get("document_id")
        ),
        None
    )

    if not source_doc:
        st.warning(
            "Source document is not available. "
            "Please upload the PDF again."
        )
        return

    source_page = selected.get("page", 1)

    st.markdown(
        f"**Source:** "
        f"{source_doc.get('name', 'Uploaded document')}"
    )

    st.markdown(f"**Page:** {source_page}")

    page_text = ""

    for record in get_page_records(source_doc):
        if record["page"] == int(source_page):
            page_text = record["text"]
            break

    if page_text:
        with st.expander("📖 View extracted page text"):
            st.write(page_text)

    file_bytes = source_doc.get("file_bytes")

    if (
        file_bytes
        and source_doc.get("name", "").lower().endswith(".pdf")
    ):
        st.download_button(
            "📥 Download Original PDF",
            data=file_bytes,
            file_name=source_doc["name"],
            mime="application/pdf",
            key=f"download_{source_doc.get('id', 'pdf')}"
        )

    if st.button("✖️ Close Source Viewer"):
        st.session_state["selected_source"] = None
        st.rerun()


# --------------------------------------------------
# 6. DISPLAY CHAT MESSAGES
# --------------------------------------------------

def display_message(message, message_index):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        for index, citation in enumerate(
            message.get("citations", [])
        ):
            label = (
                f"📄 Open source — {citation['document']} "
                f"(Page {citation['page']})"
            )

            if st.button(
                label,
                key=f"source_{message_index}_{index}"
            ):
                st.session_state["selected_source"] = {
                    "document_id": citation["document_id"],
                    "page": citation["page"]
                }

                st.rerun()


# --------------------------------------------------
# 7. ACTIVE STUDY MATERIAL
# --------------------------------------------------

documents = st.session_state.get(
    "uploaded_materials",
    []
)

with st.expander("📁 Active Study Context", expanded=True):
    if documents:
        for doc in documents:
            st.write(
                f"📄 **{doc.get('name', 'Uploaded document')}**"
            )
    else:
        st.info(
            "No study material found. "
            "Upload and process a PDF from the Upload page first."
        )


# --------------------------------------------------
# 8. QUICK QUESTIONS
# --------------------------------------------------

st.markdown("### ✨ Quick Questions")

quick_questions = [
    "Explain branch prediction",
    "What is a pipeline?",
    "Explain cache memory"
]

columns = st.columns(3)

for index, question in enumerate(quick_questions):
    with columns[index]:
        if st.button(
            question,
            key=f"quick_question_{index}"
        ):
            st.session_state["pending_question"] = question
            st.rerun()


# --------------------------------------------------
# 9. CHAT HISTORY
# --------------------------------------------------

for message_index, message in enumerate(
    st.session_state["chat_messages"]
):
    display_message(message, message_index)


# --------------------------------------------------
# 10. HANDLE QUESTION
# --------------------------------------------------

prompt = st.chat_input(
    "Ask a question from your uploaded notes..."
)

if st.session_state.get("pending_question"):
    prompt = st.session_state.pop("pending_question")

if prompt:
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": prompt,
        "citations": []
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    documents = st.session_state.get(
        "uploaded_materials",
        []
    )

    if not documents:
        answer = (
            "Please upload and process your study material "
            "before asking questions."
        )

        citations = []

    else:
        matches = find_relevant_context(
            prompt,
            documents
        )

        if not matches:
            answer = (
                "I couldn't find relevant information for this "
                "question in your uploaded study material. "
                "Try asking about a concept covered in your notes."
            )

            citations = []

        else:
            context_parts = []

            for match in matches:
                context_parts.append(
                    f"Source: {match['document']}\n"
                    f"Page: {match['page']}\n"
                    f"Text:\n{match['text'][:3000]}"
                )

            study_material = "\n\n---\n\n".join(
                context_parts
            )

            citations = [
                {
                    "document": match["document"],
                    "document_id": match["document_id"],
                    "page": match["page"]
                }
                for match in matches
            ]

            try:
                with st.spinner(
                    "🤖 AI is preparing your answer..."
                ):
                    answer = generate_tutor_answer(
                        question=prompt,
                        study_material=study_material
                    )

            except Exception as error:
                print("CHAT ERROR:", repr(error))

                answer = (
                    "⚠️ The AI tutor is temporarily unavailable.\n\n"
                    "Please try again in a few seconds. "
                    "If this keeps happening, check Gemini API "
                    "availability and your API limits."
                )

    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": answer,
        "citations": citations
    })

    st.rerun()


# --------------------------------------------------
# 11. SOURCE VIEWER PANEL
# --------------------------------------------------

show_source_viewer()