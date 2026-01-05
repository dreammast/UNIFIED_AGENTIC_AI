"""
Basic Chatbot Agent - Unified implementation.
"""
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import Dict, Any, List
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.services.states import ChatState


class ChatbotNode:
    """Node for basic chatbot functionality."""
    
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = """You are a helpful and intelligent AI assistant. 
        You provide accurate, concise, and helpful responses to user queries.
        You maintain context from the conversation history.
        Be friendly and professional in your tone."""
    
    def process(self, state: ChatState) -> Dict[str, Any]:
        """Process user message and generate response."""
        messages = state.get("messages", [])
        
        if not messages:
            return state
        
        # Get the last user message
        last_message = messages[-1]
        
        # Prepare messages for LLM
        llm_messages = [{"role": "system", "content": self.system_prompt}]
        
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


class ChatbotGraph:
    """LangGraph-based chatbot."""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder = StateGraph(ChatState)
        self.chatbot_node = ChatbotNode(llm)
    
    def build(self):
        """Build the graph."""
        self.graph_builder.add_node("chatbot", self.chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
        
        return self.graph_builder.compile()


def create_chatbot_graph(llm):
    """Create and return compiled chatbot graph."""
    graph_builder = ChatbotGraph(llm)
    return graph_builder.build()
