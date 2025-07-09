from __future__ import annotations

from typing import List
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
import gzip


def _load_graph(path: str) -> Graph:
    """Carrega um grafo RDF do caminho fornecido."""
    g = Graph()
    if path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = f.read()
        g.parse(data=data, format="turtle")
    else:
        g.parse(path, format="turtle")
    return g


def recommend_logical(uri: str, ontology_path: str, top_n: int = 5) -> List[str]:
    """Retorna filmes logicamente relacionados.

    Parameters
    ----------
    uri : str
        URI do filme de referência.
    ontology_path : str
        Caminho para o dump de filmes.
    top_n : int
        Número máximo de recomendações.

    Returns
    -------
    List[str]
        URIs de filmes recomendados.
    """
    graph = _load_graph(ontology_path)
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
