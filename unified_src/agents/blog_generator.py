"""
Blog Generator Agent - Unified implementation.
"""
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any
import streamlit as st
from unified_src.services.llm_service import get_llm
from unified_src.services.states import BlogState, BlogContent, BlogMetadata
from pydantic import BaseModel, Field


class BlogGeneratorNode:
    """Node for blog generation."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate_title(self, state: BlogState) -> Dict[str, Any]:
        """Generate blog title based on topic."""
        if not state.get("topic"):
            return state
        
        topic = state["topic"]
        keywords = state.get("keywords", [])
        tone = state.get("tone", "professional")
        
        prompt = f"""You are an expert blog content writer. Generate a creative and SEO-friendly blog title for the following:
        
Topic: {topic}
Keywords: {', '.join(keywords) if keywords else 'None'}
Tone: {tone}

Provide only the title, no additional text."""
        
        response = self.llm.invoke(prompt)
        title = response.content.strip()
        
        state["blog"] = BlogContent(
            introduction="",
            sections=[],
            conclusion="",
            seo_metadata=BlogMetadata(
                title=title,
                keywords=keywords,
                tone=tone
            )
        )
        return state
    
    def generate_introduction(self, state: BlogState) -> Dict[str, Any]:
        """Generate blog introduction."""
        topic = state["topic"]
        title = state["blog"].seo_metadata.title
        
        prompt = f"""Write a compelling introduction for a blog post with the following details:
        
Title: {title}
Topic: {topic}
Tone: {state.get("tone", "professional")}

The introduction should be engaging and set up the topic well. Write 2-3 paragraphs."""
        
        response = self.llm.invoke(prompt)
        state["blog"].introduction = response.content
        return state
    
    def generate_sections(self, state: BlogState) -> Dict[str, Any]:
        """Generate main content sections."""
        topic = state["topic"]
        title = state["blog"].seo_metadata.title
        tone = state.get("tone", "professional")
        
        prompt = f"""Create detailed sections for a blog post:
        
Title: {title}
Topic: {topic}
Tone: {tone}

Generate 3-4 main sections with headings and content. Format as:
---SECTION_START---
Heading: [Section Heading]
Content: [Section content]
---SECTION_END---

Provide detailed, informative content for each section."""
        
        response = self.llm.invoke(prompt)
        content = response.content
        
        # Parse sections
        sections = []
        section_blocks = content.split("---SECTION_START---")[1:]
        
        for block in section_blocks:
            if "---SECTION_END---" in block:
                block = block.split("---SECTION_END---")[0]
            
            lines = block.strip().split("\n")
            heading = ""
            section_content = ""
            
            for line in lines:
                if line.startswith("Heading:"):
                    heading = line.replace("Heading:", "").strip()
                elif line.startswith("Content:"):
                    section_content = line.replace("Content:", "").strip()
                else:
                    if section_content:
                        section_content += "\n" + line
            
            if heading and section_content:
                sections.append({"heading": heading, "content": section_content})
        
        state["blog"].sections = sections
        return state
    
    def generate_conclusion(self, state: BlogState) -> Dict[str, Any]:
        """Generate blog conclusion."""
        topic = state["topic"]
        title = state["blog"].seo_metadata.title
        
        prompt = f"""Write a compelling conclusion for a blog post:
        
Title: {title}
Topic: {topic}

Summarize key points and provide actionable takeaways. Write 2-3 paragraphs."""
        
        response = self.llm.invoke(prompt)
        state["blog"].conclusion = response.content
        return state


class BlogGeneratorGraph:
    """LangGraph-based blog generator."""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder = StateGraph(BlogState)
        self.blog_node = BlogGeneratorNode(llm)
    
    def build(self):
        """Build the graph."""
        self.graph_builder.add_node("generate_title", self.blog_node.generate_title)
        self.graph_builder.add_node("generate_introduction", self.blog_node.generate_introduction)
        self.graph_builder.add_node("generate_sections", self.blog_node.generate_sections)
        self.graph_builder.add_node("generate_conclusion", self.blog_node.generate_conclusion)
        
        self.graph_builder.add_edge(START, "generate_title")
        self.graph_builder.add_edge("generate_title", "generate_introduction")
        self.graph_builder.add_edge("generate_introduction", "generate_sections")
        self.graph_builder.add_edge("generate_sections", "generate_conclusion")
        self.graph_builder.add_edge("generate_conclusion", END)
        
        return self.graph_builder.compile()


def create_blog_generator_graph(llm):
    """Create and return compiled blog generator graph."""
    graph_builder = BlogGeneratorGraph(llm)
    return graph_builder.build()
