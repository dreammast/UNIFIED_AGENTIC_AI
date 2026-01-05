"""
Research Q&A Agent - Answer questions based on provided URLs.
Performs retrieval and grounded answer generation.
"""
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any, List
import logging
from unified_src.services.llm_service import get_llm
from unified_src.services.states import ResearchQAState, Citation
from unified_src.services.web_loader import WebLoader
from unified_src.services.citation_engine import CitationEngine

logger = logging.getLogger(__name__)


class ResearchQANode:
    """Node for research Q&A processing."""
    
    def __init__(self, llm):
        self.llm = llm
        self.web_loader = WebLoader()
        self.citation_engine = CitationEngine()
    
    def load_urls(self, state: ResearchQAState) -> Dict[str, Any]:
        """Load content from provided URLs."""
        urls = state.get("urls", [])
        
        if not urls:
            state["error"] = "No URLs provided"
            return state
        
        logger.info(f"Loading {len(urls)} URLs for Q&A")
        
        try:
            result = self.web_loader.load_urls(urls)
            state["chunks"] = result.get("chunks", [])
            return state
        except Exception as e:
            logger.error(f"Error loading URLs: {str(e)}")
            state["error"] = f"Failed to load URLs: {str(e)}"
            return state
    
    def chunk_content(self, state: ResearchQAState) -> Dict[str, Any]:
        """Content already chunked in load_urls, but this node validates chunks."""
        if not state.get("chunks"):
            state["error"] = "No content chunks available"
            return state
        
        logger.info(f"Processed {len(state['chunks'])} content chunks")
        return state
    
    def retrieve_relevant_info(self, state: ResearchQAState) -> Dict[str, Any]:
        """Retrieve relevant information for the question."""
        question = state.get("question", "")
        chunks = state.get("chunks", [])
        
        if not question or not chunks:
            state["error"] = "Question or chunks missing"
            return state
        
        logger.info(f"Retrieving information for question: {question}")
        
        try:
            # Simple relevance scoring based on keyword matching
            # In production, use embeddings and semantic search
            question_words = set(question.lower().split())
            
            scored_chunks = []
            for chunk in chunks:
                content = chunk.get("content", "").lower()
                
                # Count matching words
                matches = sum(1 for word in question_words if word in content)
                score = matches / len(question_words) if question_words else 0
                
                scored_chunks.append({
                    "chunk": chunk,
                    "score": score
                })
            
            # Sort by relevance and take top 5
            top_chunks = sorted(scored_chunks, key=lambda x: x["score"], reverse=True)[:5]
            state["retrieved_chunks"] = [item["chunk"] for item in top_chunks]
            
            # Add citations from retrieved chunks
            if top_chunks:
                for item in top_chunks:
                    chunk = item["chunk"]
                    metadata = chunk.get("metadata", {})
                    
                    self.citation_engine.add_citation(
                        title=metadata.get("title", "Unknown"),
                        url=metadata.get("url", ""),
                        excerpt=chunk.get("content", "")[:200]
                    )
            
            return state
        except Exception as e:
            logger.error(f"Error retrieving information: {str(e)}")
            state["error"] = f"Retrieval failed: {str(e)}"
            return state
    
    def answer_question(self, state: ResearchQAState) -> Dict[str, Any]:
        """Generate answer based on retrieved information."""
        question = state.get("question", "")
        chunks = state.get("retrieved_chunks", [])
        
        if not chunks:
            state["error"] = "No relevant information found"
            return state
        
        logger.info("Generating answer")
        
        try:
            # Build context from relevant chunks
            context_parts = []
            for chunk in chunks:
                content = chunk.get("content", "")
                metadata = chunk.get("metadata", {})
                source = metadata.get("title", "Unknown Source")
                context_parts.append(f"[From {source}]:\n{content}")
            
            context = "\n\n".join(context_parts)
            
            prompt = f"""Based on the following context, answer the user's question. 
Be specific and cite the sources where you found the information.

Context:
{context}

Question: {question}

Provide a detailed, well-sourced answer. Reference the sources mentioned."""
            
            response = self.llm.invoke(prompt)
            state["answer"] = response.content
            
            return state
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            state["error"] = f"Failed to generate answer: {str(e)}"
            return state
    
    def generate_citations(self, state: ResearchQAState) -> Dict[str, Any]:
        """Generate citations for the answer."""
        logger.info("Generating citations")
        
        try:
            citations = self.citation_engine.get_citations_list()
            state["citations"] = [
                Citation(
                    index=c["index"],
                    title=c["title"],
                    url=c["url"],
                    excerpt=c["excerpt"],
                    accessed_date=c.get("accessed_date")
                )
                for c in citations
            ]
            
            return state
        except Exception as e:
            logger.error(f"Error generating citations: {str(e)}")
            return state


class ResearchQAGraph:
    """LangGraph-based research Q&A system."""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder = StateGraph(ResearchQAState)
        self.qa_node = ResearchQANode(llm)
    
    def build(self):
        """Build the graph."""
        self.graph_builder.add_node("load_urls", self.qa_node.load_urls)
        self.graph_builder.add_node("chunk_content", self.qa_node.chunk_content)
        self.graph_builder.add_node("retrieve_relevant_info", self.qa_node.retrieve_relevant_info)
        self.graph_builder.add_node("answer_question", self.qa_node.answer_question)
        self.graph_builder.add_node("generate_citations", self.qa_node.generate_citations)
        
        self.graph_builder.add_edge(START, "load_urls")
        self.graph_builder.add_edge("load_urls", "chunk_content")
        self.graph_builder.add_edge("chunk_content", "retrieve_relevant_info")
        self.graph_builder.add_edge("retrieve_relevant_info", "answer_question")
        self.graph_builder.add_edge("answer_question", "generate_citations")
        self.graph_builder.add_edge("generate_citations", END)
        
        return self.graph_builder.compile()


def create_research_qa_graph(llm):
    """Create and return compiled research Q&A graph."""
    graph_builder = ResearchQAGraph(llm)
    return graph_builder.build()
