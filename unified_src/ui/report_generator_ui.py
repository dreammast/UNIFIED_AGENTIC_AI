"""
UI component for Report Generator.
"""
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.agents.report_generator import create_report_generator_graph
from unified_src.services.markdown_exporter import MarkdownExporter
from unified_src.services.pdf_exporter import PDFExporter
from unified_src.utils.helpers import (
    initialize_session_state, get_module_state, update_module_state,
    display_error, display_success, display_info
)
import logging

logger = logging.getLogger(__name__)


def render_report_generator_ui():
    """Render the report generator interface."""
    st.header("📝 AI Report Generator")
    st.write("Generate comprehensive, professionally formatted reports with citations and web search integration.")
    
    initialize_session_state()
    
    # Sidebar for settings
    with st.sidebar:
        st.subheader("Report Settings")
        tone_options = ["Technical", "Business", "Academic", "Casual"]
        selected_tone = st.selectbox("Tone", tone_options, index=0, key="report_tone")
        
        length_options = ["Short", "Medium", "Long"]
        selected_length = st.selectbox("Length", length_options, index=1, key="report_length")
        
        template_options = ["technical_report", "business_report", "research_report"]
        selected_template = st.selectbox("Template", template_options, index=0, key="report_template")
        
        enable_citations = st.checkbox("Enable Citations", value=True, key="report_citations")
        enable_web_search = st.checkbox("Enable Web Search", value=False, key="report_web_search")
    
    # Get or initialize report state
    report_state = get_module_state("report_generator")
    
    # Input form
    st.subheader("Report Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input(
            "Report Title",
            placeholder="e.g., The Future of Artificial Intelligence",
            key="report_title"
        )
        
        topic = st.text_area(
            "Topic / Description",
            placeholder="Describe the topic and key areas to cover",
            height=100,
            key="report_topic"
        )
    
    with col2:
        query = st.text_area(
            "User Query / Objective",
            placeholder="What should the report focus on?",
            height=100,
            key="report_query"
        )
        
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Executive Leadership, Developers, Researchers",
            key="report_audience"
        )
    
    # URL input
    st.subheader("Data Sources")
    urls_input = st.text_area(
        "URLs (comma-separated, optional)",
        placeholder="https://example.com/article1, https://example.com/article2",
        height=80,
        key="report_urls"
    )
    
    # Parse URLs
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]
    
    # Generate button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        generate_button = st.button("🚀 Generate Report", use_container_width=True, type="primary")
    
    with col2:
        pass
    
    with col3:
        # Placeholder for future features
        pass
    
    if generate_button:
        # Validation
        if not title:
            display_error("Please enter a report title!")
            return
        
        if not topic and not query:
            display_error("Please enter a topic or query!")
            return
        
        # Initialize report state
        state = {
            "title": title,
            "topic": topic,
            "query": query,
            "target_audience": target_audience,
            "tone": selected_tone,
            "length": selected_length,
            "template": selected_template,
            "urls": urls,
            "enable_citations": enable_citations,
            "enable_web_search": enable_web_search,
            "loaded_content": None,
            "search_results": None,
            "report": None,
            "error": None
        }
        
        try:
            llm = get_llm()
            graph = create_report_generator_graph(llm)
            
            progress_placeholder = st.empty()
            progress_placeholder.info("⏳ Generating report... This may take a moment.")
            
            with st.spinner("🔄 Processing..."):
                result = graph.invoke(state)
            
            progress_placeholder.empty()
            
            if result.get("error"):
                display_error(result["error"])
                return
            
            report = result.get("report")
            
            if report:
                # Save to session state
                report_state["generated_report"] = report
                update_module_state("report_generator", report_state)
                
                display_success("Report generated successfully!")
                
                # Display the report
                st.divider()
                st.subheader("📄 Generated Report")
                
                # Display report metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"📊 Tone: {report.metadata.get('tone', 'Unknown')}")
                with col2:
                    st.caption(f"📏 Template: {report.metadata.get('template', 'Unknown')}")
                with col3:
                    st.caption(f"📝 Words: {report.metadata.get('word_count', 'Unknown')}")
                
                st.divider()
                
                # Display report content
                exporter = MarkdownExporter()
                markdown_content = exporter.export_report(report)
                
                # Render markdown
                st.markdown(markdown_content)
                
                # Download button
                st.divider()
                st.subheader("📥 Export Options")
                
                # Markdown download
                md_filename = exporter.sanitize_filename(f"{title}.md")
                md_bytes = exporter.get_markdown_bytes(markdown_content)
                
                st.download_button(
                    label="📥 Download as Markdown (.md)",
                    data=md_bytes,
                    file_name=md_filename,
                    mime="text/markdown",
                    use_container_width=True
                )
                
                # PDF download
                st.download_button(
                    label="📥 Download as PDF (.pdf)",
                    data=PDFExporter.export_report(title, markdown_content),
                    file_name=f"{title}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        except Exception as e:
            display_error(f"Report generation failed: {str(e)}")
            logger.exception("Report generation error")
    
    # Display tips
    with st.expander("💡 Tips for Better Reports"):
        st.markdown("""
        - **Specific Topics**: Be specific about what you want the report to cover
        - **Multiple URLs**: Provide 2-5 URLs for comprehensive research
        - **Clear Objectives**: State what you want to achieve with the report
        - **Target Audience**: Knowing the audience helps shape the tone and complexity
        - **Enable Web Search**: Turn on for the latest information on trending topics
        """)
