"""
Configuration settings for the Unified Agentic AI Platform.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings and environment variables."""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    
    # LLM Configuration
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 2048
    
    # UI Configuration
    PAGE_TITLE = "🧠 Unified Agentic AI Platform"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    
    # Module Names
    MODULES = {
        "chatbot": "🧠 Agentic Chatbot",
        "web_chatbot": "🌐 Chatbot with Web Search",
        "news_generator": "📰 AI News Generator",
        "blog_generator": "✍️ Blog Generator",
        "settings": "⚙️ Settings"
    }
    
    # Paths
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        if not cls.LANGCHAIN_API_KEY:
            raise ValueError("LANGCHAIN_API_KEY environment variable is not set.")


# Initialize settings
settings = Settings()
