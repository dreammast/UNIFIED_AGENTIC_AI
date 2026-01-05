"""
Utility functions for the unified platform.
"""
import streamlit as st
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "current_module" not in st.session_state:
        st.session_state.current_module = "chatbot"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    
    if "module_states" not in st.session_state:
        st.session_state.module_states = {
            "chatbot": {},
            "web_chatbot": {},
            "news_generator": {},
            "blog_generator": {},
            "report_generator": {},
            "research_qa": {},
        }
    
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "enable_memory": True,
            "theme": "light"
        }


def get_module_state(module_name: str) -> Dict[str, Any]:
    """Get state for a specific module."""
    initialize_session_state()
    return st.session_state.module_states.get(module_name, {})


def update_module_state(module_name: str, updates: Dict[str, Any]):
    """Update state for a specific module."""
    initialize_session_state()
    st.session_state.module_states[module_name].update(updates)


def display_error(message: str):
    """Display an error message in the UI."""
    st.error(f"❌ Error: {message}")
    logger.error(message)


def display_success(message: str):
    """Display a success message in the UI."""
    st.success(f"✅ {message}")
    logger.info(message)


def display_info(message: str):
    """Display an info message in the UI."""
    st.info(f"ℹ️ {message}")
    logger.info(message)


def display_warning(message: str):
    """Display a warning message in the UI."""
    st.warning(f"⚠️ {message}")
    logger.warning(message)


def format_response(content: str, title: Optional[str] = None) -> str:
    """Format a response for display."""
    if title:
        return f"**{title}**\n\n{content}"
    return content


def safely_execute(func, *args, **kwargs) -> Optional[Any]:
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        display_error(f"Execution failed: {str(e)}")
        logger.exception(f"Error executing {func.__name__}")
        return None


def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value."""
    initialize_session_state()
    return st.session_state.settings.get(key, default)


def update_setting(key: str, value: Any):
    """Update a setting value."""
    initialize_session_state()
    st.session_state.settings[key] = value


def clear_module_state(module_name: str):
    """Clear state for a specific module."""
    initialize_session_state()
    st.session_state.module_states[module_name] = {}
