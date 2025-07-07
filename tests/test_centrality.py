import networkx as nx
import pytest
from src.recommender.features.centrality import compute_betweenness


def test_compute_betweenness_path():
    g = nx.Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    result = compute_betweenness(g)
    assert result[2] == pytest.approx(1.0)
    assert result[1] == pytest.approx(0.0)
    assert result[3] == pytest.approx(0.0)
