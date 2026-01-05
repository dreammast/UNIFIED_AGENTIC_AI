"""
Report Generator Agent - Generates structured reports with citations.
"""

import logging
from typing import Dict, Any, List

from langgraph.graph import StateGraph, START, END
from langchain_community.tools import TavilySearchResults

from unified_src.services.states import (
    ReportState,
    ReportContent,
    ReportSection,
    Citation,
)
from unified_src.services.web_loader import WebLoader
from unified_src.services.citation_engine import CitationEngine

logger = logging.getLogger(__name__)


# =========================
# Report Generator Node
# =========================

class ReportGeneratorNode:
    """LangGraph node responsible for report generation."""

    def __init__(self, llm):
        self.llm = llm
        self.web_loader = WebLoader()
        self.citation_engine = CitationEngine()

    # -------- URL LOADING --------
    def load_urls(self, state: ReportState) -> Dict[str, Any]:
        urls = state.get("urls") or []

        if not urls:
            state["loaded_content"] = {"loaded_content": {}}
            return state

        logger.info("Loading URLs for report")

        try:
            loaded = self.web_loader.load_urls(urls)

            # 🔒 HARD GUARANTEE: always a dict
            if isinstance(loaded, dict):
                state["loaded_content"] = loaded
            else:
                state["loaded_content"] = {"loaded_content": {}}

        except Exception as e:
            logger.exception("URL loading failed")
            state["loaded_content"] = {"loaded_content": {}}
            state["error"] = f"Failed to load URLs: {e}"

        return state

    # -------- WEB SEARCH --------
    def web_search(self, state: ReportState) -> Dict[str, Any]:
        if not state.get("enable_web_search"):
            return state

        query = state.get("query")
        if not query:
            return state

        try:
            search = TavilySearchResults(max_results=5)
            state["search_results"] = search.invoke(query)
        except Exception as e:
            logger.warning(f"Web search skipped: {e}")

        return state

    # -------- SOURCE SUMMARIZATION --------
    def summarize_sources(self, state: ReportState) -> Dict[str, Any]:
        loaded = state.get("loaded_content") or {}
        sources = loaded.get("loaded_content") or {}

        if not sources:
            return state

        for url, content in sources.items():
            if not isinstance(content, dict):
                continue

            self.citation_engine.add_citation(
                title=content.get("title", "Unknown"),
                url=url,
                excerpt=content.get("text", "")[:200],
            )

        return state

    # -------- REPORT GENERATION --------
    def generate_report(self, state: ReportState) -> Dict[str, Any]:
        title = state.get("title", "Untitled Report")
        topic = state.get("topic", "")
        query = state.get("query", "")
        tone = state.get("tone", "Technical")
        template = state.get("template", "technical_report")

        context_blocks: List[str] = []

        loaded = state.get("loaded_content") or {}
        sources = loaded.get("loaded_content") or {}

        for content in sources.values():
            if not isinstance(content, dict):
                continue

            context_blocks.append(
                f"{content.get('title', '')}\n{content.get('text', '')[:500]}"
            )

        context = "\n\n".join(context_blocks)

        prompt = f"""
You are an expert report writer.

Title: {title}
Topic: {topic}
Objective: {query}
Tone: {tone}
Template: {template}

Context:
{context if context else "No external sources provided."}

Write a structured report with:
- Executive Summary
- Introduction
- 3–4 Main Sections
- Conclusion

Use clear headings and professional language.
"""

        try:
            response = self.llm.invoke(prompt)
            report_text = response.content or ""

            parsed = self._parse_sections(report_text)

            report = ReportContent(
                title=title,
                executive_summary=parsed["executive_summary"],
                introduction=parsed["introduction"],
                sections=parsed["sections"],
                conclusion=parsed["conclusion"],
                references=self.citation_engine.citations,
                metadata={
                    "template": template,
                    "tone": tone,
                    "topic": topic,
                    "word_count": len(report_text.split()),  # ✅ int-safe
                },
            )

            state["report"] = report

        except Exception as e:
            logger.exception("Report generation failed")
            state["error"] = f"Report generation failed: {e}"

        return state

    # -------- SECTION PARSER --------
    def _parse_sections(self, text: str) -> Dict[str, Any]:
        sections = {
            "executive_summary": "",
            "introduction": "",
            "sections": [],
            "conclusion": "",
        }

        current = None
        buffer: List[str] = []
        section_title = None

        for line in text.splitlines():
            low = line.lower().strip()

            if "executive summary" in low:
                current, buffer = "executive_summary", []
            elif low.startswith("introduction"):
                current, buffer = "introduction", []
            elif low.startswith("conclusion"):
                if current == "sections" and section_title:
                    sections["sections"].append(
                        ReportSection(title=section_title, content="\n".join(buffer))
                    )
                current, buffer = "conclusion", []
            elif line.startswith("#"):
                if current == "sections" and section_title:
                    sections["sections"].append(
                        ReportSection(title=section_title, content="\n".join(buffer))
                    )
                current = "sections"
                section_title = line.strip("# ").strip()
                buffer = []
            else:
                buffer.append(line)

        if current == "sections" and section_title:
            sections["sections"].append(
                ReportSection(title=section_title, content="\n".join(buffer))
            )
        elif current:
            sections[current] = "\n".join(buffer)

        return sections


# =========================
# Graph Builder
# =========================

class ReportGeneratorGraph:
    def __init__(self, llm):
        self.graph = StateGraph(ReportState)
        self.node = ReportGeneratorNode(llm)

    def build(self):
        self.graph.add_node("load_urls", self.node.load_urls)
        self.graph.add_node("web_search", self.node.web_search)
        self.graph.add_node("summarize_sources", self.node.summarize_sources)
        self.graph.add_node("generate_report", self.node.generate_report)

        self.graph.add_edge(START, "load_urls")
        self.graph.add_edge("load_urls", "web_search")
        self.graph.add_edge("web_search", "summarize_sources")
        self.graph.add_edge("summarize_sources", "generate_report")
        self.graph.add_edge("generate_report", END)

        return self.graph.compile()


def create_report_generator_graph(llm):
    """Factory function"""
    return ReportGeneratorGraph(llm).build()
