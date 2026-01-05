"""
UI component for Web Search Chatbot.
"""
import streamlit as st
from langchain_core.messages import HumanMessage
from unified_src.services.llm_service import get_llm
from unified_src.agents.web_chatbot import create_web_chatbot_graph
from unified_src.utils.helpers import (
    initialize_session_state, get_module_state, update_module_state,
    display_error, display_success, display_info
)


def render_web_chatbot_ui():
    """Render the web search chatbot interface."""
    st.header("🌐 Chatbot with Web Search")
    st.write("Ask questions and get answers grounded in real-time web information.")
    
    initialize_session_state()
    
    # Sidebar settings
    with st.sidebar:
        st.subheader("Web Search Settings")
        use_web_search = st.checkbox("Enable Web Search", value=True)
    
    # Get or initialize web chatbot state
    web_chatbot_state = get_module_state("web_chatbot")
    if "messages" not in web_chatbot_state:
        web_chatbot_state["messages"] = []
    if "search_results" not in web_chatbot_state:
        web_chatbot_state["search_results"] = []
    
    web_chatbot_state["use_web_search"] = use_web_search
    
    # Display chat history
    st.subheader("Conversation")
    
    for message in web_chatbot_state["messages"]:
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
    user_input = st.chat_input("Ask a question...")
    
    if user_input:
        # Add user message to chat history
        web_chatbot_state["messages"].append(HumanMessage(content=user_input))
        update_module_state("web_chatbot", web_chatbot_state)
        
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response from graph
        try:
            llm = get_llm()
            graph = create_web_chatbot_graph(llm)
            
            with st.spinner("Searching web and generating response..."):
                state = {
                    "messages": web_chatbot_state["messages"],
                    "search_results": web_chatbot_state.get("search_results", []),
                    "use_web_search": use_web_search
                }
                result = graph.invoke(state)
                
                # Update state with new messages and search results
                web_chatbot_state["messages"] = result["messages"]
                web_chatbot_state["search_results"] = result.get("search_results", [])
                update_module_state("web_chatbot", web_chatbot_state)
                
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
                    
                    # Show search results if available
                    if result.get("search_results") and use_web_search:
                        with st.expander("📚 Web Search Sources"):
                            for i, result_item in enumerate(result["search_results"], 1):
                                st.markdown(f"**{i}. {result_item.title}**")
                                st.caption(f"Source: {result_item.source}")
                                st.write(result_item.snippet)
                                st.markdown(f"[Read more]({result_item.url})")
                                st.divider()
        
        except Exception as e:
            display_error(f"Failed to generate response: {str(e)}")
            # Remove the user message if processing failed
            web_chatbot_state["messages"].pop()
            update_module_state("web_chatbot", web_chatbot_state)
            st.rerun()
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Chat Controls")
        
        if st.button("Clear Chat History"):
            web_chatbot_state["messages"] = []
            web_chatbot_state["search_results"] = []
            update_module_state("web_chatbot", web_chatbot_state)
            display_success("Chat history cleared!")
            st.rerun()
