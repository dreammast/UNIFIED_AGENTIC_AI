"""
AI News Generator Agent - Unified implementation.
"""
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any, List
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.services.states import NewsState, NewsArticle
from datetime import datetime


class NewsGeneratorNode:
    """Node for news generation."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def fetch_news(self, state: NewsState) -> Dict[str, Any]:
        """Generate news articles for the given category."""
        category = state.get("category", "technology")
        timeframe = state.get("timeframe", "daily")
        tone = state.get("tone", "formal")
        
        prompt = f"""Generate 3 high-quality news articles about {category} for {timeframe} briefing.
        
Requirements:
- Tone: {tone}
- Each article should be realistic and informative
- Include relevant details and context
- Format each article as:
---ARTICLE_START---
Title: [Article Title]
Summary: [2-3 sentence summary]
Content: [Full article content with at least 5 paragraphs]
---ARTICLE_END---

Generate exactly 3 articles with detailed, original content."""
        
        response = self.llm.invoke(prompt)
        content = response.content
        
        # Parse articles
        articles = []
        article_blocks = content.split("---ARTICLE_START---")[1:]
        
        for block in article_blocks:
            if "---ARTICLE_END---" in block:
                block = block.split("---ARTICLE_END---")[0]
            
            lines = block.strip().split("\n")
            title = ""
            summary = ""
            article_content = ""
            
            current_section = None
            for line in lines:
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                elif line.startswith("Summary:"):
                    summary = line.replace("Summary:", "").strip()
                    current_section = "summary"
                elif line.startswith("Content:"):
                    article_content = line.replace("Content:", "").strip()
                    current_section = "content"
                elif current_section == "summary" and line.strip():
                    summary += " " + line.strip()
                elif current_section == "content" and line.strip():
                    article_content += "\n" + line.strip()
            
            if title and summary and article_content:
                article = NewsArticle(
                    title=title,
                    summary=summary,
                    content=article_content,
                    source="AI News Generator",
                    timestamp=datetime.now().isoformat()
                )
                articles.append(article)
        
        state["articles"] = articles
        return state
    
    def summarize_news(self, state: NewsState) -> Dict[str, Any]:
        """Generate a summary of the news."""
        articles = state.get("articles", [])
        
        if not articles:
            state["summary"] = "No articles generated."
            return state
        
        # Create article summaries for context
        articles_text = "\n\n".join([
            f"Article: {article.title}\nSummary: {article.summary}"
            for article in articles
        ])
        
        prompt = f"""Create a comprehensive daily/weekly briefing summary based on these articles:
        
{articles_text}

Tone: {state.get("tone", "formal")}

Provide a 1-2 paragraph executive summary that highlights the key themes and important points."""
        
        response = self.llm.invoke(prompt)
        state["summary"] = response.content
        return state
    
    def save_result(self, state: NewsState) -> Dict[str, Any]:
        """Save results (in real implementation, would save to database)."""
        # In this unified version, we just ensure the state is complete
        return state


class NewsGeneratorGraph:
    """LangGraph-based news generator."""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder = StateGraph(NewsState)
        self.news_node = NewsGeneratorNode(llm)
    
    def build(self):
        """Build the graph."""
        self.graph_builder.add_node("fetch_news", self.news_node.fetch_news)
        self.graph_builder.add_node("summarize_news", self.news_node.summarize_news)
        self.graph_builder.add_node("save_result", self.news_node.save_result)
        
        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news", "summarize_news")
        self.graph_builder.add_edge("summarize_news", "save_result")
        self.graph_builder.add_edge("save_result", END)
        
        return self.graph_builder.compile()


def create_news_generator_graph(llm):
    """Create and return compiled news generator graph."""
    graph_builder = NewsGeneratorGraph(llm)
    return graph_builder.build()
