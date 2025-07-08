# src/recommender/pipeline.py
from typing import Any, Dict, List, Tuple
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from ontology.build_ontology import load_ontology
from .graph_builder import build_graph
from serendipity.distance import compute_avg_shortest_path_length
from .recommenders.surprise_rs import SurpriseRS
from .engine import rerank

BASE = "http://ex.org/stream#"


def generate_recommendations(
    user_id: Any,
    ratings: Dict[Tuple[Any, Any], float],
    ontology_path: str,
    top_n: int = 10,
    alpha: float = 0.5,
    beta: float = 0.5,
) -> List[Any]:
    """Gera recomendações serendipiosas para um usuário."""

    # 1. Carrega a ontologia e o grafo RDFLib
    rdf_graph: Graph = load_ontology(ontology_path)

    # 2. Constrói o grafo NetworkX
    graph_nx = build_graph(rdf_graph)

    # 3. Identifica apenas as instâncias de vídeo
    #    (filtrando por rdf:type :Video)
    video_class = URIRef(BASE + "Video")
    video_nodes = [
        subj for subj, _, _ in rdf_graph.triples((None, RDF.type, video_class))
    ]

    # 4. Calcula a novidade como distância média nos vídeos
    novelty_full = compute_avg_shortest_path_length(graph_nx)
    novelty = {node: novelty_full.get(node, 0.0) for node in video_nodes}

    # 5. Treina o sistema de recomendação simplificado
    rs = SurpriseRS()
    rs.fit(ratings)

    # 6. Converte os itens já avaliados para URIRefs (não usado por ora)
    _rated_videos = {URIRef(BASE + item) for (user, item) in ratings if user == user_id}

    # 7. Define candidatos como vídeos não avaliados
    candidates = video_nodes

    # 8. Obtém relevância prevista (fake_predict será aplicado aqui no teste)
    relevance = rs.predict(user_id, candidates)

    # 9. Reordena por serendipidade
    ordered = rerank(candidates, relevance, novelty, alpha, beta)

    # 10. Converte URIRefs para local names e retorna top_n
    result = []
    for uri in ordered[:top_n]:
        # uri é URIRef("http://…#videoX"), queremos "videoX"
        result.append(str(uri).split("#")[-1])
    return result
