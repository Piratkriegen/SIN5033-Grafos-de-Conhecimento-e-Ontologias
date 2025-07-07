# arquivo: src/recommender/pipeline.py
# Python 3

from typing import Any, Dict, List, Tuple
from rdflib import Graph

from .ontology_loader import load_ontology
from .graph_builder import build_graph
from .features.centrality import compute_betweenness
from .features.distance import compute_avg_shortest_path_length
from .recommenders.surprise_rs import SurpriseRS
from .engine import rerank


def generate_recommendations(
    user_id: Any,
    ratings: Dict[Tuple[Any, Any], float],
    ontology_path: str,
    top_n: int = 10,
    alpha: float = 0.5,
    beta: float = 0.5,
) -> List[Any]:
    """Gera recomendações serendipiosas para um usuário."""
    # 1. Carrega a ontologia
    rdf_graph: Graph = load_ontology(ontology_path)

    # 2. Constrói o grafo NetworkX
    graph_nx = build_graph(rdf_graph)

    # 3. Calcula a novidade (betweenness)
    novelty = compute_betweenness(graph_nx)

    # 4. Treina o sistema de recomendação
    rs = SurpriseRS()
    rs.fit(ratings)

    # 6. Seleciona itens que o usuário ainda não avaliou
    rated_items = {item for (user, item) in ratings if user == user_id}
    candidates = [node for node in graph_nx.nodes if node not in rated_items]

    # 5. Obtém relevância prevista para cada candidato
    relevance = rs.predict(user_id, candidates)

    # 7. Reordena com base em relevância e novidade
    ordered = rerank(candidates, relevance, novelty, alpha, beta)

    # 8. Retorna somente os ``top_n`` itens
    return ordered[:top_n]
