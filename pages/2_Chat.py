
import sys
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import streamlit as st

# Project root ko Python path mein add karna
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from study_data import init_session_state, generate_tutor_response


# --------------------------------------------------
# 1. PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Concept AI Tutor",
    page_icon="💬",
    layout="wide"
)

init_session_state()

st.title("💬 Concept AI Tutor")
st.caption(
    "Ask conceptual questions, understand your notes, "
    "and open the original source of an answer."
)

# Required session-state values
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

if "selected_source" not in st.session_state:
    st.session_state["selected_source"] = None

if "uploaded_materials" not in st.session_state:
    st.session_state["uploaded_materials"] = []


# --------------------------------------------------
# 2. FIND RELEVANT INFORMATION IN UPLOADED NOTES
# --------------------------------------------------

def find_relevant_context(question, documents):
    """
    Search uploaded documents and return relevant page passages.
    """

    question_words = set(
        re.findall(r"\b[a-zA-Z0-9]+\b", question.lower())
    )

    # Ignore very common words during matching
    stop_words = {
        "what", "is", "are", "the", "a", "an", "in",
        "on", "of", "to", "for", "and", "explain",
        "tell", "me", "about", "how", "why", "does"
    }

    question_words -= stop_words
    matches = []

    for doc in documents:
        extracted_text = doc.get("extracted_text", "")

        if not extracted_text:
            continue

        # Split text into page-wise sections
        page_sections = re.split(
            r"---\s*Page\s+(\d+)\s*---",
            extracted_text,
            flags=re.IGNORECASE
        )

        # The usual format is:
        # text before first page, page number, page text...
        if len(page_sections) >= 3:
            page_records = []

            for i in range(1, len(page_sections), 2):
                page_number = int(page_sections[i])
                page_text = (
                    page_sections[i + 1]
                    if i + 1 < len(page_sections)
                    else ""
                )

                page_records.append((page_number, page_text))
        else:
            page_records = [(1, extracted_text)]

        for page_number, page_text in page_records:
            if not page_text.strip():
                continue

            page_words = set(
                re.findall(r"\b[a-zA-Z0-9]+\b", page_text.lower())
            )

            score = len(question_words.intersection(page_words))

            if score > 0:
                matches.append({
                    "score": score,
                    "text": page_text.strip(),
                    "document": doc.get("name", "Uploaded document"),
                    "document_id": doc.get("id"),
                    "page": page_number
                })

    matches.sort(key=lambda item: item["score"], reverse=True)

    return matches[:5]


# --------------------------------------------------
# 3. SOURCE VIEWER
# --------------------------------------------------

def show_source_viewer():
    """
    Show the selected document and its matching page text.
    Also provides a YouTube timestamp-link creator.
    """

    selected = st.session_state.get("selected_source")

    if not selected:
        return

    st.divider()
    st.subheader("📚 Source Viewer")

    documents = st.session_state.get("uploaded_materials", [])

    source_doc = next(
        (
            doc for doc in documents
            if doc.get("id") == selected.get("document_id")
        ),
        None
    )

    if source_doc:
        source_name = source_doc.get("name", "Uploaded document")
        source_page = selected.get("page", 1)

        st.markdown(f"**Source:** {source_name}")
        st.markdown(f"**Page:** {source_page}")

        # Find the selected page's extracted text
        page_text = ""

        page_records = source_doc.get("page_records", [])

        if isinstance(page_records, list):
            for record in page_records:
                if not isinstance(record, dict):
                    continue

                record_page = record.get(
                    "page",
                    record.get("page_number", 1)
                )

                if str(record_page) == str(source_page):
                    page_text = record.get(
                        "text",
                        record.get("content", "")
                    )
                    break

        # Fallback: find the page in extracted_text
        if not page_text:
            extracted_text = source_doc.get("extracted_text", "")

            sections = re.split(
                r"---\s*Page\s+(\d+)\s*---",
                extracted_text,
                flags=re.IGNORECASE
            )

            for i in range(1, len(sections), 2):
                if (
                    int(sections[i]) == int(source_page)
                    and i + 1 < len(sections)
                ):
                    page_text = sections[i + 1].strip()
                    break

        if page_text:
            with st.expander("📖 View extracted page text", expanded=True):
                st.write(page_text)
        else:
            st.info(
                "Page text is not available. "
                "Try downloading the original document."
            )

        # Download original PDF when available
        file_bytes = source_doc.get("file_bytes")

        if (
            file_bytes
            and source_name.lower().endswith(".pdf")
        ):
            st.download_button(
                "📥 Download Original PDF",
                data=file_bytes,
                file_name=source_name,
                mime="application/pdf",
                key=f"download_source_{source_doc.get('id', 'pdf')}"
            )

    else:
        st.warning(
            "This source is not currently available in the uploaded materials."
        )

    # --------------------------------------------------
    # 4. YOUTUBE TIMESTAMP LINK
    # --------------------------------------------------

    st.divider()
    st.markdown("### ▶️ Open a YouTube video at a specific time")
    st.caption(
        "Enter a YouTube video URL and the time in seconds. "
        "For example, 312 seconds opens the video at 5:12."
    )

    youtube_url = st.text_input(
        "YouTube video URL",
        placeholder="https://www.youtube.com/watch?v=VIDEO_ID",
        key="youtube_source_url"
    )

    timestamp = st.number_input(
        "Start time (seconds)",
        min_value=0,
        value=312,
        step=1,
        key="youtube_timestamp"
    )

    if st.button("▶️ Prepare Timestamp Link"):
        parsed_url = urlparse(youtube_url.strip())
        host = parsed_url.netloc.lower().split(":")[0]

        valid_host = (
            host == "youtube.com"
            or host.endswith(".youtube.com")
            or host == "youtu.be"
            or host.endswith(".youtu.be")
        )

        if (
            parsed_url.scheme not in ("http", "https")
            or not valid_host
            or not parsed_url.path.strip("/")
        ):
            st.error("Please enter a valid YouTube video URL.")

        else:
            query = parse_qs(parsed_url.query)

            # Add/update the video start time
            query["t"] = [f"{int(timestamp)}s"]

            timestamp_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                urlencode(query, doseq=True),
                parsed_url.fragment
            ))

            minutes = int(timestamp) // 60
            seconds = int(timestamp) % 60

            st.success(
                f"Timestamp link ready: {minutes}:{seconds:02d}"
            )

            st.link_button(
                f"Open video at {minutes}:{seconds:02d}",
                timestamp_url
            )

    if st.button("✖️ Close Source Viewer"):
        st.session_state["selected_source"] = None
        st.rerun()


