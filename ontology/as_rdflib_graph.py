"""Helper utilities to load OWL or TTL files as ``rdflib.Graph`` objects."""

from rdflib import Graph


def as_rdflib_graph(path: str) -> Graph:
    """Load an ontology file into an ``rdflib.Graph``.

    Parameters
    ----------
    path : str
        Path to a ``.ttl`` or ``.owl`` file.

    Returns
    -------
    Graph
        Parsed RDFLib graph.
    """

    fmt = "xml" if path.endswith((".owl", ".rdf", ".xml")) else "turtle"
    g = Graph()
    g.parse(path, format=fmt)
    return g
