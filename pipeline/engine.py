# arquivo: src/recommender/engine.py
# Python 3

from typing import List, Dict, Any

def rerank(
    candidates: List[Any],
    relevance: Dict[Any, float],
    novelty: Dict[Any, float],
    alpha: float = 0.5,
    beta:  float = 0.5
) -> List[Any]:
    """
    Reordena uma lista de candidatos por serendipidade:
      score(item) = alpha * novelty[item] + beta * relevance[item]

    Parametros
    ----------
    candidates : List[Any]
        Itens a serem rankeados.
    relevance : Dict[Any, float]
        Score de relevancia (e.g. similaridade) por item.
    novelty : Dict[Any, float]
        Score de novidade por item.
    alpha : float
        Peso da novidade no score combinado.
    beta : float
        Peso da relevancia no score combinado.

    Retorna
    -------
    List[Any]
        Lista de candidatos ordenada do maior para o menor score combinado.
    """
    scores = {}
    for item in candidates:
        scores[item] = alpha * novelty.get(item, 0.0) + beta * relevance.get(item, 0.0)
    return sorted(candidates, key=lambda x: scores[x], reverse=True)
