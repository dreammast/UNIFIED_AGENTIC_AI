"""
UI component for Basic Chatbot.
"""
import streamlit as st
from langchain_core.messages import HumanMessage
from unified_src.services.llm_service import get_llm
from unified_src.services.pdf_exporter import PDFExporter
from unified_src.services.content_processor import ContentProcessor
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
            
            graph = create_chatbot_graph(llm)
            
            with st.spinner("Generating response..."):
                # Processing Multimodal Inputs (from session state or UI)
                # Note: We need to check if these controls exist in sidebar, or we can look at state
                # BUT since this is a rerun, we grab from sidebar widgets directly if possible or store in session state.
                
                # To simplify, we will assume the sidebar inputs write to session_state or we access them here.
                # However, Streamlit UI rendering happens top-down. The sidebar code is BELOW.
                # We need to move Sidebar controls UP or read them after.
                # Actually, standard Streamlit pattern is sidebar first.
                # Refactoring render_chatbot_ui to put sidebar first would be best, but large refactor.
                # Instead, I will use st.session_state to keys.
                
                uploaded_files = st.session_state.get("chat_files", [])
                url_input = st.session_state.get("chat_url", "")
                
                extracted_context = ""
                if uploaded_files or url_input:
                     with st.spinner("Analyzing uploaded content..."):
                         urls = [url_input] if url_input else []
                         extracted_context = ContentProcessor.process_content_list(files=uploaded_files, urls=urls)
                
                state = {
                    "messages": chatbot_state["messages"],
                    "extracted_context": extracted_context,
                    "uploaded_files": [f.name for f in uploaded_files] if uploaded_files else []
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
            
        st.divider()
        st.write("📂 **Multimodal Input**")
        st.file_uploader(
            "Upload files (PDF, TXT, MD)", 
            type=["pdf", "txt", "md"], 
            accept_multiple_files=True,
            key="chat_files"
        )
        st.text_input("Analyze URL", placeholder="https://example.com", key="chat_url")
            
        if chatbot_state["messages"]:
            st.divider()
            st.download_button(
                label="📥 Export Chat to PDF",
                data=PDFExporter.export_chat_history("Agentic Chatbot History", chatbot_state["messages"]),
                file_name="chat_history.pdf",
                mime="application/pdf"
            )
