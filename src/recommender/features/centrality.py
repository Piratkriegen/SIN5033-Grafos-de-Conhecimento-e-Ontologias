# arquivo: src/recommender/features/centrality.py
# Python 3

import networkx as nx
from typing import Dict, Any

def compute_betweenness(graph: nx.Graph) -> Dict[Any, float]:
    """
    Recebe um grafo NetworkX e retorna um dicionário
    mapeando cada nó ao seu valor de centralidade de betweenness.

    Parâmetros:
    ----------
    graph : nx.Graph
        Grafo não-direcionado cujas arestas valem 1.

    Retorna:
    -------
    Dict[Any, float]
        { nó: valor_de_betweenness, ... }
    """
