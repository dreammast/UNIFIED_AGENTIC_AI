"""
Report Graph - LangGraph orchestration for report generation.
"""
from unified_src.agents.report_generator import create_report_generator_graph


def create_report_graph(llm):
    """
    Create and compile the report generation graph.
    
    Args:
        llm: Language model instance
        
    Returns:
        Compiled LangGraph workflow
    """
    return create_report_generator_graph(llm)
