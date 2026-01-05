"""
Unified Agentic AI Platform
Main Streamlit application entry point.
"""
import streamlit as st
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="🧠 Unified Agentic AI Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
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


def initialize_app():
    """Initialize the application."""
    try:
        # Validate environment variables
        groq_api_key = os.getenv("GROQ_API_KEY")
        langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
        
        if not groq_api_key:
            st.error("❌ GROQ_API_KEY environment variable is not set.")
            st.stop()
        
        if not langchain_api_key:
            st.error("❌ LANGCHAIN_API_KEY environment variable is not set.")
            st.stop()
        
        # Set LangSmith API key for tracing
        os.environ["LANGSMITH_API_KEY"] = langchain_api_key
        
        # Initialize session state
        from unified_src.utils.helpers import initialize_session_state
        initialize_session_state()
        
        return True
    
    except Exception as e:
        st.error(f"❌ Initialization failed: {str(e)}")
        logger.exception("Application initialization error")
        return False


def render_sidebar():
    """Render the sidebar with module selection."""
    with st.sidebar:
        st.title("🧠 Unified Agentic AI")
        st.divider()
        
        # Module selection
        st.subheader("📚 Modules")
        
        module_options = {
            "chatbot": ("🧠 Agentic Chatbot", "Basic conversational AI"),
            "web_chatbot": ("🌐 Web Search Chatbot", "Chat with web search integration"),
            "news_generator": ("📰 AI News Generator", "Generate news briefings"),
            "blog_generator": ("✍️ Blog Generator", "Create blog posts"),
            "report_generator": ("📝 AI Report Generator", "Generate comprehensive reports"),
            "research_qa": ("🔍 Research Q&A", "Ask questions based on URLs"),
            "settings": ("⚙️ Settings", "Configure the platform")
        }
        
        selected_module = st.radio(
            "Select a module:",
            options=list(module_options.keys()),
            format_func=lambda x: module_options[x][0],
            key="module_selector"
        )
        
        st.divider()
        
        # Help section
        with st.expander("ℹ️ Help & Documentation"):
            module_info = module_options.get(selected_module)
            if module_info:
                st.markdown(f"### {module_info[0]}")
                st.write(module_info[1])
                
                if selected_module == "chatbot":
                    st.markdown("""
                    - Have natural conversations
                    - Maintain context across messages
                    - Clear chat history anytime
                    """)
                
                elif selected_module == "web_chatbot":
                    st.markdown("""
                    - Ask questions about current topics
                    - Get web-grounded responses
                    - View sources for claims
                    - Toggle web search on/off
                    """)
                
                elif selected_module == "news_generator":
                    st.markdown("""
                    - Select news categories
                    - Choose briefing timeframe (daily/weekly/monthly)
                    - Pick writing tone (formal/casual/technical)
                    - Download as markdown
                    """)
                
                elif selected_module == "blog_generator":
                    st.markdown("""
                    - Enter topic and keywords
                    - Auto-generate SEO-optimized titles
                    - Create structured blog posts
                    - Download as markdown
                    """)
                
                elif selected_module == "report_generator":
                    st.markdown("""
                    - Generate comprehensive reports
                    - Multiple template options (technical, business, research)
                    - Extract data from URLs and web search
                    - Auto-generated citations
                    - Download as markdown
                    """)
                
                elif selected_module == "research_qa":
                    st.markdown("""
                    - Ask questions about specific URLs
                    - Get grounded answers with citations
                    - Multiple source integration
                    - Export Q&A responses
                    - Fast, accurate retrieval
                    """)
                
                elif selected_module == "settings":
                    st.markdown("""
                    - Configure LLM parameters
                    - Customize UI settings
                    - Test API connections
                    - Manage session data
                    """)
        
        st.divider()
        
        # Footer
        st.caption("🚀 Powered by LangChain, LangGraph, and Groq")
        st.caption("v1.0.0 | Built for Enterprise AI")
        
        return selected_module


def render_module(module_name: str):
    """Render the selected module."""
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
        st.error(f"❌ Error rendering module: {str(e)}")
        logger.exception(f"Error rendering module {module_name}")


def main():
    """Main application function."""
    # Initialize app
    if not initialize_app():
        return
    
    # Render sidebar and get selected module
    selected_module = render_sidebar()
    
    # Render the selected module
    render_module(selected_module)


if __name__ == "__main__":
    main()
