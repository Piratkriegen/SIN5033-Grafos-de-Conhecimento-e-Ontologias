import networkx as nx
from typing import Dict, Any


def compute_betweenness(graph: nx.Graph) -> Dict[Any, float]:
    """Compute betweenness centrality for all nodes."""

    return nx.betweenness_centrality(graph)
