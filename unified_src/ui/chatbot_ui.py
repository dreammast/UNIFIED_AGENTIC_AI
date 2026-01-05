"""
UI component for Basic Chatbot.
"""
import streamlit as st
from langchain_core.messages import HumanMessage
from unified_src.services.llm_service import get_llm
from unified_src.agents.chatbot import create_chatbot_graph
from unified_src.utils.helpers import (
    initialize_session_state, get_module_state, update_module_state,
    display_error, display_success
)


def render_chatbot_ui():
    """Render the basic chatbot interface."""
    st.header("🧠 Agentic Chatbot")
    st.write("Have an intelligent conversation with the AI assistant.")
    
    initialize_session_state()
    
    # Get or initialize chatbot state
    chatbot_state = get_module_state("chatbot")
    if "messages" not in chatbot_state:
        chatbot_state["messages"] = []
    
    # Display chat history
    st.subheader("Conversation")
    
    for message in chatbot_state["messages"]:
        if hasattr(message, 'content'):
            content = message.content
        else:
            content = str(message)
        
        if isinstance(message, HumanMessage) or (isinstance(message, dict) and message.get('role') == 'user'):
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)
    
    # Input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        chatbot_state["messages"].append(HumanMessage(content=user_input))
        update_module_state("chatbot", chatbot_state)
        
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response from graph
        try:
            llm = get_llm()
            graph = create_chatbot_graph(llm)
            
            with st.spinner("Generating response..."):
                state = {
                    "messages": chatbot_state["messages"]
                }
                result = graph.invoke(state)
                
                # Update state with new messages
                chatbot_state["messages"] = result["messages"]
                update_module_state("chatbot", chatbot_state)
                
                # Show assistant response (last message)
                if result["messages"]:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        content = last_message.content
                    else:
                        content = str(last_message)
                    
                    with st.chat_message("assistant"):
                        st.write(content)
                    
                    display_success("Response generated successfully!")
        
        except Exception as e:
            display_error(f"Failed to generate response: {str(e)}")
            # Remove the user message if processing failed
            chatbot_state["messages"].pop()
            update_module_state("chatbot", chatbot_state)
            st.rerun()
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Chatbot Controls")
        
        if st.button("Clear Chat History"):
            chatbot_state["messages"] = []
            update_module_state("chatbot", chatbot_state)
            display_success("Chat history cleared!")
            st.rerun()
