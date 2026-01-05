"""
Unified Agentic AI Platform
Main Streamlit application entry point.
"""

import streamlit as st
import os
import logging

# -------------------------------------------------
# OPTIONAL dotenv loading (SAFE FOR STREAMLIT CLOUD)
# -------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional in production (Streamlit Cloud)
    pass

# -------------------------------------------------
# Logging configuration
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Streamlit page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="🧠 Unified Agentic AI Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# Custom CSS
# -------------------------------------------------
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
    }
    .section-header {
        margin: 2rem 0 1rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# Initialization
# -------------------------------------------------
def initialize_app():
    """Initialize the application safely for local + cloud."""

    try:
        # 1️⃣ Read secrets (Streamlit Cloud preferred)
        groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        langchain_api_key = st.secrets.get("LANGCHAIN_API_KEY", os.getenv("LANGCHAIN_API_KEY"))

        if not groq_api_key:
            st.error("❌ GROQ_API_KEY is not set (Streamlit Secrets or .env).")
            st.stop()

        if not langchain_api_key:
            st.error("❌ LANGCHAIN_API_KEY is not set (Streamlit Secrets or .env).")
            st.stop()

        # 2️⃣ Inject into environment for LangChain / LangGraph
        os.environ["GROQ_API_KEY"] = groq_api_key
        os.environ["LANGSMITH_API_KEY"] = langchain_api_key

        # 3️⃣ Initialize session state
        from unified_src.utils.helpers import initialize_session_state
        initialize_session_state()

        return True

    except Exception as e:
        logger.exception("Initialization error")
        st.error(f"❌ Initialization failed: {e}")
        return False


# -------------------------------------------------
# Sidebar
# -------------------------------------------------
def render_sidebar():
    """Render sidebar navigation."""

    with st.sidebar:
        st.title("🧠 Unified Agentic AI")
        st.divider()

        st.subheader("📚 Modules")

        module_options = {
            "chatbot": ("🧠 Agentic Chatbot", "Conversational AI"),
            "web_chatbot": ("🌐 Web Search Chatbot", "Web-grounded chat"),
            "news_generator": ("📰 AI News Generator", "News briefings"),
            "blog_generator": ("✍️ Blog Generator", "SEO blogs"),
            "report_generator": ("📝 AI Report Generator", "Professional reports"),
            "research_qa": ("🔍 Research Q&A", "URL-based Q&A"),
            "settings": ("⚙️ Settings", "Platform configuration"),
        }

        selected_module = st.radio(
            "Select a module:",
            options=list(module_options.keys()),
            format_func=lambda x: module_options[x][0],
            key="module_selector"
        )

        st.divider()

        with st.expander("ℹ️ Help & Documentation"):
            label, desc = module_options[selected_module]
            st.markdown(f"### {label}")
            st.write(desc)

        st.divider()
        st.caption("🚀 Powered by LangChain, LangGraph & Groq")
        st.caption("v1.0.0 | Production-ready")

        return selected_module


# -------------------------------------------------
# Module Renderer
# -------------------------------------------------
def render_module(module_name: str):
    """Lazy-load and render selected module."""

    try:
        if module_name == "chatbot":
            from unified_src.ui.chatbot_ui import render_chatbot_ui
            render_chatbot_ui()

        elif module_name == "web_chatbot":
            from unified_src.ui.web_chatbot_ui import render_web_chatbot_ui
            render_web_chatbot_ui()

        elif module_name == "news_generator":
            from unified_src.ui.news_generator_ui import render_news_generator_ui
            render_news_generator_ui()

        elif module_name == "blog_generator":
            from unified_src.ui.blog_generator_ui import render_blog_generator_ui
            render_blog_generator_ui()

        elif module_name == "report_generator":
            from unified_src.ui.report_generator_ui import render_report_generator_ui
            render_report_generator_ui()

        elif module_name == "research_qa":
            from unified_src.ui.research_qa_ui import render_research_qa_ui
            render_research_qa_ui()

        elif module_name == "settings":
            from unified_src.ui.settings_ui import render_settings_ui
            render_settings_ui()

        else:
            st.error(f"Unknown module: {module_name}")

    except Exception as e:
        logger.exception(f"Module render error: {module_name}")
        st.error(f"❌ Error rendering module: {e}")


# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    if not initialize_app():
        return

    selected_module = render_sidebar()
    render_module(selected_module)


if __name__ == "__main__":
    main()
