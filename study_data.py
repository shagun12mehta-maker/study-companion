"""
study_data.py
Helper module for managing session state, sample learning materials,
realistic quiz question banks, and progress analytics.
"""

from datetime import datetime
import streamlit as st

# Default course topics available across the application
AVAILABLE_TOPICS = [
    "Data Structures",
    "Operating Systems",
    "Computer Networks",
    "Programming Concepts"
]

# Curated question bank with multiple difficulties and explanations
QUESTION_BANK = {
    "Data Structures": [
        {
            "id": "ds_1",
            "question": "Which data structure operates on a Last-In, First-Out (LIFO) order?",
            "options": ["Queue", "Stack", "Binary Search Tree", "Linked List"],
            "answer_index": 1,
            "explanation": "A Stack follows the LIFO principle: the last element pushed onto the stack is the first one popped off.",
            "difficulty": "Easy",
            "concept": "Stack Basics"
        },
        {
            "id": "ds_2",
            "question": "What is the average time complexity for searching an element in a balanced Binary Search Tree (BST)?",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
            "answer_index": 2,
            "explanation": "In a balanced BST, each comparison halves the remaining search space, yielding O(log n) average time complexity.",
            "difficulty": "Easy",
            "concept": "Tree Traversal"
        },
        {
            "id": "ds_3",
            "question": "How does a hash table resolve collisions when using separate chaining?",
            "options": [
                "By probing the next available contiguous index",
                "By storing colliding elements in a linked list at the bucket index",
                "By immediately resizing the table to double its capacity",
                "By overwriting the older entry with the new key-value pair"
            ],
            "answer_index": 1,
            "explanation": "Separate chaining handles collisions by maintaining a linked list (or other bucket chain) for every table slot.",
            "difficulty": "Medium",
            "concept": "Hashing Collisions"
        },
        {
            "id": "ds_4",
            "question": "Which algorithm is best suited for finding the shortest path in an unweighted graph?",
            "options": [
                "Depth-First Search (DFS)",
                "Breadth-First Search (BFS)",
                "Dijkstra's Algorithm",
                "Prim's Algorithm"
            ],
            "answer_index": 1,
            "explanation": "Breadth-First Search (BFS) explores all neighbors level-by-level, guaranteeing the shortest path in unweighted graphs.",
            "difficulty": "Medium",
            "concept": "Graph Algorithms"
        },
        {
            "id": "ds_5",
            "question": "In a max-heap with n elements, what is the worst-case time complexity to extract the maximum element?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "answer_index": 1,
            "explanation": "Removing the root takes O(1), but restoring the heap invariant (heapify down) requires traversing tree height, taking O(log n).",
            "difficulty": "Hard",
            "concept": "Heaps and Priority Queues"
        }
    ],
    "Operating Systems": [
        {
            "id": "os_1",
            "question": "What primary resource do threads of the same process share by default?",
            "options": [
                "Stack and registers",
                "Address space and heap memory",
                "Program counter and registers",
                "Thread ID and stack frame"
            ],
            "answer_index": 1,
            "explanation": "Threads share their parent process's virtual address space, heap, and open file descriptors, while keeping their own registers and stack.",
            "difficulty": "Easy",
            "concept": "Processes and Threads"
        },
        {
            "id": "os_2",
            "question": "Which of the following is NOT one of Coffman's four conditions required for deadlock?",
            "options": [
                "Mutual Exclusion",
                "Hold and Wait",
                "Preemptive Scheduling",
                "Circular Wait"
            ],
            "answer_index": 2,
            "explanation": "The condition is No Preemption. Preemptive scheduling actually helps prevent or break deadlocks.",
            "difficulty": "Easy",
            "concept": "Deadlock Conditions"
        },
        {
            "id": "os_3",
            "question": "What is the primary function of the Translation Lookaside Buffer (TLB)?",
            "options": [
                "To buffer disk writes before flushing to persistent storage",
                "To cache recently used virtual-to-physical address translations",
                "To manage round-robin CPU scheduling queues",
                "To synchronize shared variables across threads"
            ],
            "answer_index": 1,
            "explanation": "The TLB is a high-speed hardware cache inside the MMU that avoids multi-level page table lookups in RAM.",
            "difficulty": "Medium",
            "concept": "Virtual Memory and Paging"
        },
        {
            "id": "os_4",
            "question": "What phenomenon occurs when a system spends more time servicing page faults than executing instructions?",
            "options": ["Starvation", "Thrashing", "Fragmentation", "Context Flooding"],
            "answer_index": 1,
            "explanation": "Thrashing happens when processes do not have enough working-set frames, leading to continuous disk I/O from page faults.",
            "difficulty": "Medium",
            "concept": "Memory Management"
        },
        {
            "id": "os_5",
            "question": "In modern kernels, why is the Completely Fair Scheduler (CFS) favored over traditional multilevel feedback queues?",
            "options": [
                "It eliminates the need for context switches completely",
                "It tracks virtual runtime (vruntime) using a red-black tree for bounded O(log n) picking",
                "It restricts processes to a single shared execution core",
                "It uses FIFO queueing exclusively for interactive tasks"
            ],
            "answer_index": 1,
            "explanation": "CFS models an ideal multitasking CPU by scheduling the task with the lowest vruntime, tracked efficiently in a red-black tree.",
            "difficulty": "Hard",
            "concept": "CPU Scheduling"
        }
    ],
    "Computer Networks": [
        {
            "id": "net_1",
            "question": "At which layer of the OSI model does an IP router primarily operate?",
            "options": [
                "Data Link Layer (Layer 2)",
                "Network Layer (Layer 3)",
                "Transport Layer (Layer 4)",
                "Application Layer (Layer 7)"
            ],
            "answer_index": 1,
            "explanation": "Routers forward packets based on logical IP addresses, which belong to the Network Layer (Layer 3).",
            "difficulty": "Easy",
            "concept": "OSI Reference Model"
        },
        {
            "id": "net_2",
            "question": "Which protocol is connectionless and does not guarantee packet delivery order?",
            "options": ["TCP", "UDP", "BGP", "SSH"],
            "answer_index": 1,
            "explanation": "User Datagram Protocol (UDP) trades reliable transmission and sequencing for low latency and minimal protocol overhead.",
            "difficulty": "Easy",
            "concept": "Transport Protocols"
        },
        {
            "id": "net_3",
            "question": "What sequence of packets completes the standard TCP three-way handshake?",
            "options": [
                "ACK -> SYN -> SYN-ACK",
                "SYN -> SYN-ACK -> ACK",
                "SYN -> ACK -> DATA",
                "CONNECT -> ACCEPT -> READY"
            ],
            "answer_index": 1,
            "explanation": "Client sends SYN, server responds with SYN-ACK, and client acknowledges with ACK to establish a full-duplex session.",
            "difficulty": "Medium",
            "concept": "TCP Handshake"
        },
        {
            "id": "net_4",
            "question": "What is the primary role of DNS in modern internet infrastructure?",
            "options": [
                "Encrypting end-to-end payload traffic",
                "Translating human-readable domain names into IP addresses",
                "Assigning dynamic local IP addresses to LAN clients",
                "Detecting dropped packets on wireless channels"
            ],
            "answer_index": 1,
            "explanation": "Domain Name System (DNS) maps human-friendly hostnames (e.g., example.com) to machine-routable IP addresses.",
            "difficulty": "Medium",
            "concept": "Application Protocols"
        },
        {
            "id": "net_5",
            "question": "How does the TCP congestion control algorithm identify packet loss in Reno?",
            "options": [
                "By pinging the gateway router on a timer",
                "Through triple duplicate ACKs or a retransmission timeout (RTO)",
                "By measuring instantaneous packet round-trip jitter only",
                "Through ICMP error codes sent by intermediate switches"
            ],
            "answer_index": 1,
            "explanation": "TCP Reno triggers fast retransmit upon receiving three duplicate ACKs, or backs off completely if a full RTO timer expires.",
            "difficulty": "Hard",
            "concept": "Congestion Control"
        }
    ],
    "Programming Concepts": [
        {
            "id": "prog_1",
            "question": "In Python, which built-in data type is immutable?",
            "options": ["List", "Dictionary", "Tuple", "Set"],
            "answer_index": 2,
            "explanation": "Tuples cannot be modified once created; attempting to reassign an index raises a TypeError.",
            "difficulty": "Easy",
            "concept": "Python Data Types"
        },
        {
            "id": "prog_2",
            "question": "What object-oriented principle allows a subclass to provide a specific implementation of a method defined in its parent class?",
            "options": ["Encapsulation", "Method Overriding (Polymorphism)", "Data Hiding", "Composition"],
            "answer_index": 1,
            "explanation": "Polymorphic method overriding lets subclasses supply custom behaviors while preserving the parent interface.",
            "difficulty": "Easy",
            "concept": "Object-Oriented Design"
        },
        {
            "id": "prog_3",
            "question": "What is the base case in a recursive function responsible for?",
            "options": [
                "Allocating dynamic memory on the heap",
                "Terminating the recursion and preventing infinite stack frames",
                "Accelerating loop iteration using caching",
                "Converting recursion into an iterative while loop automatically"
            ],
            "answer_index": 1,
            "explanation": "The base case provides a direct answer without further recursive calls, guarding against RecursionError / stack overflow.",
            "difficulty": "Medium",
            "concept": "Recursion and Call Stacks"
        },
        {
            "id": "prog_4",
            "question": "What is the amortized time complexity of appending an element to the end of a dynamic array (like Python's list)?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
            "answer_index": 0,
            "explanation": "While occasional array doubling takes O(n), spreading that cost across all appends gives an amortized O(1) runtime.",
            "difficulty": "Medium",
            "concept": "Time and Space Complexity"
        },
        {
            "id": "prog_5",
            "question": "How does Python's Global Interpreter Lock (GIL) influence CPU-bound multithreaded programs?",
            "options": [
                "It speeds up execution across all available hardware cores",
                "It restricts bytecode execution to one thread at a time, limiting CPU parallelism",
                "It automatically converts CPU-bound threads into separate OS processes",
                "It disables memory garbage collection during thread execution"
            ],
            "answer_index": 1,
            "explanation": "The CPython GIL allows only one native thread to hold the Python interpreter at any given moment, making multiprocessing preferable for CPU-heavy tasks.",
            "difficulty": "Hard",
            "concept": "Concurrency and Runtime"
        }
    ]
}


