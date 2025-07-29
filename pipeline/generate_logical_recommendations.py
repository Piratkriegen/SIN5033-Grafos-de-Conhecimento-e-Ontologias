from __future__ import annotations

from typing import List
from rdflib import Graph
import gzip
from typing import Dict

_GRAPH_CACHE: Dict[str, Graph] = {}


def clear_cache() -> None:
    """Remove all graphs stored in the cache."""

    _GRAPH_CACHE.clear()


def _load_graph(path: str) -> Graph:
    """Return an RDF graph, reusing the cache when possible.

    Parameters
    ----------
    path : str
        Path to the TTL/OWL file.

    Returns
    -------
    Graph
        Loaded RDF graph.
    """

    if path not in _GRAPH_CACHE:
        g = Graph()
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = f.read()
            g.parse(data=data, format="turtle")
        else:
            g.parse(path, format="turtle")
        _GRAPH_CACHE[path] = g
    return _GRAPH_CACHE[path]


def recommend_logical(
    uri: str,
    ontology_path: str,
    top_n: int = 5,
    rdf_graph: Graph | None = None,
) -> List[str]:
    """Return logically related movies using the local ontology.

    Parameters
    ----------
    uri : str
        Reference movie URI.
    ontology_path : str
        Path to the movie dump.
    rdf_graph : Graph, optional
        Already loaded graph to reuse.
    top_n : int
        Maximum number of recommendations.

    Returns
    -------
    List[str]
        URIs of recommended movies.
    """
    graph = rdf_graph if rdf_graph is not None else _load_graph(ontology_path)
    query = f"""
    PREFIX ex: <http://ex.org/stream#>
    PREFIX prop: <http://www.wikidata.org/prop/direct/>
    SELECT DISTINCT ?rec WHERE {{
      VALUES ?p {{ prop:P136 prop:P57 prop:P161 }}
      <{uri}> ?p ?v .
      ?rec ?p ?v .
      ?rec a ex:Filme .
      FILTER(?rec != <{uri}>)
    }} LIMIT {top_n}
    """
    results = graph.query(query)
    return [str(r[0]) for r in results]
