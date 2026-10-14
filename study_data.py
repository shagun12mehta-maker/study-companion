
"""
study_data.py
Helper module for managing session state, learning materials,
tutor responses, and progress analytics.
"""

from datetime import datetime
import streamlit as st


# Topics available throughout the application
AVAILABLE_TOPICS = [
    "Data Structures",
    "Operating Systems",
    "Computer Networks",
    "Programming Concepts",
]


# --------------------------------------------------
# 1. INITIALIZE SESSION STATE
# --------------------------------------------------

def init_session_state():

    # Store the student's name
    if "student_name" not in st.session_state:
        st.session_state["student_name"] = "Shagun"

    # Start with an empty document list.
    # No sample PDFs are automatically added.
    if "uploaded_materials" not in st.session_state:
        st.session_state["uploaded_materials"] = []

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Quiz history
    if "quiz_history" not in st.session_state:
        st.session_state["quiz_history"] = []

    # Track quiz answers
    if "quiz_answers" not in st.session_state:
        st.session_state["quiz_answers"] = []

    # Track quiz score
    if "quiz_score" not in st.session_state:
        st.session_state["quiz_score"] = 0


# --------------------------------------------------
# 2. GENERATE A TUTOR RESPONSE
# --------------------------------------------------

def generate_tutor_response(question, topic="Programming Concepts"):

    question = question.strip()

    if not question:
        return "Please enter a question so I can help you."

    q = question.lower()

    # Basic topic-specific responses
    if "data structure" in q or "array" in q or "stack" in q:
        return (
            "Let's understand this step by step!\n\n"
            "A data structure is a way of organizing and storing "
            "data so that we can use it efficiently.\n\n"
            "Examples include arrays, linked lists, stacks, queues, "
            "trees, and graphs.\n\n"
            "For example, an array stores multiple values under "
            "one variable name."
        )

    if "operating system" in q or "process" in q or "thread" in q:
        return (
            "An Operating System (OS) manages computer hardware "
            "and software resources.\n\n"
            "Examples include Windows, Linux, and macOS.\n\n"
            "A process is a program that is currently executing. "
            "A thread is a smaller execution unit within a process."
        )

    if "computer network" in q or "tcp" in q or "ip address" in q:
        return (
            "A computer network connects devices so they can "
            "communicate and share resources.\n\n"
            "TCP helps provide reliable data delivery, while IP "
            "helps route packets to their destinations."
        )

    if "python" in q or "programming" in q or "function" in q:
        return (
            "Programming means giving instructions to a computer.\n\n"
            "In Python, a function is a reusable block of code.\n\n"
            "Example:\n\n"
            "```python\n"
            "def greet():\n"
            "    print('Hello!')\n\n"
            "greet()\n"
            "```\n\n"
            "Here, `def` defines the function and `greet()` calls it."
        )

    # General response
    return (
        f"Let's work through your question about {topic}.\n\n"
        f"You asked: {question}\n\n"
        "Try breaking the concept into smaller parts. "
        "If you share the exact topic or a short example, "
        "I can explain it step by step."
    )


# --------------------------------------------------
# 3. CALCULATE DASHBOARD METRICS
# --------------------------------------------------

def calculate_dashboard_metrics():

    uploaded_materials = st.session_state.get(
        "uploaded_materials", []
    )

    quiz_history = st.session_state.get(
        "quiz_history", []
    )

    chat_history = st.session_state.get(
        "chat_history", []
    )

    total_documents = len(uploaded_materials)
    total_quizzes = len(quiz_history)
    total_questions = len(chat_history)

    scores = []

    for quiz in quiz_history:
        score = quiz.get("score")

        if isinstance(score, (int, float)):
            scores.append(score)

    if scores:
        average_score = sum(scores) / len(scores)
    else:
        average_score = 0

    return {
        "total_documents": total_documents,
        "total_quizzes": total_quizzes,
        "total_questions": total_questions,
        "average_score": round(average_score, 2),
    }


# --------------------------------------------------
# 4. FORMAT FILE SIZE
# --------------------------------------------------

def format_file_size(size_bytes):

    if size_bytes < 0:
        return "Unknown size"

    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"

    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# --------------------------------------------------
# 5. GET CURRENT DATE AND TIME
# --------------------------------------------------

def get_current_timestamp():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")