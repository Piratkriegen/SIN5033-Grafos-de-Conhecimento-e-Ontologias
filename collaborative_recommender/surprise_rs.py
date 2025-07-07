# arquivo: collaborative_recommender/surprise_rs.py
# Python 3

from typing import Any, Dict, List, Tuple

import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split


class SurpriseRS:
    """
    Wrapper de um algoritmo do Surprise para gerar relevância.

    Exemplo de uso:
      rs = SurpriseRS(algo=SVD())
      rs.fit(ratings_dict)
      relevance = rs.predict(user_id, item_list)

    ratings_dict: {(user_id, item_id): rating}
    """

    def __init__(self, algo=None):
        self.algo = algo or SVD()
        self._trainset = None

    def fit(self, ratings: Dict[Tuple[Any, Any], float]) -> None:
        """Constrói o Dataset Surprise e treina o modelo."""
        # converte para DataFrame
        df = pd.DataFrame(
            [(u, i, r) for (u, i), r in ratings.items()],
            columns=["user", "item", "rating"],
        )
        if df.empty:
            self._trainset = None
            return

        rating_min = df["rating"].min()
        rating_max = df["rating"].max()
        reader = Reader(rating_scale=(rating_min, rating_max))
        dataset = Dataset.load_from_df(df[["user", "item", "rating"]], reader)
        trainset, _ = train_test_split(dataset)
        self.algo.fit(trainset)
        self._trainset = trainset

    def predict(self, user_id: Any, items: List[Any]) -> Dict[Any, float]:
        """Para cada item em `items`, retorna a predição de rating."""
        predictions: Dict[Any, float] = {}
        for item in items:
            pred = self.algo.predict(user_id, item).est
            predictions[item] = pred
        return predictions