def init_session_state():
    """Initializes persistent application session state with realistic defaults."""
    if "student_name" not in st.session_state:
        st.session_state["student_name"] = "Alex"

    if "uploaded_materials" not in st.session_state:
        # Preload two realistic starter course documents so the user can test right away
        st.session_state["uploaded_materials"] = [
            {
                "id": "doc_1",
                "name": "Data_Structures_Lecture_Notes.pdf",
                "size_kb": 1240.5,
                "upload_time": "Today, 10:15 AM",
                "topic": "Data Structures",
                "page_count": 28,
                "status": "Indexed"
            },
            {
                "id": "doc_2",
                "name": "Operating_Systems_Chapter_4.pptx",
                "size_kb": 3480.0,
                "upload_time": "Yesterday, 04:30 PM",
                "topic": "Operating Systems",
                "page_count": 42,
                "status": "Indexed"
            }
        ]

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Hey there! I'm your AI Study Companion. "
                    "Ask me to break down complex concepts, give code examples, "
                    "or summarize notes from your uploaded lecture slides."
                )
            }
        ]

    if "quiz_history" not in st.session_state:
        # Seed an initial quiz record so the analytics dashboard has realistic data immediately
        st.session_state["quiz_history"] = [
            {
                "topic": "Data Structures",
                "difficulty": "Easy",
                "score": 4,
                "total": 5,
                "percentage": 80.0,
                "date": "Oct 10, 2026",
                "weak_concepts": ["Hashing Collisions"]
            }
        ]

    if "streak_days" not in st.session_state:
        st.session_state["streak_days"] = 3

    if "active_quiz" not in st.session_state:
        st.session_state["active_quiz"] = None


