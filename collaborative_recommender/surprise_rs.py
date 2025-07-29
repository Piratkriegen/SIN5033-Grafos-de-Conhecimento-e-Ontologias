from typing import Any, Dict, List, Tuple


class SurpriseRS:
    """Minimal recommender used for tests without external dependencies.

    The class stores the provided ratings and computes simple mean ratings for
    each item. It intentionally avoids using the ``surprise`` package.
    """

    def __init__(self) -> None:
        self.ratings: Dict[Tuple[Any, Any], float] = {}
        self.global_mean: float = 0.0

    def fit(self, ratings: Dict[Tuple[Any, Any], float]) -> None:
        """Store ratings and compute a global mean."""
        self.ratings = ratings
        if ratings:
            self.global_mean = sum(ratings.values()) / len(ratings)
        else:
            self.global_mean = 0.0

    def predict(self, user_id: Any, items: List[Any]) -> Dict[Any, float]:
        """Return a simple relevance score for each item."""
        # mean rating per item considering all users
        item_sum: Dict[Any, float] = {}
        item_count: Dict[Any, int] = {}
        for (u, i), r in self.ratings.items():
            item_sum[i] = item_sum.get(i, 0.0) + r
            item_count[i] = item_count.get(i, 0) + 1

        relevance: Dict[Any, float] = {}
        for item in items:
            if item in item_sum:
                relevance[item] = item_sum[item] / item_count[item]
            else:
                relevance[item] = self.global_mean
        return relevance
