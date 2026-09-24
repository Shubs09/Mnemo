import html
from datetime import datetime

import requests
import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Mnemo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def render_html(markup):
    """
    Render an HTML snippet safely inside st.markdown.

    Streamlit's markdown parser treats any line indented by 4+ spaces
    as a code block, and a blank line ends an HTML block. So we strip
    every line's indentation and drop blank lines before rendering.
    """
    cleaned = "\n".join(
        line.strip()
        for line in markup.splitlines()
        if line.strip()
    )

    st.markdown(cleaned, unsafe_allow_html=True)


def safe_text(value):
    """
    Escape user / AI generated text so it cannot break the HTML,
    and keep line breaks visible.
    """
    return html.escape(str(value)).replace("\n", "<br>")


def truncate(text, limit):
    """Collapse whitespace and shorten long text for previews."""
    flat = " ".join(str(text).split())

    if len(flat) <= limit:
        return flat

    return flat[:limit].rstrip() + "…"


def greeting():
    hour = datetime.now().hour

    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def go_to(page):
    """Button callback: switch page (Streamlit reruns automatically)."""
    st.session_state.page = page


def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }


def get_error(response, default_message):
    try:
        return response.json().get("detail", default_message)
    except Exception:
        return default_message


def set_flash(kind, message):
    """Store a message to show after the next rerun."""
    st.session_state.flash = (kind, message)


def show_flash():
    """Display and clear the stored flash message."""
    flash = st.session_state.get("flash")

    if not flash:
        return

    kind, message = flash
    st.session_state.flash = None

    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.error(message)


def logout():
    st.session_state.access_token = None
    st.session_state.email = None
    st.session_state.page = "Dashboard"


def handle_unauthorized(response):
    """If the token expired or is invalid, log the user out."""
    if response.status_code == 401:
        logout()
        set_flash("warning", "Your session expired. Please sign in again.")
        st.rerun()


# ============================================================
# REUSABLE UI COMPONENTS
# ============================================================

def hero(label, title, description):
    render_html(
        f"""
        <div class="hero">
            <div class="hero-label">{label}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-description">{description}</div>
        </div>
        """
    )


def stat_card(label, value):
    render_html(
        f"""
        <div class="stat-card">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
        """
    )


def latest_memory_card(journal):
    snippet = html.escape(truncate(journal.get("content", ""), 90))
    memory_id = safe_text(journal.get("id", "Unknown"))

    render_html(
        f"""
        <div class="stat-card">
            <div class="stat-label">LATEST MEMORY · #{memory_id}</div>
            <div class="stat-snippet">{snippet}</div>
        </div>
        """
    )


def section_title(text):
    render_html(f'<div class="section-title">{text}</div>')


def empty_state(icon, title, description):
    render_html(
        f"""
        <div class="empty-state">
            <div class="empty-icon">{icon}</div>
            <div class="empty-title">{title}</div>
            <div class="empty-description">{description}</div>
        </div>
        """
    )


def journal_card(journal_id, content, preview_chars=None):
    if preview_chars:
        body = html.escape(truncate(content, preview_chars))
    else:
        body = safe_text(content)

    render_html(
        f"""
        <div class="journal-card">
            <div class="journal-id">MEMORY #{safe_text(journal_id)}</div>
            <div class="journal-content">{body}</div>
        </div>
        """
    )


# ============================================================
# CUSTOM CSS
# ============================================================

