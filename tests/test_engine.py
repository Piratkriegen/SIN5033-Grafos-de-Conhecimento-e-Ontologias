from pipeline.engine import rerank


def test_rerank_basic():
    candidates = [1, 2]
    relevance = {1: 0.9, 2: 0.1}
    novelty = {1: 0.2, 2: 0.8}
    # com alpha=0.5, beta=0.5: scores = {1:0.55, 2:0.45}
    assert rerank(
        candidates,
        relevance,
        novelty,
        alpha=0.5,
        beta=0.5,
    ) == [1, 2]


def test_rerank_extreme_weights():
    candidates = ["a", "b", "c"]
    relevance = {"a": 1.0, "b": 0.0, "c": 0.5}
    novelty = {"a": 0.0, "b": 1.0, "c": 0.5}
    # só novidade (alpha=1, beta=0): b > c > a
    assert rerank(candidates, relevance, novelty, alpha=1.0, beta=0.0) == [
        "b",
        "c",
        "a",
    ]
    # só relevância (alpha=0, beta=1): a > c > b
    assert rerank(candidates, relevance, novelty, alpha=0.0, beta=1.0) == [
        "a",
        "c",
        "b",
    ]
