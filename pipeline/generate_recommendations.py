"""Pipeline to generate serendipitous recommendations."""

from typing import Any, Dict, List, Tuple, Optional

from rdflib import URIRef, Graph
from rdflib.namespace import RDF

from ontology.build_ontology import build_ontology_graph

from content_recommender.query_by_preference import query_by_preference

try:  # pragma: no cover - fallback for PYTHONPATH issues
    from collaborative_recommender.surprise_rs import SurpriseRS
except ModuleNotFoundError:  # fallback when package not on sys.path
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from collaborative_recommender.surprise_rs import SurpriseRS

# from serendipity.distance import compute_avg_shortest_path_length
from serendipity.centrality import compute_betweenness
from .engine import rerank

import networkx as nx

_GRAPH_CACHE: Dict[str, Graph] = {}


def clear_cache() -> None:
    """Clear all cached graphs."""

    _GRAPH_CACHE.clear()


def _load_graph(path: str) -> Graph:
    """Return an inferred graph, reusing the cache when available.

    Parameters
    ----------
    path : str
        Path to the TTL/OWL file.

    Returns
    -------
    Graph
        RDF graph with inferences.
    """

    if path not in _GRAPH_CACHE:
        _GRAPH_CACHE[path] = build_ontology_graph(path)
    return _GRAPH_CACHE[path]


BASE = "http://ex.org/stream#"


def _build_graph(rdf_graph: Graph) -> nx.Graph:
    """Convert an ``rdflib.Graph`` to a simple ``networkx`` graph.

    All triples except ``rdf:type`` are considered edges so the novelty metrics
    operate consistently across different test graphs.
    """

    graph = nx.Graph()

    for s, p, o in rdf_graph.triples((None, None, None)):
        if p == RDF.type:
            # ``rdf:type`` only declares classes and does not add connectivity
            continue
        if not isinstance(o, URIRef):
            # ignore literals to keep only edges between resources
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
    rdf_graph: Optional[Graph] = None,
) -> List[str]:
    """Generate hybrid recommendations based on content and collaboration.

    Parameters
    ----------
    user_id : Any
        Identifier of the target user.
    ratings : Dict[Tuple[Any, Any], float]
        Known user ratings.
    ontology_path : str
        Path to the ontology file.
    rdf_graph : Graph, optional
        Pre-loaded graph to reuse.
    top_n : int
        Maximum number of returned items.
    alpha : float
        Weight of novelty.
    beta : float
        Weight of relevance.
    novelty_metric : str
        Novelty metric to compute.

    Returns
    -------
    List[str]
        Identifiers of recommended videos.
    """

    # 1. Load the inferred graph, optionally reusing an existing instance
    # fmt: off
    rdf_graph = (
        rdf_graph if rdf_graph is not None else _load_graph(ontology_path)
    )
    # fmt: on

    # 2. Select candidates using content-based SPARQL filters

    user_uri = BASE + str(user_id)
    # returns a list of local names, e.g. ["videoA", "videoB"]
    candidate_names = query_by_preference(rdf_graph, user_uri)
    # convert back to URIRefs
    candidates = [URIRef(BASE + name) for name in candidate_names]

    # If no candidate is found by content filtering fall back to all movies
    if not candidates:
        video_class = URIRef(BASE + "Filme")
        triples = rdf_graph.triples((None, RDF.type, video_class))
        candidates = [subj for subj, _, _ in triples]

    # 3. Train and predict collaborative relevance
    rs = SurpriseRS()
    # convert rating items to URIRefs for compatibility
    ratings_uri = {
        (u, URIRef(BASE + i) if not isinstance(i, URIRef) else i): r
        for (u, i), r in ratings.items()
    }
    rs.fit(ratings_uri)
    relevance = rs.predict(user_id, candidates)

    # 4. Compute novelty from the graph
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

    # 5. Re-rank candidates
    ordered = rerank(candidates, relevance, novelty, alpha, beta)

    # 6. Extract local names and limit to ``top_n``
    return [str(uri).split("#")[-1] for uri in ordered[:top_n]]
