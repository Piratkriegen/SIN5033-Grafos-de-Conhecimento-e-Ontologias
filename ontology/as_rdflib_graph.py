"""Utilitários para criação de grafos RDFLib."""

from rdflib import Graph


def as_rdflib_graph(path: str) -> Graph:
    """Carrega um arquivo OWL ou TTL em um :class:`rdflib.Graph`.

    Parameters
    ----------
    path : str
        Caminho para um arquivo ``.ttl`` ou ``.owl``.

    Returns
    -------
    Graph
        Grafo RDFLib resultante do ``parse`` do arquivo.
    """

    fmt = "xml" if path.endswith((".owl", ".rdf", ".xml")) else "turtle"
    g = Graph()
    g.parse(path, format=fmt)
    return g
