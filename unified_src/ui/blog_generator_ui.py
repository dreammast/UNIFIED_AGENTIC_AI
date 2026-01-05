"""
UI component for Blog Generator.
"""
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.agents.blog_generator import create_blog_generator_graph
from unified_src.services.pdf_exporter import PDFExporter
from unified_src.utils.helpers import (
    initialize_session_state, get_module_state, update_module_state,
    display_error, display_success
)


def render_blog_generator_ui():
    """Render the blog generator interface."""
    st.header("✍️ Blog Generator")
    st.write("Generate structured, SEO-optimized blog posts automatically.")
    
    initialize_session_state()
    
    # Sidebar for settings
    with st.sidebar:
        st.subheader("Blog Settings")
        tone_options = ["professional", "casual", "formal", "conversational"]
        selected_tone = st.selectbox("Tone", tone_options, index=0)
    
    # Get or initialize blog generator state
    blog_state = get_module_state("blog_generator")
    
    # Input form
    st.subheader("Blog Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input("Blog Topic", placeholder="e.g., Artificial Intelligence in Healthcare")
        keywords_input = st.text_area("Keywords (comma-separated)", placeholder="e.g., AI, healthcare, diagnosis")
    
    with col2:
        target_audience = st.text_input("Target Audience", placeholder="e.g., Healthcare professionals")
        title = st.text_input("Blog Title (Optional)", placeholder="Leave empty to auto-generate")
    
    if st.button("🚀 Generate Blog", use_container_width=True):
        if not topic:
            display_error("Please enter a blog topic!")
            return
        
        # Parse keywords
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        # Initialize blog state
        state = {
            "topic": topic,
            "keywords": keywords,
            "tone": selected_tone,
            "language": "English",
            "blog": None
        }
        
        try:
            llm = get_llm()
            graph = create_blog_generator_graph(llm)
            
            with st.spinner("🔄 Generating blog post... This may take a moment."):
                result = graph.invoke(state)
            
            blog_content = result.get("blog")
            
            if blog_content:
                # Save to session state
                blog_state["generated_blog"] = blog_content
                update_module_state("blog_generator", blog_state)
                
                display_success("Blog post generated successfully!")
                
                # Display the blog
                st.divider()
                st.subheader("📄 Generated Blog Post")
                
                # Display title
                st.markdown(f"# {blog_content.seo_metadata.title}")
                
                # Display metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"📊 Tone: {blog_content.seo_metadata.tone}")
                with col2:
                    st.caption(f"🎯 Keywords: {', '.join(blog_content.seo_metadata.keywords[:3])}")
                with col3:
                    st.caption(f"📝 Topic: {topic}")
                
                st.divider()
                
                # Display introduction
                st.markdown("## Introduction")
                st.write(blog_content.introduction)
                
                # Display sections
                if blog_content.sections:
                    st.markdown("## Main Content")
                    for section in blog_content.sections:
                        st.markdown(f"### {section.get('heading', 'Section')}")
                        st.write(section.get('content', ''))
                
                # Display conclusion
                st.markdown("## Conclusion")
                st.write(blog_content.conclusion)
                
                # Download options
                st.divider()
                st.subheader("💾 Download")
                
                # Generate markdown content
                markdown_content = f"""# {blog_content.seo_metadata.title}

**Tone:** {blog_content.seo_metadata.tone}  
**Keywords:** {', '.join(blog_content.seo_metadata.keywords)}  
**Topic:** {topic}

## Introduction

{blog_content.introduction}

## Main Content
"""
                
                for section in blog_content.sections:
                    markdown_content += f"\n### {section.get('heading', 'Section')}\n\n{section.get('content', '')}\n\n"
                
                markdown_content += f"\n## Conclusion\n\n{blog_content.conclusion}"
                
                # Download button
                st.download_button(
                    label="📥 Download as PDF",
                    data=PDFExporter.export_report(
                        blog_content.seo_metadata.title,
                        markdown_content
                    ),
                    file_name=f"{blog_content.seo_metadata.title.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
        
        except Exception as e:
            display_error(f"Failed to generate blog: {str(e)}")
    
    # Display previously generated blog if available
    elif "generated_blog" in blog_state:
        st.divider()
        st.subheader("📄 Previously Generated Blog")
        
        blog_content = blog_state["generated_blog"]
        
        # Display title
        st.markdown(f"# {blog_content.seo_metadata.title}")
        
        # Display metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📊 Tone: {blog_content.seo_metadata.tone}")
        with col2:
            st.caption(f"🎯 Keywords: {', '.join(blog_content.seo_metadata.keywords[:3])}")
        with col3:
            st.caption(f"📝 Topic: {topic if topic else 'N/A'}")
        
        st.divider()
        
        # Display introduction
        st.markdown("## Introduction")
        st.write(blog_content.introduction)
        
        # Display sections
        if blog_content.sections:
            st.markdown("## Main Content")
            for section in blog_content.sections:
                st.markdown(f"### {section.get('heading', 'Section')}")
                st.write(section.get('content', ''))
        
        # Display conclusion
        st.markdown("## Conclusion")
        st.write(blog_content.conclusion)

        # Download options
        st.divider()
        st.subheader("💾 Download")
        
        # Generate content for PDF
        pdf_content = f"# {blog_content.seo_metadata.title}\n\n"
        pdf_content += f"**Tone:** {blog_content.seo_metadata.tone}\n"
        pdf_content += f"**Keywords:** {', '.join(blog_content.seo_metadata.keywords)}\n\n"
        pdf_content += "## Introduction\n\n"
        pdf_content += f"{blog_content.introduction}\n\n"
        pdf_content += "## Main Content\n\n"
        for section in blog_content.sections:
             pdf_content += f"### {section.get('heading', 'Section')}\n\n{section.get('content', '')}\n\n"
        pdf_content += f"## Conclusion\n\n{blog_content.conclusion}"

        st.download_button(
            label="📥 Download as PDF",
            data=PDFExporter.export_report(
                blog_content.seo_metadata.title,
                pdf_content
            ),
            file_name=f"{blog_content.seo_metadata.title.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
