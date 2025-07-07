# arquivo: src/recommender/features/centrality.py
# Python 3

import networkx as nx
from typing import Dict, Any

def compute_betweenness(graph: nx.Graph) -> Dict[Any, float]:
    """Calcula a centralidade de betweenness para todos os nós do grafo.

    Parameters
    ----------
    graph : nx.Graph
        Grafo não direcionado e não ponderado.

    Returns
    -------
    Dict[Any, float]
        Mapeamento ``{nó: valor}`` com a centralidade de betweenness.
    """

    # A função ``nx.betweenness_centrality`` já retorna exatamente o
    # dicionário necessário com os valores para cada nó. Assim, apenas
    # delegamos o cálculo para ela.
    return nx.betweenness_centrality(graph)
