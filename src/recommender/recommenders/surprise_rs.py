from typing import Any, Dict, List, Tuple

class SurpriseRS:
    """Pequena implementação simplificada de um sistema de recomendação.

    Esta classe não utiliza a biblioteca ``surprise`` para evitar depender de
    pacotes externos durante os testes. O treinamento consiste em armazenar as
    avaliações fornecidas, esperando que ``ratings`` seja um dicionário no
    formato ``{(usuario, item): nota}``.
    """

    def __init__(self) -> None:
        self.ratings: Dict[Tuple[Any, Any], float] = {}
        self.global_mean: float = 0.0

    def fit(self, ratings: Dict[Tuple[Any, Any], float]) -> None:
        """Armazena as avaliações e calcula a média global."""
        self.ratings = ratings
        if ratings:
            self.global_mean = sum(ratings.values()) / len(ratings)
        else:
            self.global_mean = 0.0

    def predict(self, user_id: Any, items: List[Any]) -> Dict[Any, float]:
        """Retorna uma relevância simples para cada item."""
        # média das notas para cada item considerando todos os usuários
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