CUSTOM_CSS = """
<style>

/* ==================================================
   GLOBAL APP
   ================================================== */

.stApp {
    background: #0b1020;
    color: #f8fafc;
}

[data-testid="stHeader"] {
    background: rgba(11, 16, 32, 0.90);
}

[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid rgba(148, 163, 184, 0.15);
}

[data-testid="stSidebar"] * {
    color: #e2e8f0;
}


/* ==================================================
   HERO
   ================================================== */

.hero {
    padding: 38px;
    border-radius: 24px;
    margin-bottom: 28px;
    background:
        radial-gradient(
            circle at 90% 10%,
            rgba(99, 102, 241, 0.25),
            transparent 35%
        ),
        radial-gradient(
            circle at 10% 90%,
            rgba(14, 165, 233, 0.16),
            transparent 30%
        ),
        #11182d;
    border: 1px solid rgba(129, 140, 248, 0.25);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.18);
}

.hero-label {
    color: #a5b4fc;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.1;
    color: #f8fafc;
}

.hero-description {
    margin-top: 12px;
    color: #a8b3c7;
    font-size: 16px;
    line-height: 1.6;
    max-width: 760px;
}


/* ==================================================
   STAT CARDS
   ================================================== */

.stat-card {
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 18px;
    padding: 22px;
    min-height: 110px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.stat-label {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.8px;
}

.stat-value {
    color: #f8fafc;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}


.stat-snippet {
    color: #e5e7eb;
    font-size: 17px;
    font-weight: 600;
    line-height: 1.5;
    margin-top: 10px;
}


/* ==================================================
   SECTION TITLES
   ================================================== */

.section-title {
    color: #f8fafc;
    font-size: 24px;
    font-weight: 700;
    margin-top: 24px;
    margin-bottom: 14px;
}


/* ==================================================
   JOURNAL CARDS
   ================================================== */

.journal-card {
    background: #111827;
    border: 1px solid rgba(148, 163, 184, 0.13);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.10);
}

.journal-id {
    color: #818cf8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.journal-content {
    color: #e5e7eb;
    font-size: 15px;
    line-height: 1.7;
    margin-top: 8px;
}


/* ==================================================
   AI SOURCE CARDS
   ================================================== */

.source-card {
    background: #0f172a;
    border: 1px solid rgba(99, 102, 241, 0.20);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 10px;
}

.source-title {
    color: #a5b4fc;
    font-size: 13px;
    font-weight: 700;
}

.source-content {
    color: #dbe4f0;
    font-size: 14px;
    line-height: 1.6;
    margin-top: 6px;
}

.similarity {
    color: #94a3b8;
    font-size: 12px;
    margin-top: 8px;
}


/* ==================================================
   EMPTY STATE
   ================================================== */

.empty-state {
    background: rgba(15, 23, 42, 0.60);
    border: 1px dashed rgba(148, 163, 184, 0.25);
    border-radius: 20px;
    padding: 50px 20px;
    text-align: center;
}

.empty-icon {
    font-size: 42px;
}

.empty-title {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 700;
    margin-top: 10px;
}

.empty-description {
    color: #94a3b8;
    margin-top: 6px;
}


/* ==================================================
   LOGIN
   ================================================== */

.login-container {
    max-width: 520px;
    margin: 8vh auto 0;
}

.login-brand {
    text-align: center;
    margin-bottom: 30px;
}

.login-icon {
    font-size: 52px;
}

.login-title {
    color: #f8fafc;
    font-size: 36px;
    font-weight: 800;
    margin-top: 8px;
}

.login-subtitle {
    color: #94a3b8;
    margin-top: 6px;
}


/* ==================================================
   INFO BOX
   ================================================== */

.info-box {
    background: rgba(79, 70, 229, 0.08);
    border: 1px solid rgba(129, 140, 248, 0.16);
    border-radius: 14px;
    padding: 14px 16px;
    color: #c7d2fe;
    font-size: 13px;
    line-height: 1.5;
}


/* ==================================================
   USER EMAIL (sidebar)
   ================================================== */

.user-email {
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 14px;
    word-break: break-all;
}


/* ==================================================
   BUTTONS
   ================================================== */

button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    border-radius: 12px;
    min-height: 44px;
    font-weight: 700;
    border: 1px solid rgba(129, 140, 248, 0.30);
    background: #4f46e5;
    color: white;
    transition: all 0.2s ease;
}

button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: #6366f1;
    border-color: #818cf8;
    color: white;
    transform: translateY(-1px);
}

button[kind="secondary"],
button[data-testid="stBaseButton-secondary"] {
    border-radius: 12px;
    min-height: 44px;
    font-weight: 600;
    border: 1px solid rgba(148, 163, 184, 0.25);
    background: transparent;
    color: #cbd5e1;
    transition: all 0.2s ease;
}

button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(99, 102, 241, 0.14);
    border-color: #818cf8;
    color: #f8fafc;
}

/* Sidebar buttons: full width, left aligned */
[data-testid="stSidebar"] .stButton,
[data-testid="stSidebar"] [data-testid="stButton"] {
    width: 100%;
}

[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    width: 100%;
    justify-content: flex-start;
}


/* ==================================================
   STREAMLIT CLEANUP
   ================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
"""

