"""
Knowledge Graph Service
Handles all networkx graph construction and topic summarization.
"""
import networkx as nx
import json


def build_knowledge_graph(topic_list: list, corpus_id: str, files: list) -> tuple[str, str, str]:
    """
    Builds the complete knowledge graph with topics, files, and connections.
    
    Args:
        topic_list: List of topic strings from professor input
        corpus_id: The RAG corpus ID to query for topic summaries
        files: List of file objects from Canvas
        
    Returns:
        Tuple of (nodes_json, edges_json, data_json) as serialized JSON strings
    """
    # TODO: Implement KG construction
    # 1. Create networkx graph
    # 2. Add topic nodes
    # 3. Add file nodes
    # 4. For each topic:
    #    - Query RAG corpus
    #    - Generate summary with Gemini
    #    - Create edges to source files
    # 5. Serialize to JSON strings
    
    # Placeholder structure
    nodes = []
    edges = []
    data = {}
    
    return (
        json.dumps(nodes),
        json.dumps(edges),
        json.dumps(data)
    )
