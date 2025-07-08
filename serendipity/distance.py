# arquivo: src/recommender/features/distance.py
# Python 3

import networkx as nx
from typing import Dict, Any


def compute_avg_shortest_path_length(
    graph: nx.Graph,
) -> Dict[Any, float]:
    """Calcula a média das distâncias (caminhos mais curtos).

    Para cada nó em ``graph`` são consideradas todas as distâncias
    até os demais nós alcançáveis.

    Parâmetros
    ----------
    graph : nx.Graph
        Grafo não-direcionado.

    Retorna
    -------
    Dict[Any, float]
        Dicionário { nó: média_das_distâncias, … }.
    """
    results: Dict[Any, float] = {}
    for node in graph.nodes:
        lengths = nx.single_source_shortest_path_length(graph, node)
        # remove a distância para o próprio nó
        distances = [d for target, d in lengths.items() if target != node]
        if distances:
            results[node] = sum(distances) / len(distances)
        else:
            results[node] = 0.0
    return results
