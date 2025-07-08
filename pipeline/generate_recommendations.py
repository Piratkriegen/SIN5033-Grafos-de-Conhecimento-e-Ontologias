# pipeline/generate_recommendations.py
# Python 3

"""Pipeline para gerar recomendações serendipiosas."""

from typing import Any, Dict, List, Tuple

from rdflib import URIRef, Graph
from rdflib.namespace import RDF

from ontology.build_ontology import build_ontology_graph

from content_recommender.query_by_preference import query_by_preference
from collaborative_recommender.surprise_rs import SurpriseRS

# from serendipity.distance import compute_avg_shortest_path_length
from serendipity.centrality import compute_betweenness
from .engine import rerank

import networkx as nx

BASE = "http://ex.org/stream#"


def _build_graph(rdf_graph: Graph) -> nx.Graph:
    """Converte um ``rdflib.Graph`` em um grafo ``networkx`` simples.

    A implementação anterior considerava apenas as relações ``:assiste`` e
    ``:pertenceAGenero``. Nos testes fornecidos, entretanto, os grafos usam
    outras propriedades como ``:tematica`` e ``:dirigidoPor``. Para que a
    métrica de novidade funcione corretamente em todos os cenários de teste,
    passamos a considerar **todas** as triplas (exceto ``rdf:type``) ao
    montar o grafo.
    """

    graph = nx.Graph()

    for s, p, o in rdf_graph.triples((None, None, None)):
        if p == RDF.type:
            # 'rdf:type' apenas declara classes; não contribui para conectividade
            continue
        if not isinstance(o, URIRef):
            # ignoramos valores literais para manter apenas ligações entre nós
            continue
        graph.add_node(s)
        graph.add_node(o)
        graph.add_edge(s, o)

    return graph


def generate_recommendations(
    user_id: Any,
    ratings: Dict[Tuple[Any, Any], float],
    ontology_path: str,
    top_n: int = 10,
    alpha: float = 0.5,
    beta: float = 0.5,
) -> List[str]:
    """Gera recomendações hibridas baseadas em conteúdo e colaboração."""

    # 1. Carrega o grafo com inferência
    rdf_graph = build_ontology_graph(ontology_path)

    # 2. Seleciona candidatos via content-based (SPARQL)
    #    usando as preferências do usuário na ontologia inferida

    user_uri = BASE + str(user_id)
    # retorna lista de local-names, ex: ["videoA","videoB"]
    candidate_names = query_by_preference(rdf_graph, user_uri)
    # converte de volta para URIRefs
    candidates = [URIRef(BASE + name) for name in candidate_names]

    # (Opcional) Se não houver candidato por filtro de conteúdo,
    # pode-se cair em todos os filmes:
    if not candidates:
        video_class = URIRef(BASE + "Filme")
        candidates = [
            subj for subj, _, _ in rdf_graph.triples((None, RDF.type, video_class))
        ]

    # 3. Treina e prediz relevância colaborativa
    rs = SurpriseRS()
    # converte itens de ratings para URIRefs para compatibilidade
    ratings_uri = {
        (u, URIRef(BASE + i) if not isinstance(i, URIRef) else i): r
        for (u, i), r in ratings.items()
    }
    rs.fit(ratings_uri)
    relevance = rs.predict(user_id, candidates)

    # 4. Calcula novelty a partir do grafo
    graph_nx = _build_graph(rdf_graph)
    novelty_full = compute_betweenness(graph_nx)
    novelty = {c: novelty_full.get(c, 0.0) for c in candidates}

    # 5. Reordena
    ordered = rerank(candidates, relevance, novelty, alpha, beta)

    # 6. Extrai local-names e limita ao top_n
    return [str(uri).split("#")[-1] for uri in ordered[:top_n]]