# --------------------------------------------------
# 5. DISPLAY CHAT MESSAGES AND CITATIONS
# --------------------------------------------------

def display_message(message, message_index):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        citations = message.get("citations", [])

        for citation_index, citation in enumerate(citations):
            document_name = citation.get(
                "document",
                "Uploaded document"
            )
            page = citation.get("page", 1)

            if st.button(
                f"📄 Open source — {document_name} (Page {page})",
                key=f"source_{message_index}_{citation_index}"
            ):
                st.session_state["selected_source"] = {
                    "document_id": citation.get("document_id"),
                    "page": page
                }
                st.rerun()


# --------------------------------------------------
# 6. ACTIVE STUDY CONTEXT
# --------------------------------------------------

documents = st.session_state.get("uploaded_materials", [])

with st.expander("📁 Active Study Context", expanded=True):
    if documents:
        for doc in documents:
            st.write(
                f"📄 **{doc.get('name', 'Uploaded document')}**"
            )
    else:
        st.info(
            "No study material found. Upload and process a PDF "
            "from the Upload page first."
        )


# --------------------------------------------------
# 7. QUICK QUESTIONS
# --------------------------------------------------

st.markdown("### ✨ Quick Questions")

quick_questions = [
    "Explain branch prediction",
    "What is a pipeline?",
    "Explain cache memory"
]

quick_cols = st.columns(3)

for index, question in enumerate(quick_questions):
    with quick_cols[index]:
        if st.button(question, key=f"quick_question_{index}"):
            st.session_state["pending_question"] = question
            st.rerun()


# --------------------------------------------------
# 8. SHOW CHAT HISTORY
# --------------------------------------------------

for message_index, message in enumerate(
    st.session_state["chat_messages"]
):
    display_message(message, message_index)


# --------------------------------------------------
# 9. HANDLE NEW QUESTION
# --------------------------------------------------

prompt = st.chat_input(
    "Ask a question from your study material..."
)

if st.session_state.get("pending_question"):
    prompt = st.session_state["pending_question"]
    st.session_state["pending_question"] = None

if prompt:
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": prompt,
        "citations": []
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    matches = find_relevant_context(prompt, documents)

    citations = []
    answer = ""

    if matches:
        # Use the best matching passages from the notes
        best_matches = matches[:3]

        answer_parts = [
            "### 📚 Relevant information from your notes"
        ]

        for match in best_matches:
            answer_parts.append(
                f"**Source:** {match['document']} "
                f"(Page {match['page']})\n\n"
                f"{match['text'][:1800]}"
            )

            citations.append({
                "document": match["document"],
                "document_id": match["document_id"],
                "page": match["page"]
            })

        answer = "\n\n---\n\n".join(answer_parts)

    else:
        # Fallback tutor response when no note passage matches
        try:
            answer = generate_tutor_response(prompt)
        except Exception as error:
            answer = (
                "I couldn't generate a tutor response right now. "
                "Please check the study_data.py setup and try again.\n\n"
                f"Details: {error}"
            )

    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": answer,
        "citations": citations
    })

    st.rerun()


# --------------------------------------------------
# 10. SOURCE VIEWER PANEL
# --------------------------------------------------

show_source_viewer()
