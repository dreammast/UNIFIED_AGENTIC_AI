"""
UI component for Research Q&A.
"""
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.agents.research_agent import create_research_qa_graph
from unified_src.services.markdown_exporter import MarkdownExporter
from unified_src.utils.helpers import (
    initialize_session_state, get_module_state, update_module_state,
    display_error, display_success, display_info
)
import logging

logger = logging.getLogger(__name__)


def render_research_qa_ui():
    """Render the research Q&A interface."""
    st.header("🔍 Research-Driven Q&A")
    st.write("Ask questions about content from specific URLs. Get grounded answers with citations.")
    
    initialize_session_state()
    
    # Get or initialize research state
    research_state = get_module_state("research_qa")
    
    # Input form
    st.subheader("Ask a Question Based on URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        question = st.text_area(
            "Your Question",
            placeholder="What is the main topic of these articles?",
            height=100,
            key="research_question"
        )
    
    with col2:
        urls_input = st.text_area(
            "URLs (comma-separated)",
            placeholder="https://example.com/article1, https://example.com/article2",
            height=100,
            key="research_urls"
        )
    
    # Parse URLs
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]
    
    # Generate button
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ask_button = st.button("🔍 Get Answer", use_container_width=True, type="primary")
    
    if ask_button:
        # Validation
        if not question:
            display_error("Please enter a question!")
            return
        
        if not urls:
            display_error("Please provide at least one URL!")
            return
        
        # Initialize research state
        state = {
            "question": question,
            "urls": urls,
            "chunks": None,
            "retrieved_chunks": None,
            "answer": None,
            "citations": [],
            "sources": None,
            "error": None
        }
        
        try:
            llm = get_llm()
            graph = create_research_qa_graph(llm)
            
            progress_placeholder = st.empty()
            progress_placeholder.info("⏳ Processing URLs and generating answer... This may take a moment.")
            
            with st.spinner("🔄 Analyzing content..."):
                result = graph.invoke(state)
            
            progress_placeholder.empty()
            
            if result.get("error"):
                display_error(result["error"])
                return
            
            answer = result.get("answer")
            citations = result.get("citations", [])
            
            if answer:
                # Save to session state
                research_state["last_answer"] = answer
                research_state["last_citations"] = citations
                update_module_state("research_qa", research_state)
                
                display_success("Answer generated successfully!")
                
                # Display the answer
                st.divider()
                st.subheader("📋 Answer")
                
                # Display question
                with st.expander("❓ Question", expanded=True):
                    st.markdown(f"**{question}**")
                
                # Display answer
                st.markdown(answer)
                
                # Display sources
                if citations:
                    st.divider()
                    st.subheader("📚 Sources")
                    
                    for citation in citations:
                        with st.expander(f"[{citation.index}] {citation.title}"):
                            st.write(f"**URL:** {citation.url}")
                            if citation.accessed_date:
                                st.write(f"**Accessed:** {citation.accessed_date}")
                            st.write(f"**Excerpt:** {citation.excerpt}")
                
                # Download options
                st.divider()
                st.subheader("📥 Export")
                
                # Create markdown content
                exporter = MarkdownExporter()
                citations_list = [
                    {
                        "index": c.index,
                        "title": c.title,
                        "url": c.url,
                        "accessed_date": c.accessed_date
                    }
                    for c in citations
                ]
                
                markdown_content = exporter.export_qa_response(
                    question=question,
                    answer=answer,
                    citations=citations_list
                )
                
                # Download button
                md_filename = exporter.sanitize_filename(f"qa_response_{question[:30]}.md")
                md_bytes = exporter.get_markdown_bytes(markdown_content)
                
                st.download_button(
                    label="📥 Download Q&A as Markdown",
                    data=md_bytes,
                    file_name=md_filename,
                    mime="text/markdown",
                    use_container_width=True
                )
                
                # Show markdown preview
                with st.expander("Preview Markdown"):
                    st.code(markdown_content, language="markdown")
            else:
                display_error("No answer was generated.")
        
        except Exception as e:
            display_error(f"Q&A processing failed: {str(e)}")
            logger.exception("Research Q&A error")
    
    # Display tips
    with st.expander("💡 Tips for Better Answers"):
        st.markdown("""
        - **Specific Questions**: Ask clear, specific questions about the content
        - **Relevant URLs**: Provide URLs directly related to your question
        - **Simple Questions**: Simpler questions tend to get more accurate answers
        - **Multiple Sources**: Using 2-3 URLs helps provide more comprehensive answers
        - **Follow-up Questions**: You can ask follow-up questions in separate queries
        """)
    
    # Display recent queries
    if research_state.get("last_answer"):
        st.divider()
        with st.expander("📜 View Last Query"):
            st.markdown(f"**Question:** {research_state.get('last_question', 'N/A')}")
            st.markdown(f"**Answer:** {research_state.get('last_answer', 'N/A')[:500]}...")
