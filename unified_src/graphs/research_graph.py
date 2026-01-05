"""
Research Q&A Graph - LangGraph orchestration for research-driven Q&A.
"""
from unified_src.agents.research_agent import create_research_qa_graph


def create_research_qa_graph_def(llm):
    """
    Create and compile the research Q&A graph.
    
    Args:
        llm: Language model instance
        
    Returns:
        Compiled LangGraph workflow
    """
    return create_research_qa_graph(llm)
