import networkx as nx
from typing import Dict, Any


def compute_avg_shortest_path_length(
    graph: nx.Graph,
) -> Dict[Any, float]:
    """Compute the mean shortest path length for every node.

    For each node, all reachable nodes are considered when averaging the
    shortest path lengths.

    Parameters
    ----------
    graph : nx.Graph
        Undirected graph.

    Returns
    -------
    Dict[Any, float]
        Mapping ``{node: mean_distance, ...}``.
    """
    results: Dict[Any, float] = {}
    for node in graph.nodes:
        lengths = nx.single_source_shortest_path_length(graph, node)
        # discard distance to the node itself
        distances = [d for target, d in lengths.items() if target != node]
        if distances:
            results[node] = sum(distances) / len(distances)
        else:
            results[node] = 0.0
    return results
