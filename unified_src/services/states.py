"""
Unified state definitions for all modules.
"""
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========================
# Base Chat State
# ========================
class ChatState(TypedDict):
    """Unified state for chat-based modules."""
    messages: Annotated[List[Any], add_messages]
    user_id: Optional[str]
    session_id: Optional[str]
    extracted_context: Optional[str]
    uploaded_files: Optional[List[str]]


# ========================
# Blog Generation State
# ========================
class BlogMetadata(BaseModel):
    """Blog metadata."""
    title: str = Field(description="Title of the blog post")
    keywords: List[str] = Field(default=[], description="SEO keywords")
    tone: str = Field(default="professional", description="Writing tone")
    target_audience: str = Field(default="general", description="Target audience")


class BlogContent(BaseModel):
    """Blog content structure."""
    introduction: str = Field(description="Introduction section")
    sections: List[Dict[str, str]] = Field(default=[], description="Sections with headings and content")
    conclusion: str = Field(description="Conclusion section")
    seo_metadata: Optional[BlogMetadata] = None


class BlogState(TypedDict):
    """State for blog generation module."""
    topic: str
    blog: Optional[BlogContent]
    keywords: List[str]
    tone: str
    language: str


# ========================
# News Generation State
# ========================
class NewsArticle(BaseModel):
    """News article structure."""
    title: str = Field(description="Article title")
    summary: str = Field(description="Article summary")
    content: str = Field(description="Full article content")
    source: Optional[str] = Field(default=None, description="Source of news")
    timestamp: Optional[str] = Field(default=None, description="Publication timestamp")


class NewsState(TypedDict):
    """State for news generation module."""
    category: str
    timeframe: str  # daily, weekly, monthly
    tone: str  # formal, casual
    articles: List[NewsArticle]
    summary: Optional[str]


# ========================
# Web Search State
# ========================
class SearchResult(BaseModel):
    """Search result from web search."""
    title: str = Field(description="Page title")
    url: str = Field(description="Page URL")
    snippet: str = Field(description="Page snippet")
    source: str = Field(description="Source domain")


class WebChatState(TypedDict):
    """State for web-enabled chat module."""
    messages: Annotated[List[Any], add_messages]
    search_results: List[SearchResult]
    user_id: Optional[str]
    session_id: Optional[str]
    use_web_search: bool
    extracted_context: Optional[str]
    uploaded_files: Optional[List[str]]


# ========================
# Report Generation State
# ========================
class ReportSection(BaseModel):
    """Report section structure."""
    title: str = Field(description="Section title")
    content: str = Field(description="Section content")
    subsections: List[Dict[str, str]] = Field(default=[], description="Subsections with titles and content")


class Citation(BaseModel):
    """Citation structure."""
    index: int = Field(description="Citation number")
    title: str = Field(description="Source title")
    url: str = Field(description="Source URL")
    excerpt: str = Field(description="Relevant excerpt")
    accessed_date: Optional[str] = Field(default=None, description="Date accessed")


class ReportContent(BaseModel):
    """Report content structure."""
    title: str = Field(description="Report title")
    executive_summary: str = Field(description="Executive summary")
    introduction: str = Field(description="Introduction section")
    sections: List[ReportSection] = Field(default=[], description="Main report sections")
    conclusion: str = Field(description="Conclusion section")
    references: List[Citation] = Field(default=[], description="List of citations")
    metadata: Dict[str, str] = Field(default={}, description="Report metadata")


class ReportState(TypedDict):
    """State for report generation module."""
    title: str
    topic: str
    query: str
    target_audience: str
    tone: str  # Technical, Business, Academic, Casual
    length: str  # Short, Medium, Long
    template: str  # technical_report, business_report, research_report
    urls: List[str]
    enable_citations: bool
    enable_web_search: bool
    loaded_content: Optional[Dict[str, Any]]
    search_results: Optional[List[Dict[str, Any]]]
    report: Optional[ReportContent]
    error: Optional[str]


# ========================
# Research Q&A State
# ========================
class ResearchQAState(TypedDict):
    """State for research-driven Q&A module."""
    question: str
    urls: List[str]
    chunks: Optional[List[Dict[str, Any]]]
    retrieved_chunks: Optional[List[Dict[str, Any]]]
    answer: Optional[str]
    citations: List[Citation]
    sources: Optional[List[SearchResult]]
    error: Optional[str]


# ========================
# Settings State
# ========================
class SettingsState(TypedDict):
    """State for application settings."""
    theme: str
    model_temperature: float
    max_tokens: int
    enable_memory: bool
    custom_system_prompt: Optional[str]
