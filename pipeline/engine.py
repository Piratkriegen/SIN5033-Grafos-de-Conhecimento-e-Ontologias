from typing import List, Dict, Any


def rerank(
    candidates: List[Any],
    relevance: Dict[Any, float],
    novelty: Dict[Any, float],
    alpha: float = 0.5,
    beta: float = 0.5,
) -> List[Any]:
    """Reorder items by serendipity.

    The final score is computed as
    ``alpha * novelty[item] + beta * relevance[item]``.

    Parameters
    ----------
    candidates : List[Any]
        Items to sort.
    relevance : Dict[Any, float]
        Relevance score for each item.
    novelty : Dict[Any, float]
        Novelty score for each item.
    alpha : float
        Weight of novelty in the combined score.
    beta : float
        Weight of relevance in the combined score.

    Returns
    -------
    List[Any]
        Candidates ordered from highest to lowest combined score.
    """
    scores = {}
    for item in candidates:
        score = alpha * novelty.get(item, 0.0)
        score += beta * relevance.get(item, 0.0)
        scores[item] = score
    return sorted(candidates, key=lambda x: scores[x], reverse=True)
