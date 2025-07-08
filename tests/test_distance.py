import pytest
import networkx as nx

from serendipity.distance import compute_avg_shortest_path_length


def test_compute_avg_shortest_path_length_path():
    # Grafo linha: 1–2–3
    G = nx.path_graph([1, 2, 3])
    dist = compute_avg_shortest_path_length(G)

    # Distâncias excluem o nó em si:
    # Para 1: distâncias são [1,2] → média = 1.5
    # Para 2: distâncias são [1,1] → média = 1.0
    # Para 3: distâncias são [2,1] → média = 1.5
    assert dist[1] == pytest.approx(1.5)
    assert dist[2] == pytest.approx(1.0)
    assert dist[3] == pytest.approx(1.5)
