"""
Unified LLM Service for managing LLM initialization and configuration.
"""
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


class LLMService:
    """Service for managing LLM initialization across all modules."""
    
    _instance = None
    _llm = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize LLM service."""
        if self._llm is None:
            self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the Groq LLM."""
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set.")
            
            os.environ["GROQ_API_KEY"] = groq_api_key
            
            # Initialize Groq LLM
            self._llm = ChatGroq(
                api_key=groq_api_key,
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.7,
                max_tokens=2048
            )
        except Exception as e:
            raise ValueError(f"Error initializing LLM: {e}")
    
    def get_llm(self):
        """Get the initialized LLM instance."""
        if self._llm is None:
            self._initialize_llm()
        return self._llm
    
    def reset(self):
        """Reset the LLM instance (useful for testing)."""
        self._llm = None
        self._initialize_llm()


# Convenience function
def get_llm():
    """Get the LLM instance."""
    service = LLMService()
    return service.get_llm()
