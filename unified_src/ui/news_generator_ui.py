"""
UI component for AI News Generator.
"""
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.agents.news_generator import create_news_generator_graph
from unified_src.utils.helpers import (
    initialize_session_state, get_module_state, update_module_state,
    display_error, display_success
)


def render_news_generator_ui():
    """Render the news generator interface."""
    st.header("📰 AI News Generator")
    st.write("Generate AI-powered news summaries and briefings.")
    
    initialize_session_state()
    
    # Sidebar settings
    with st.sidebar:
        st.subheader("News Settings")
        
        categories = [
            "Technology",
            "Business",
            "Science",
            "Health",
            "Politics",
            "Entertainment",
            "Sports",
            "World News",
            "Finance",
            "AI & Machine Learning"
        ]
        
        selected_category = st.selectbox("News Category", categories)
        
        timeframes = ["daily", "weekly", "monthly"]
        selected_timeframe = st.selectbox("Timeframe", timeframes)
        
        tones = ["formal", "casual", "technical"]
        selected_tone = st.selectbox("Tone", tones)
    
    # Get or initialize news generator state
    news_state = get_module_state("news_generator")
    
    st.subheader("Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"📂 Category: {selected_category}")
    with col2:
        st.info(f"⏰ Timeframe: {selected_timeframe.capitalize()}")
    with col3:
        st.info(f"🎤 Tone: {selected_tone.capitalize()}")
    
    # Generate button
    if st.button("📡 Generate News Briefing", use_container_width=True):
        try:
            llm = get_llm()
            graph = create_news_generator_graph(llm)
            
            with st.spinner(f"Generating {selected_timeframe} news briefing for {selected_category}..."):
                state = {
                    "category": selected_category,
                    "timeframe": selected_timeframe,
                    "tone": selected_tone,
                    "articles": [],
                    "summary": None
                }
                
                result = graph.invoke(state)
            
            articles = result.get("articles", [])
            summary = result.get("summary", "")
            
            # Save to session state
            news_state["latest_briefing"] = {
                "category": selected_category,
                "timeframe": selected_timeframe,
                "tone": selected_tone,
                "articles": articles,
                "summary": summary
            }
            update_module_state("news_generator", news_state)
            
            display_success(f"Generated {len(articles)} articles successfully!")
            
            # Display executive summary
            if summary:
                st.divider()
                st.subheader("📋 Executive Summary")
                st.write(summary)
            
            # Display articles
            if articles:
                st.divider()
                st.subheader(f"📑 {selected_category} News Articles ({selected_timeframe.capitalize()})")
                
                for idx, article in enumerate(articles, 1):
                    with st.expander(f"Article {idx}: {article.title}", expanded=(idx == 1)):
                        st.markdown(f"**{article.title}**")
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.caption(f"🔗 Source: {article.source}")
                        with col2:
                            st.caption(f"⏱️ {article.timestamp[:10]}")
                        
                        st.markdown("**Summary:**")
                        st.write(article.summary)
                        
                        st.markdown("**Full Article:**")
                        st.write(article.content)
            
            # Download option
            st.divider()
            st.subheader("💾 Download Briefing")
            
            # Generate markdown
            markdown_content = f"# {selected_category} {selected_timeframe.capitalize()} Briefing\n\n"
            markdown_content += f"**Tone:** {selected_tone.capitalize()}\n\n"
            
            if summary:
                markdown_content += f"## Executive Summary\n\n{summary}\n\n"
            
            markdown_content += "## Articles\n\n"
            
            for idx, article in enumerate(articles, 1):
                markdown_content += f"### {idx}. {article.title}\n\n"
                markdown_content += f"**Source:** {article.source}  \n"
                markdown_content += f"**Summary:** {article.summary}\n\n"
                markdown_content += f"{article.content}\n\n---\n\n"
            
            st.download_button(
                label="📥 Download as Markdown",
                data=markdown_content,
                file_name=f"{selected_category}_{selected_timeframe}_briefing.md",
                mime="text/markdown"
            )
        
        except Exception as e:
            display_error(f"Failed to generate news briefing: {str(e)}")
    
    # Display previously generated briefing if available
    elif "latest_briefing" in news_state:
        briefing = news_state["latest_briefing"]
        
        st.divider()
        st.subheader("📋 Latest Briefing")
        
        if briefing.get("summary"):
            st.subheader("Executive Summary")
            st.write(briefing["summary"])
        
        if briefing.get("articles"):
            st.divider()
            st.subheader(f"Articles ({len(briefing['articles'])})")
            
            for idx, article in enumerate(briefing["articles"], 1):
                with st.expander(f"Article {idx}: {article.title}", expanded=(idx == 1)):
                    st.markdown(f"**{article.title}**")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"🔗 Source: {article.source}")
                    with col2:
                        st.caption(f"⏱️ {article.timestamp[:10]}")
                    
                    st.markdown("**Summary:**")
                    st.write(article.summary)
                    
                    st.markdown("**Full Article:**")
                    st.write(article.content)
