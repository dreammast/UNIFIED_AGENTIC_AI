"""
UI component for Settings.
"""
import streamlit as st
from unified_src.utils.helpers import (
    initialize_session_state, get_setting, update_setting,
    display_success, display_info
)


def render_settings_ui():
    """Render the settings interface."""
    st.header("⚙️ Settings")
    st.write("Configure the Unified Agentic AI Platform.")
    
    initialize_session_state()
    
    # LLM Settings
    st.subheader("🤖 LLM Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=get_setting("temperature", 0.7),
            step=0.1,
            help="Controls randomness: 0 = deterministic, 2 = very random"
        )
        update_setting("temperature", temperature)
    
    with col2:
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=256,
            max_value=4096,
            value=get_setting("max_tokens", 2048),
            step=256,
            help="Maximum length of generated responses"
        )
        update_setting("max_tokens", max_tokens)
    
    # UI Settings
    st.subheader("🎨 UI Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "Theme",
            ["light", "dark", "auto"],
            index=["light", "dark", "auto"].index(get_setting("theme", "light"))
        )
        update_setting("theme", theme)
    
    with col2:
        enable_memory = st.checkbox(
            "Enable Conversation Memory",
            value=get_setting("enable_memory", True),
            help="Save conversation history across sessions"
        )
        update_setting("enable_memory", enable_memory)
    
    # Advanced Settings
    with st.expander("🔧 Advanced Settings"):
        st.subheader("Custom System Prompt")
        
        custom_prompt = st.text_area(
            "System Prompt (for chatbots)",
            value=get_setting("custom_system_prompt", ""),
            placeholder="Enter a custom system prompt...",
            height=150,
            help="Override the default system prompt for chatbot modules"
        )
        
        if custom_prompt:
            update_setting("custom_system_prompt", custom_prompt)
            display_info("Custom system prompt will be used in chatbot modules.")
        
        # Model selection
        st.subheader("Model Information")
        st.info("""
        **Current Model:** meta-llama/llama-4-scout-17b-16e-instruct
        
        **Provider:** Groq
        
        **Capabilities:**
        - General conversation and reasoning
        - Code generation and explanation
        - Content creation and summarization
        - Web-grounded responses (with search integration)
        """)
    
    # API Configuration
    st.subheader("🔐 API Configuration")
    
    st.info("""
    API keys are loaded from environment variables:
    - `GROQ_API_KEY` - Required for LLM
    - `LANGCHAIN_API_KEY` - Required for LangChain
    - `TAVILY_API_KEY` - Optional, enables web search
    
    Please ensure these are set in your `.env` file.
    """)
    
    if st.button("Test API Connection"):
        try:
            from unified_src.services.llm_service import get_llm
            llm = get_llm()
            
            # Test simple invocation
            response = llm.invoke("Say 'API connection successful!' in 5 words or less.")
            
            st.success("✅ API Connection Successful!")
            st.write(f"**Response:** {response.content}")
        except Exception as e:
            st.error(f"❌ API Connection Failed: {str(e)}")
    
    # Session Management
    st.subheader("📊 Session Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Temperature", f"{get_setting('temperature', 0.7):.1f}")
    
    with col2:
        st.metric("Max Tokens", get_setting("max_tokens", 2048))
    
    with col3:
        st.metric("Memory Enabled", "Yes" if get_setting("enable_memory", True) else "No")
    
    # Clear session data
    st.divider()
    st.subheader("🗑️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear All Chat History"):
            st.session_state.module_states = {
                "chatbot": {},
                "web_chatbot": {},
                "news_generator": {},
                "blog_generator": {},
            }
            display_success("All chat histories cleared!")
            st.rerun()
    
    with col2:
        if st.button("Reset Settings to Default"):
            st.session_state.settings = {
                "temperature": 0.7,
                "max_tokens": 2048,
                "enable_memory": True,
                "theme": "light"
            }
            display_success("Settings reset to default!")
            st.rerun()
    
    # About
    st.divider()
    st.subheader("ℹ️ About")
    
    st.markdown("""
    **Unified Agentic AI Platform v1.0**
    
    A comprehensive platform combining:
    - 🧠 Agentic Chatbot
    - 🌐 Web Search Integration
    - 📰 AI News Generation
    - ✍️ Blog Post Generation
    
    Powered by:
    - LangChain & LangGraph
    - Groq LLM
    - Streamlit
    
    Built with best practices in agent architecture and prompt engineering.
    """)