render_html(CUSTOM_CSS)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "access_token": None,
    "email": None,
    "page": "Dashboard",
    "flash": None,
    "journal_form_id": 0,
}

for state_key, default_value in DEFAULT_STATE.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value


# ============================================================
# LOGIN
# ============================================================

def login():

    render_html(
        """
        <div class="login-container">
            <div class="login-brand">
                <div class="login-icon">🧠</div>
                <div class="login-title">Mnemo</div>
                <div class="login-subtitle">
                    Your AI journal that remembers.
                </div>
            </div>
        </div>
        """
    )

    email = st.text_input(
        "Email",
        placeholder="you@example.com",
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="••••••••",
    )

    if st.button("Sign in to Mnemo", type="primary"):

        if not email or not password:
            st.warning("Please enter both email and password.")
            return

        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()

                st.session_state.access_token = data["access_token"]
                st.session_state.email = email

                st.rerun()

            else:
                st.error(get_error(response, "Login failed."))

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to FastAPI. "
                "Make sure the backend is running."
            )

        except requests.exceptions.RequestException:
            st.error(
                "The backend request failed. "
                "Please try again."
            )


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    with st.sidebar:

        st.markdown("## 🧠 Mnemo")
        st.caption("Your AI journal that remembers")

        st.divider()

        navigation = {
            "Dashboard": "🏠",
            "New Journal": "✍️",
            "My Journals": "📚",
            "Ask AI": "🤖",
        }

        for page, icon in navigation.items():

            st.button(
                f"{icon}  {page}",
                key=f"navigation_{page}",
                type="primary" if st.session_state.page == page else "secondary",
                on_click=go_to,
                args=(page,),
            )

        st.divider()

        st.markdown("**Signed in as**")

        render_html(
            f'<div class="user-email">{html.escape(str(st.session_state.email))}</div>'
        )

        render_html(
            """
            <div class="info-box">
                🔒 Your journal uses authenticated
                user-specific access.
            </div>
            """
        )

        st.write("")

        if st.button("Log out", key="logout"):
            logout()
            st.rerun()


# ============================================================
# GET JOURNALS
# ============================================================

def fetch_journals():

    try:
        response = requests.get(
            f"{BACKEND_URL}/journal/",
            headers=get_headers(),
            timeout=30,
        )

        handle_unauthorized(response)

        if response.status_code == 200:
            return response.json().get("journals", [])

        st.error(get_error(response, "Failed to load journals."))

    except requests.exceptions.RequestException:
        st.error("Could not connect to the backend.")

    return []


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    journals = fetch_journals()

    hero(
        "PRIVATE AI MEMORY",
        f"{greeting()}. 👋",
        "Capture your thoughts, revisit your memories, "
        "and ask questions about your journal using "
        "semantic search and AI.",
    )

    # ---------------- QUICK ACTIONS ----------------

    action1, action2, _ = st.columns([1, 1, 2])

    with action1:
        st.button(
            "✍️  Write today's entry",
            key="quick_write",
            type="primary",
            on_click=go_to,
            args=("New Journal",),
        )

    with action2:
        st.button(
            "🤖  Ask your journal",
            key="quick_ask",
            on_click=go_to,
            args=("Ask AI",),
        )

    st.write("")

    # ---------------- STAT CARDS ----------------

    total_entries = len(journals)

    column1, column2 = st.columns([1, 2])

    with column1:
        stat_card("TOTAL MEMORIES", total_entries)

    with column2:
        if journals:
            latest_memory_card(journals[0])
        else:
            stat_card("LATEST MEMORY", "Nothing yet")

    # ---------------- RECENT MEMORIES ----------------

    section_title("Recent memories")

    if not journals:
        empty_state(
            "📖",
            "Your journal is empty",
            "Write your first entry and start building "
            "your personal AI memory.",
        )
        return

    for journal in journals[:5]:
        journal_card(
            journal.get("id", "Unknown"),
            journal.get("content", ""),
            preview_chars=180,
        )

    if total_entries > 5:
        st.button(
            f"View all {total_entries} memories →",
            key="view_all",
            on_click=go_to,
            args=("My Journals",),
        )


