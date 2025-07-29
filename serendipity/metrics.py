# arquivo: serendipity/metrics.py
"""Novelty metrics based on complex networks."""

from typing import Any, Dict

import networkx as nx


def compute_clustering_coefficient(graph: nx.Graph) -> Dict[Any, float]:
    """Return the clustering coefficient of each node."""
    return nx.clustering(graph)


def compute_pagerank(graph: nx.Graph, **kwargs: Any) -> Dict[Any, float]:
    """Return the PageRank of each node."""
    return nx.pagerank(graph, **kwargs)


def compute_hhi(
    graph: nx.Graph,
    communities: Dict[Any, int],
) -> Dict[Any, float]:
    """Compute the Herfindahl-Hirschman index (HHI) of each node.

    Parameters
    ----------
    graph : nx.Graph
        Graph to analyze.
    communities : Dict[Any, int]
        Mapping ``node → community_id``.

    Returns
    -------
    Dict[Any, float]
        ``{node: hhi}`` for all nodes in the graph.
    """
    hhi: Dict[Any, float] = {}
    for node in graph:
        neigh = list(graph.neighbors(node))
        total = len(neigh)
        if total == 0:
            hhi[node] = 0.0
            continue
        counts: Dict[int, int] = {}
        for v in neigh:
            cid = communities.get(v, -1)
            counts[cid] = counts.get(cid, 0) + 1
        hhi_val = sum((cnt / total) ** 2 for cnt in counts.values())
        hhi[node] = hhi_val
    return hhi
