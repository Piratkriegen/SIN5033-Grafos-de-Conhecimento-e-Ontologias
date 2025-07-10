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
            # 'rdf:type' apenas declara classes; não contribui para
            # conectividade
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
    novelty_metric: str = "betweenness",
    rdf_graph: Graph | None = None,
) -> List[str]:
    """Gera recomendações híbridas baseadas em conteúdo e colaboração.

    Parameters
    ----------
    user_id : Any
        Identificador do usuário.
    ratings : Dict[Tuple[Any, Any], float]
        Avaliações conhecidas.
    ontology_path : str
        Caminho para o arquivo de ontologia.
    top_n : int
        Número máximo de itens retornados.
    alpha : float
        Peso de novidade.
    beta : float
        Peso de relevância.
    novelty_metric : str
        Métrica de novidade a ser utilizada.

    rdf_graph : Graph | None, optional
        Grafo RDF pré-carregado. Se ``None``, o grafo será construído a
        partir de ``ontology_path``.

    Returns
    -------
    List[str]
        Lista de identificadores de vídeo.
    """

    # 1. Carrega o grafo com inferência
    if rdf_graph is None:
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
        triples = rdf_graph.triples((None, RDF.type, video_class))
        candidates = [subj for subj, _, _ in triples]

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

    from serendipity.metrics import (
        compute_clustering_coefficient,
        compute_pagerank,
        compute_hhi,
    )

    if novelty_metric == "betweenness":
        novelty_full = compute_betweenness(graph_nx)
    elif novelty_metric == "avg_shortest_path":
        from serendipity.distance import compute_avg_shortest_path_length

        novelty_full = compute_avg_shortest_path_length(graph_nx)
    elif novelty_metric == "clustering":
        novelty_full = compute_clustering_coefficient(graph_nx)
    elif novelty_metric == "pagerank":
        novelty_full = compute_pagerank(graph_nx)
    elif novelty_metric == "hhi":
        from networkx.algorithms import community

        communities = {}
        louvain = community.louvain_communities(graph_nx, seed=42)
        for cid, comm in enumerate(louvain):
            for node in comm:
                communities[node] = cid
        novelty_full = compute_hhi(graph_nx, communities)
    else:
        raise ValueError(f"Unknown novelty_metric: {novelty_metric}")
    novelty = {c: novelty_full.get(c, 0.0) for c in candidates}

    # 5. Reordena
    ordered = rerank(candidates, relevance, novelty, alpha, beta)

    # 6. Extrai local-names e limita ao top_n
    return [str(uri).split("#")[-1] for uri in ordered[:top_n]]
