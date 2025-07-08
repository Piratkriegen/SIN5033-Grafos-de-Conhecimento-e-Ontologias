# collaborative_recommender/surprise_rs.py
from typing import Any, Dict, List, Tuple


class SurpriseRS:
    """
    Wrapper simplificado que não depende de scikit-surprise.
    No fit, só armazena o dicionário de ratings e computa média global.
    No predict, para cada item:
      - se houver ratings, retorna média dos ratings daquele item;
      - senão, retorna a média global.
    """

    def __init__(self) -> None:
        self.ratings: Dict[Tuple[Any, Any], float] = {}
        self.global_mean: float = 0.0

    def fit(self, ratings: Dict[Tuple[Any, Any], float]) -> None:
        self.ratings = ratings
        if ratings:
            self.global_mean = sum(ratings.values()) / len(ratings)

    def predict(self, user_id: Any, items: List[Any]) -> Dict[Any, float]:
        # calcula soma e contagem por item
        item_sum: Dict[Any, float] = {}
        item_count: Dict[Any, int] = {}
        for (_u, i), r in self.ratings.items():
            item_sum[i] = item_sum.get(i, 0.0) + r
            item_count[i] = item_count.get(i, 0) + 1

        # gera predições
        preds: Dict[Any, float] = {}
        for item in items:
            if item_count.get(item, 0):
                preds[item] = item_sum[item] / item_count[item]
            else:
                preds[item] = self.global_mean
        return preds
