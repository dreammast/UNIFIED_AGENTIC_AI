"""
Markdown Exporter Service - Converts report content to markdown format.
Handles formatting and file export functionality.
"""
from typing import Dict, Any, Optional
from unified_src.services.states import ReportContent, Citation
import logging

logger = logging.getLogger(__name__)


class MarkdownExporter:
    """Service for exporting content to markdown format."""
    
    @staticmethod
    def export_report(report: ReportContent) -> str:
        """
        Export report content to markdown format.
        
        Args:
            report: ReportContent object
            
        Returns:
            Markdown formatted report
        """
        md = ""
        
        # Title
        md += f"# {report.title}\n\n"
        
        # Metadata
        if report.metadata:
            md += "---\n"
            for key, value in report.metadata.items():
                md += f"{key}: {value}\n"
            md += "---\n\n"
        
        # Executive Summary
        if report.executive_summary:
            md += "## Executive Summary\n\n"
            md += f"{report.executive_summary}\n\n"
        
        # Introduction
        if report.introduction:
            md += "## Introduction\n\n"
            md += f"{report.introduction}\n\n"
        
        # Main Sections
        if report.sections:
            for section in report.sections:
                md += f"## {section.title}\n\n"
                md += f"{section.content}\n\n"
                
                # Subsections
                if section.subsections:
                    for subsection in section.subsections:
                        title = subsection.get("title", "Untitled")
                        content = subsection.get("content", "")
                        md += f"### {title}\n\n"
                        md += f"{content}\n\n"
        
        # Conclusion
        if report.conclusion:
            md += "## Conclusion\n\n"
            md += f"{report.conclusion}\n\n"
        
        # References
        if report.references:
            md += "## References\n\n"
            for citation in report.references:
                md += f"[{citation.index}] **{citation.title}**\n"
                md += f"   - URL: {citation.url}\n"
                if citation.accessed_date:
                    md += f"   - Accessed: {citation.accessed_date}\n"
                md += "\n"
        
        return md
    
    @staticmethod
    def export_qa_response(
        question: str,
        answer: str,
        citations: Optional[list] = None,
        sources: Optional[list] = None
    ) -> str:
        """
        Export Q&A response to markdown format.
        
        Args:
            question: User question
            answer: Generated answer
            citations: List of citations
            sources: List of sources
            
        Returns:
            Markdown formatted response
        """
        md = ""
        
        # Question
        md += f"# Q&A Response\n\n"
        md += f"## Question\n\n{question}\n\n"
        
        # Answer
        md += f"## Answer\n\n{answer}\n\n"
        
        # Sources
        if citations:
            md += "## Sources\n\n"
            for citation in citations:
                md += f"[{citation.get('index', '')}] **{citation.get('title', 'Unknown')}**\n"
                md += f"   - URL: {citation.get('url', 'N/A')}\n"
                if citation.get('accessed_date'):
                    md += f"   - Accessed: {citation.get('accessed_date')}\n"
                md += "\n"
        
        return md
    
    @staticmethod
    def create_report_with_citations(
        title: str,
        content: str,
        citations: list,
        template: str = "standard"
    ) -> str:
        """
        Create a markdown report with citations.
        
        Args:
            title: Report title
            content: Main content
            citations: List of citations
            template: Template style
            
        Returns:
            Formatted markdown report
        """
        md = f"# {title}\n\n"
        
        if template != "standard":
            md += f"*Template: {template}*\n\n"
        
        md += content
        
        if citations:
            md += "\n\n## References\n\n"
            for i, citation in enumerate(citations, 1):
                md += f"[{i}] {citation.get('title', 'Unknown')}\n"
                md += f"    {citation.get('url', 'N/A')}\n"
                if citation.get('accessed_date'):
                    md += f"    Accessed: {citation.get('accessed_date')}\n"
                md += "\n"
        
        return md
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename for safe file export.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        import re
        sanitized = re.sub(invalid_chars, '', filename)
        
        # Limit length
        sanitized = sanitized[:200]
        
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        
        return sanitized
    
    @staticmethod
    def get_markdown_bytes(markdown: str) -> bytes:
        """
        Convert markdown string to bytes for download.
        
        Args:
            markdown: Markdown content
            
        Returns:
            Bytes representation
        """
        return markdown.encode('utf-8')


def export_report(report: ReportContent) -> str:
    """
    Convenience function to export report.
    
    Args:
        report: ReportContent object
        
    Returns:
        Markdown formatted report
    """
    exporter = MarkdownExporter()
    return exporter.export_report(report)