def format_file_size(size_bytes: int) -> str:
    """Formats file size into human-readable KB or MB."""
    kb = size_bytes / 1024
    if kb >= 1024:
        return f"{kb / 1024:.2f} MB"
    return f"{kb:.1f} KB"


def generate_tutor_response(user_prompt: str) -> str:
    """Generates an intelligent, educational tutor response tailored to student queries."""
    prompt_lower = user_prompt.lower()
    student = st.session_state.get("student_name", "Student")

    # Stack / Queue
    if "stack" in prompt_lower or "lifo" in prompt_lower:
        return (
            f"### 🥞 Understanding the Stack Data Structure\n\n"
            f"Think of a **Stack** like a stack of cafeteria trays:\n"
            f"- **LIFO Principle**: Last In, First Out. The most recent item added is the first one removed.\n\n"
            f"**Core Operations:**\n"
            f"1. `push(x)`: Adds item `x` onto the top of the stack — **O(1)**.\n"
            f"2. `pop()`: Removes and returns the top item — **O(1)**.\n"
            f"3. `peek()`: Inspects the top item without removing it — **O(1)**.\n\n"
            f"```python\n"
            f"# Quick Python implementation using a list\n"
            f"stack = []\n"
            f"stack.append('Page 1')  # push\n"
            f"stack.append('Page 2')\n"
            f"current = stack.pop()    # returns 'Page 2'\n"
            f"```\n\n"
            f"**Real-world use cases:** Browser back button, undo/redo mechanisms, and the system call stack during recursion."
        )

    # Tree / BST
    if "tree" in prompt_lower or "bst" in prompt_lower or "binary search" in prompt_lower:
        return (
            f"### 🌳 Binary Search Trees (BST)\n\n"
            f"A **Binary Search Tree** organizes hierarchical data with an invariant rule:\n"
            f"- For any node `N`, every node in its **left subtree** has a value `< N`.\n"
            f"- Every node in its **right subtree** has a value `> N`.\n\n"
            f"**Time Complexities:**\n"
            f"| Operation | Balanced BST | Worst Case (Degenerate) |\n"
            f"| :--- | :--- | :--- |\n"
            f"| Search | **O(log n)** | O(n) |\n"
            f"| Insertion | **O(log n)** | O(n) |\n"
            f"| Deletion | **O(log n)** | O(n) |\n\n"
            f"💡 *Pro-tip for exams:* In-order traversal of a BST always yields values in sorted ascending order!"
        )

    # Deadlock / OS
    if "deadlock" in prompt_lower or "operating system" in prompt_lower or "process" in prompt_lower:
        return (
            f"### 🔒 Operating Systems: The 4 Conditions for Deadlock\n\n"
            f"A deadlock occurs when processes are unable to continue because each holds a resource while waiting for another.\n"
            f"According to **Coffman's conditions**, deadlock requires all 4 to hold simultaneously:\n\n"
            f"1. **Mutual Exclusion**: At least one resource must be non-shareable.\n"
            f"2. **Hold and Wait**: A process holds at least one resource while waiting to acquire others.\n"
            f"3. **No Preemption**: Resources cannot be forcibly seized; only the holding process can release them.\n"
            f"4. **Circular Wait**: A closed chain of processes exists where each waits for a resource held by the next.\n\n"
            f"**How OS prevents it:** Breaking any single condition (e.g., using resource ordering to eliminate circular wait) makes deadlock impossible."
        )

    # TCP / Networking
    if "tcp" in prompt_lower or "udp" in prompt_lower or "network" in prompt_lower or "handshake" in prompt_lower:
        return (
            f"### 🌐 TCP vs UDP & The 3-Way Handshake\n\n"
            f"Here is how the two primary transport protocols compare:\n\n"
            f"- **TCP (Transmission Control Protocol)**: Connection-oriented, reliable, guarantees packet ordering, handles flow and congestion control.\n"
            f"- **UDP (User Datagram Protocol)**: Connectionless, lightweight, low-overhead, best for live video streaming and gaming where speed beats packet recovery.\n\n"
            f"**The TCP 3-Way Handshake:**\n"
            f"```text\n"
            f"Client                    Server\n"
            f"  |-------- SYN ---------->|   (Client requests connection with initial seq #)\n"
            f"  |<----- SYN-ACK ---------|   (Server confirms and sends own seq #)\n"
            f"  |-------- ACK ---------->|   (Client acknowledges; channel open)\n"
            f"```"
        )

    # Default contextual response
    materials = [m["name"] for m in st.session_state.get("uploaded_materials", [])]
    materials_mention = f" I see you have **{len(materials)} documents** loaded in your study library ({', '.join(materials[:2])})." if materials else ""

    return (
        f"That's a thoughtful question, {student}!{materials_mention}\n\n"
        f"Here is how to think about **{user_prompt.strip()}** systematically:\n\n"
        f"1. **Core Concept**: Break the problem down into its fundamental definitions first.\n"
        f"2. **Why It Matters**: Understand the trade-offs (time complexity vs memory, simplicity vs scalability).\n"
        f"3. **Practical Application**: Relate the theory to actual code or real-world system architecture.\n\n"
        f"Would you like me to walk through a concrete code example, test you on this topic with a quick quiz, or summarize key exam flashcards?"
    )