# ============================================================
# CREATE JOURNAL
# ============================================================

def create_journal():

    section_title("✍️ Capture a memory")

    st.caption(
        "Write naturally. Your entry will be embedded "
        "and stored for future AI retrieval."
    )

    # Changing the key gives us a fresh, empty text area after saving.
    content = st.text_area(
        "Journal entry",
        key=f"journal_content_{st.session_state.journal_form_id}",
        height=240,
        placeholder=(
            "What happened today?\n"
            "How did you feel?\n"
            "What did you learn?"
        ),
        label_visibility="collapsed",
    )

    if st.button("Save memory", type="primary"):

        # ---------------- VALIDATE INPUT ----------------

        if not content.strip():
            st.warning("Journal entry cannot be empty.")
            return

        # ---------------- SEND TO FASTAPI ----------------

        try:
            response = requests.post(
                f"{BACKEND_URL}/journal/",
                headers=get_headers(),
                json={"content": content},
                timeout=60,
            )

            handle_unauthorized(response)

            if response.status_code == 200:
                st.session_state.journal_form_id += 1
                set_flash("success", "Memory saved successfully.")
                st.rerun()

            else:
                st.error(get_error(response, "Failed to save journal."))

        except requests.exceptions.RequestException:
            st.error("Could not connect to the backend.")


# ============================================================
# VIEW JOURNALS
# ============================================================

def view_journals():

    section_title("📚 Your memories")

    journals = fetch_journals()

    if not journals:
        empty_state(
            "📝",
            "No memories yet",
            "Create your first journal entry to get started.",
        )
        return

    count = len(journals)

    st.caption(
        f"{count} journal {'entry' if count == 1 else 'entries'}"
    )

    for journal in journals:
        journal_card(
            journal.get("id", "Unknown"),
            journal.get("content", ""),
        )


# ============================================================
# AI CHAT
# ============================================================

def ai_chat():

    hero(
        "RAG-POWERED MEMORY",
        "Ask your journal. 🤖",
        "Ask questions about your past entries. "
        "The system retrieves relevant memories "
        "and gives the AI only that context.",
    )

    query = st.text_input(
        "Question",
        placeholder="When was I nervous about my job interview?",
        label_visibility="collapsed",
    )

    if not st.button("Ask AI", type="primary"):
        return

    if not query.strip():
        st.warning("Please enter a question.")
        return

    # ---------------- CALL BACKEND ----------------

    with st.spinner("Searching your memories and generating an answer..."):

        try:
            response = requests.post(
                f"{BACKEND_URL}/chat/",
                headers=get_headers(),
                json={"query": query},
                timeout=120,
            )

            handle_unauthorized(response)

            if response.status_code != 200:
                st.error(get_error(response, "Chat request failed."))
                return

            data = response.json()

        except requests.exceptions.RequestException:
            st.error("Could not connect to the backend.")
            return

    # ---------------- AI ANSWER ----------------

    section_title("AI Answer")

    answer = data.get("answer", "No answer was returned.")

    render_html(
        f"""
        <div class="journal-card">
            <div class="journal-content">{safe_text(answer)}</div>
        </div>
        """
    )

    # ---------------- RETRIEVED SOURCES ----------------

    sources = data.get("sources", [])

    if not sources:
        return

    section_title("Retrieved memories")

    for source in sources:

        source_id = source.get("id", "Unknown")
        source_content = source.get("content", "")
        similarity = source.get("similarity")

        if isinstance(similarity, (int, float)):
            similarity_text = f"Similarity: {similarity:.3f}"
        else:
            similarity_text = ""

        render_html(
            f"""
            <div class="source-card">
                <div class="source-title">MEMORY #{safe_text(source_id)}</div>
                <div class="source-content">{safe_text(source_content)}</div>
                <div class="similarity">{similarity_text}</div>
            </div>
            """
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

PAGES = {
    "Dashboard": dashboard,
    "New Journal": create_journal,
    "My Journals": view_journals,
    "Ask AI": ai_chat,
}


def main():

    if st.session_state.access_token is None:
        show_flash()
        login()
        return

    sidebar()
    show_flash()

    page_function = PAGES.get(st.session_state.page, dashboard)
    page_function()


main()