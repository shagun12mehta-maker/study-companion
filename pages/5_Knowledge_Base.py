
import re
import streamlit as st
from study_data import init_session_state

st.set_page_config(
    page_title="Knowledge Base",
    page_icon="📚",
    layout="wide"
)

init_session_state()

st.title("📚 Knowledge Base")
st.write(
    "Explore your uploaded study materials, topic tree, "
    "and text chunks with their source information."
)

# --------------------------------------------------
# 1. GET UPLOADED DOCUMENTS
# --------------------------------------------------

documents = st.session_state.get("uploaded_materials", [])


# --------------------------------------------------
# 2. GET PAGE-WISE TEXT
# --------------------------------------------------

def get_page_records(document):
    page_records = document.get("page_records", [])

    if page_records:
        return page_records

    extracted_text = document.get("extracted_text", "")

    if not isinstance(extracted_text, str) or not extracted_text.strip():
        return []

    matches = list(
        re.finditer(r"---\s*Page\s+(\d+)\s*---", extracted_text)
    )

    if matches:
        recovered_pages = []

        for index, match in enumerate(matches):
            start = match.end()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(extracted_text)

            page_text = extracted_text[start:end].strip()

            recovered_pages.append({
                "page_number": int(match.group(1)),
                "text": page_text
            })

        return recovered_pages

    return [{
        "page_number": "Unknown",
        "text": extracted_text
    }]


# --------------------------------------------------
# 3. CREATE TEXT CHUNKS
# --------------------------------------------------

all_chunks = []
chunk_size = 500

for document_index, document in enumerate(documents):
    source_name = document.get("name", "Unknown file")
    topic = document.get("topic", "General") or "General"
    document_id = document.get("id", f"doc_{document_index}")

    page_records = get_page_records(document)

    for page in page_records:
        page_number = page.get("page_number", "Unknown")
        page_text = page.get("text", "")

        if not isinstance(page_text, str) or not page_text.strip():
            continue

        for index in range(0, len(page_text), chunk_size):
            chunk_text = page_text[index:index + chunk_size]
            chunk_number = (index // chunk_size) + 1

            all_chunks.append({
                "chunk_id": (
                    f"{document_id}_p{page_number}_c{chunk_number}"
                ),
                "filename": source_name,
                "document_id": document_id,
                "topic": str(topic),
                "page_number": page_number,
                "text": chunk_text
            })


# --------------------------------------------------
# 4. SUMMARY METRICS
# --------------------------------------------------

topics = sorted({
    chunk["topic"] for chunk in all_chunks
})

documents_with_text = len({
    chunk["document_id"] for chunk in all_chunks
})

col1, col2, col3 = st.columns(3)

col1.metric("📄 Documents", documents_with_text)
col2.metric("📚 Topics", len(topics))
col3.metric("🧩 Total Chunks", len(all_chunks))

st.divider()


# --------------------------------------------------
# 5. SEARCH AND FILTER
# --------------------------------------------------

search_query = st.text_input(
    "🔎 Search chunks",
    placeholder="Search a concept or keyword..."
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_topic = st.selectbox(
        "Filter by topic",
        ["All Topics"] + topics
    )

with filter_col2:
    selected_document = st.selectbox(
        "Filter by document",
        ["All Documents"] + sorted({
            chunk["filename"] for chunk in all_chunks
        })
    )

visible_chunks = all_chunks

if selected_topic != "All Topics":
    visible_chunks = [
        chunk for chunk in visible_chunks
        if chunk["topic"] == selected_topic
    ]

if selected_document != "All Documents":
    visible_chunks = [
        chunk for chunk in visible_chunks
        if chunk["filename"] == selected_document
    ]

if search_query.strip():
    query_words = set(
        re.findall(r"[a-zA-Z0-9]+", search_query.lower())
    )

    visible_chunks = [
        chunk for chunk in visible_chunks
        if query_words.intersection(
            set(re.findall(r"[a-zA-Z0-9]+", chunk["text"].lower()))
        )
    ]

st.caption(
    f"Showing {len(visible_chunks)} of {len(all_chunks)} chunks"
)

st.divider()


# --------------------------------------------------
# 6. TOPIC TREE
# --------------------------------------------------

st.subheader("🌳 Topic Tree")

if not all_chunks:
    st.info(
        "Your knowledge base is empty. Go to Upload, "
        "upload a document, and process it first."
    )
else:
    for topic in topics:
        topic_chunks = [
            chunk for chunk in all_chunks
            if chunk["topic"] == topic
        ]

        with st.expander(
            f"📚 {topic} ({len(topic_chunks)} chunks)",
            expanded=False
        ):
            topic_documents = sorted({
                chunk["filename"] for chunk in topic_chunks
            })

            st.markdown("**Source documents**")

            for filename in topic_documents:
                st.write(f"📄 {filename}")

            st.markdown("**Chunks under this topic**")

            for chunk in topic_chunks:
                with st.expander(
                    f"🧩 {chunk['chunk_id']} — Page {chunk['page_number']}",
                    expanded=False
                ):
                    st.write(f"**Source:** {chunk['filename']}")
                    st.write(f"**Topic:** {chunk['topic']}")
                    st.write(f"**Page:** {chunk['page_number']}")
                    st.write(f"**Chunk ID:** {chunk['chunk_id']}")
                    st.text(chunk["text"])


# --------------------------------------------------
# 7. FILTERED CHUNK VIEW
# --------------------------------------------------

st.divider()
st.subheader("📝 Browse Chunks")

if not visible_chunks:
    st.info("No matching chunks found. Try another search or filter.")
else:
    for chunk in visible_chunks:
        with st.expander(
            f"🧩 {chunk['chunk_id']} — {chunk['filename']}",
            expanded=False
        ):
            st.write(f"**Topic:** {chunk['topic']}")
            st.write(f"**Source:** {chunk['filename']}")
            st.write(f"**Page:** {chunk['page_number']}")
            st.write(f"**Chunk ID:** {chunk['chunk_id']}")
            st.text(chunk["text"])
