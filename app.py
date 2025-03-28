import streamlit as st
from streamlit_chat import message
from main import BlogForge
import asyncio
import uuid
import time
from streamlit_mermaid import st_mermaid
import re
import hashlib

# Page config
st.set_page_config(
    page_title="BlogForge - AI-Powered Content Creation", page_icon="✍️", layout="wide"
)

# Initialize session state
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "input_keywords" not in st.session_state:
    st.session_state.input_keywords = ""


def render_markdown_with_mermaid(content, key_suffix=""):
    """Separate mermaid diagrams from regular markdown with unique keys"""
    # Generate a unique hash for the content
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]

    mermaid_blocks = re.findall(r"```mermaid(.*?)```", content, re.DOTALL)
    other_content = re.sub(r"```mermaid.*?```", "", content, flags=re.DOTALL)

    # Render regular markdown
    if other_content.strip():
        st.markdown(other_content)

    # Render each mermaid diagram with unique key
    for i, diagram in enumerate(mermaid_blocks):
        st_mermaid(
            diagram.strip(),
            height="300px",
            key=f"mermaid_{content_hash}_{i}_{key_suffix}",
        )


def validate_keywords(keyword_list):
    """Validate keywords before processing"""
    if not keyword_list:
        st.error("Please enter at least one keyword")
        return False
    if len(keyword_list) > 5:
        st.error("Maximum 5 keywords allowed. Please remove extra keywords.")
        return False
    return True


def initialize_session(keywords: list):
    """Create new BlogForge session"""
    session_id = str(uuid.uuid4())
    session_name = ", ".join(keywords)[:50] + (
        "..." if len(", ".join(keywords)) > 50 else ""
    )

    blog_forge = BlogForge(keywords=keywords, session_id=session_id)

    st.session_state.sessions[session_id] = {
        "name": session_name,
        "instance": blog_forge,
        "history": [],
    }
    st.session_state.current_session = session_id
    return blog_forge


async def process_initial_generation(blog_forge):
    with st.spinner("🔍 Researching top articles and generating your blog post..."):
        blog_post, history = await blog_forge.forge()

    st.session_state.sessions[st.session_state.current_session]["history"] = history
    return blog_post


async def process_chat(blog_forge, query):
    with st.spinner("💭 Thinking..."):
        response, new_history = await blog_forge.chat(query)

    st.session_state.sessions[st.session_state.current_session]["history"] = new_history
    return response


# Sidebar
with st.sidebar:
    st.title("✍️ BlogForge")
    st.caption("AI-powered content alchemy - transform trends into golden blogs")

    if st.button("+ New Blog Session"):
        st.session_state.current_session = None

    st.markdown("### Your Sessions")

    for session_id, session_data in st.session_state.sessions.items():
        if st.button(session_data["name"], key=f"btn_{session_id}"):
            st.session_state.current_session = session_id

    st.markdown("---")
    st.markdown(
        """
    **How it works:**
    1. Enter 1-5 keywords (one per line)
    2. We research top articles
    3. Generate fresh content
    4. Chat to refine further
    """
    )

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    if not st.session_state.current_session:
        st.title("Start New Blog")
        st.markdown("Enter 1-5 trending keywords (one per line):")

        keywords = st.text_area(
            "Keywords",
            placeholder="MCP servers\ncloud computing\n2024 trends",
            height=150,
            label_visibility="collapsed",
            help="Maximum 5 keywords allowed",
        )

        if st.button("Generate Blog Post", type="primary"):
            keyword_list = [k.strip() for k in keywords.split("\n") if k.strip()]
            if validate_keywords(keyword_list):
                blog_forge = initialize_session(keyword_list)
                blog_post = asyncio.run(process_initial_generation(blog_forge))
                st.rerun()

    else:
        session_data = st.session_state.sessions[st.session_state.current_session]
        blog_forge = session_data["instance"]
        history = session_data["history"]

        st.title(session_data["name"])

        for msg in history:
            if msg["role"] == "human":
                message(
                    msg["content"], is_user=True, key=f"human_{hash(msg['content'])}"
                )
            else:
                if "```mermaid" in msg["content"]:
                    render_markdown_with_mermaid(
                        msg["content"], key_suffix=msg["session_id"]
                    )
                else:
                    message(msg["content"], key=f"ai_{hash(msg['content'])}")

        if prompt := st.chat_input("Ask to refine the blog..."):
            message(prompt, is_user=True, key=f"human_{int(time.time())}")
            response = asyncio.run(process_chat(blog_forge, prompt))
            message(response, key=f"ai_{int(time.time())}")
            st.rerun()

with col2:
    if st.session_state.current_session:
        st.markdown("### Blog Preview")
        if history:
            latest_ai_messages = [
                msg["content"] for msg in history if msg["role"] == "ai"
            ]
            if latest_ai_messages:
                st.markdown(latest_ai_messages[-1])

        st.download_button(
            "Download Blog",
            latest_ai_messages[-1] if latest_ai_messages else "",
            file_name=f"{session_data['name']}.md",
            mime="text/markdown",
        )
