"""
Web Search Chatbot Agent - Unified implementation.
"""
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, List
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.services.states import WebChatState, SearchResult

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


class WebSearchNode:
    """Node for web search functionality."""
    
    def __init__(self, llm):
        self.llm = llm
        self.tavily_client = None
        
        if TAVILY_AVAILABLE:
            import os
            api_key = os.getenv("TAVILY_API_KEY")
            if api_key:
                try:
                    self.tavily_client = TavilyClient(api_key=api_key)
                except Exception as e:
                    st.warning(f"Could not initialize Tavily: {e}")
    
    def search(self, query: str) -> List[SearchResult]:
        """Perform web search."""
        if not self.tavily_client:
            st.warning("Web search not available. Please set TAVILY_API_KEY.")
            return []
        
        try:
            response = self.tavily_client.search(query, max_results=5)
            results = []
            
            for result in response.get("results", []):
                search_result = SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("content", ""),
                    source=result.get("source", "")
                )
                results.append(search_result)
            
            return results
        except Exception as e:
            st.error(f"Search error: {e}")
            return []
    
    def process(self, state: WebChatState) -> Dict[str, Any]:
        """Process user message with web search."""
        messages = state.get("messages", [])
        
        if not messages:
            return state
        
        # Get the last user message
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Perform web search if enabled
        search_results = []
        if state.get("use_web_search", True):
            search_results = self.search(user_query)
            state["search_results"] = search_results
        
        # Prepare context from search results
        context = ""
        if search_results:
            context = "\n\nWeb Search Results:\n"
            for i, result in enumerate(search_results, 1):
                context += f"{i}. {result.title}\n   {result.snippet}\n   Source: {result.source}\n\n"
        
        # Prepare system prompt with search context
        system_prompt = f"""You are a helpful AI assistant with access to web search results.
        Use the provided search results to ground your answers in real information.
        Always cite your sources when using information from the search results.
        Be accurate and helpful.
        
        {context if context else "No web search results available."}
        """
        
        # Prepare messages for LLM
        llm_messages = [{"role": "system", "content": system_prompt}]
        
        for msg in messages:
            if isinstance(msg, dict):
                llm_messages.append(msg)
            elif isinstance(msg, HumanMessage):
                llm_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                llm_messages.append({"role": "assistant", "content": msg.content})
        
        # Get response from LLM
        response = self.llm.invoke(llm_messages)
        
        # Add response to messages
        messages.append(AIMessage(content=response.content))
        state["messages"] = messages
        
        return state


class WebChatbotGraph:
    """LangGraph-based web-enabled chatbot."""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder = StateGraph(WebChatState)
        self.web_search_node = WebSearchNode(llm)
    
    def build(self):
        """Build the graph."""
        self.graph_builder.add_node("web_chatbot", self.web_search_node.process)
        self.graph_builder.add_edge(START, "web_chatbot")
        self.graph_builder.add_edge("web_chatbot", END)
        
        return self.graph_builder.compile()


def create_web_chatbot_graph(llm):
    """Create and return compiled web chatbot graph."""
    graph_builder = WebChatbotGraph(llm)
    return graph_builder.build()
