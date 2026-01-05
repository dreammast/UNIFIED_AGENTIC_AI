"""
Citation Engine Service - Manages citations and source tracking.
Generates citations from content chunks and search results.
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import logging
from unified_src.services.states import Citation

logger = logging.getLogger(__name__)


class CitationEngine:
    """Service for managing citations and source tracking."""
    
    def __init__(self):
        """Initialize CitationEngine."""
        self.citations: List[Citation] = []
        self.citation_map: Dict[str, int] = {}  # Maps source URL to citation index
        self.processed_sources: Set[str] = set()
    
    def add_citation(
        self,
        title: str,
        url: str,
        excerpt: str,
        accessed_date: Optional[str] = None
    ) -> int:
        """
        Add a citation or return existing citation index.
        
        Args:
            title: Source title
            url: Source URL
            excerpt: Relevant excerpt from source
            accessed_date: Date accessed (optional)
            
        Returns:
            Citation index (number)
        """
        # Return existing citation if URL already cited
        if url in self.citation_map:
            return self.citation_map[url]
        
        # Create new citation
        index = len(self.citations) + 1
        
        if accessed_date is None:
            accessed_date = datetime.now().strftime("%Y-%m-%d")
        
        citation = Citation(
            index=index,
            title=title,
            url=url,
            excerpt=excerpt,
            accessed_date=accessed_date
        )
        
        self.citations.append(citation)
        self.citation_map[url] = index
        self.processed_sources.add(url)
        
        logger.info(f"Added citation {index}: {title}")
        return index
    
    def add_citations_from_chunks(
        self,
        chunks: List[Dict[str, Any]],
        extract_func: Optional[callable] = None
    ) -> Dict[str, int]:
        """
        Add citations from content chunks.
        
        Args:
            chunks: List of content chunks
            extract_func: Optional function to extract excerpt from chunk
            
        Returns:
            Mapping of chunk index to citation index
        """
        chunk_citations = {}
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            url = metadata.get("url", "")
            title = metadata.get("title", "Unknown")
            content = chunk.get("content", "")
            
            if not url:
                continue
            
            # Extract excerpt
            excerpt = content[:200] + "..." if len(content) > 200 else content
            if extract_func:
                excerpt = extract_func(content)
            
            # Add citation
            citation_index = self.add_citation(
                title=title,
                url=url,
                excerpt=excerpt
            )
            
            chunk_citations[chunk.get("chunk_index", 0)] = citation_index
        
        return chunk_citations
    
    def add_citations_from_search_results(
        self,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Add citations from web search results.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            Mapping of result index to citation index
        """
        result_citations = {}
        
        for i, result in enumerate(search_results):
            url = result.get("url", "")
            title = result.get("title", "Unknown")
            snippet = result.get("snippet", "")
            
            if not url:
                continue
            
            citation_index = self.add_citation(
                title=title,
                url=url,
                excerpt=snippet
            )
            
            result_citations[i] = citation_index
        
        return result_citations
    
    def get_citations_list(self) -> List[Dict[str, Any]]:
        """
        Get formatted list of citations.
        
        Returns:
            List of citation dictionaries
        """
        return [
            {
                "index": c.index,
                "title": c.title,
                "url": c.url,
                "excerpt": c.excerpt,
                "accessed_date": c.accessed_date
            }
            for c in self.citations
        ]
    
    def get_references_markdown(self) -> str:
        """
        Generate markdown-formatted references section.
        
        Returns:
            Markdown formatted references
        """
        if not self.citations:
            return ""
        
        md = "## References\n\n"
        for citation in self.citations:
            md += f"[{citation.index}] **{citation.title}**\n"
            md += f"   URL: {citation.url}\n"
            if citation.accessed_date:
                md += f"   Accessed: {citation.accessed_date}\n"
            md += f"   Excerpt: {citation.excerpt}\n\n"
        
        return md
    
    def format_citation_inline(self, citation_index: int) -> str:
        """
        Format inline citation reference.
        
        Args:
            citation_index: Index of citation
            
        Returns:
            Formatted citation string (e.g., "[1]")
        """
        return f"[{citation_index}]"
    
    def reset(self):
        """Reset all citations."""
        self.citations = []
        self.citation_map = {}
        self.processed_sources = set()
        logger.info("Citations reset")
    
    def get_citation_context(self, citation_index: int) -> Optional[Dict[str, Any]]:
        """
        Get full context for a citation.
        
        Args:
            citation_index: Citation index
            
        Returns:
            Citation dictionary or None
        """
        if citation_index < 1 or citation_index > len(self.citations):
            return None
        
        citation = self.citations[citation_index - 1]
        return {
            "index": citation.index,
            "title": citation.title,
            "url": citation.url,
            "excerpt": citation.excerpt,
            "accessed_date": citation.accessed_date
        }


def create_citation_engine() -> CitationEngine:
    """
    Convenience function to create a citation engine.
    
    Returns:
        CitationEngine instance
    """
    return CitationEngine()
