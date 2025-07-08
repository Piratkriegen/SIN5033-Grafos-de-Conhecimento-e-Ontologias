import pytest
import networkx as nx

from serendipity.metrics import (
    compute_clustering_coefficient,
    compute_pagerank,
    compute_hhi,
)


@pytest.fixture
def simple_graph():
    return nx.path_graph(4)


def test_clustering(simple_graph):
    cc = compute_clustering_coefficient(simple_graph)
    assert all(val == 0 for val in cc.values())


def test_pagerank(simple_graph):
    pr = compute_pagerank(simple_graph, max_iter=100)
    assert pytest.approx(sum(pr.values()), rel=1e-6) == 1.0


def test_hhi(simple_graph):
    communities = {0: 0, 1: 0, 2: 1, 3: 1}
    hhi = compute_hhi(simple_graph, communities)
    assert pytest.approx(hhi[1], rel=1e-6) == 0.5
    assert pytest.approx(hhi[0], rel=1e-6) == 1.0