def calculate_dashboard_metrics():
    """Computes aggregated study metrics for the dashboard view."""
    materials = st.session_state.get("uploaded_materials", [])
    history = st.session_state.get("quiz_history", [])
    streak = st.session_state.get("streak_days", 1)

    total_quizzes = len(history)
    if total_quizzes > 0:
        avg_score = round(sum(q["percentage"] for q in history) / total_quizzes, 1)
    else:
        avg_score = 0.0

    # Calculate mastery per topic
    topic_scores = {topic: [] for topic in AVAILABLE_TOPICS}
    for q in history:
        t = q.get("topic")
        if t in topic_scores:
            topic_scores[t].append(q.get("percentage", 0))

    mastery_breakdown = {}
    for topic, scores in topic_scores.items():
        if scores:
            mastery_breakdown[topic] = int(round(sum(scores) / len(scores)))
        else:
            mastery_breakdown[topic] = 0

    # Collect weak areas
    weak_topics = []
    for topic, score in mastery_breakdown.items():
        if score > 0 and score < 75:
            weak_topics.append((topic, score))
        elif score == 0:
            weak_topics.append((topic, None))  # Not tested yet

    return {
        "materials_count": len(materials),
        "quizzes_count": total_quizzes,
        "average_mastery": avg_score,
        "streak_days": streak,
        "mastery_breakdown": mastery_breakdown,
        "weak_topics": weak_topics
    }
