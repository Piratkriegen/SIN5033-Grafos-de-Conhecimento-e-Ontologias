# arquivo: serendipity/metrics.py
# Python 3

"""Métricas de novidade baseadas em redes complexas."""

from typing import Any, Dict

import networkx as nx


def compute_clustering_coefficient(graph: nx.Graph) -> Dict[Any, float]:
    """Calcula o coeficiente de clustering de cada nó.

    Parameters
    ----------
    graph : nx.Graph
        Grafo não-direcionado.

    Returns
    -------
    Dict[Any, float]
        Mapeamento ``{nó: coeficiente}``.
    """
    return nx.clustering(graph)


def compute_pagerank(graph: nx.Graph, **kwargs: Any) -> Dict[Any, float]:
    """Retorna o PageRank de cada nó.

    Parameters
    ----------
    graph : nx.Graph
        Grafo de interesse.
    **kwargs : Any
        Parâmetros adicionais para ``networkx.pagerank``.

    Returns
    -------
    Dict[Any, float]
        PageRank por nó.
    """
    return nx.pagerank(graph, **kwargs)


def compute_hhi(graph: nx.Graph, communities: Dict[Any, int]) -> Dict[Any, float]:
    """Calcula o índice de Herfindahl-Hirschman (HHI) de cada nó.

    Para cada nó, considera a distribuição dos vizinhos entre as
    comunidades informadas.

    Parameters
    ----------
    graph : nx.Graph
        Grafo a ser analisado.
    communities : Dict[Any, int]
        Mapeamento ``nó → id_da_comunidade``.

    Returns
    -------
    Dict[Any, float]
        ``{nó: hhi}`` para todos os nós do grafo.
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
