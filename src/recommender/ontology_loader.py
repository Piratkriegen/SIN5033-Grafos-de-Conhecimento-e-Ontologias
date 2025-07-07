# Python 3
from rdflib import Graph, URIRef
from rdflib.namespace import RDF


def load_ontology(path: str) -> Graph:
    """Load ontology file and validate required classes exist.

    Parameters
    ----------
    path : str
        Path to a .ttl or .owl file.

    Returns
    -------
    Graph
        RDFLib Graph with all triples loaded.

    Raises
    ------
    ValueError
        If :Video, :Usuario or :Genero classes are not defined.
    """
    g = Graph()
    # Determine format by extension (defaults to turtle)
    fmt = "xml" if path.endswith(('.owl', '.rdf', '.xml')) else "turtle"
    g.parse(path, format=fmt)

    base = "http://ex.org/stream#"
    required = {
        "Video": URIRef(base + "Video"),
        "Usuario": URIRef(base + "Usuario"),
        "Genero": URIRef(base + "Genero"),
    }
    for name, uri in required.items():
        if not any(g.triples((None, RDF.type, uri))):
            raise ValueError(f"Classe {name} n\u00e3o encontrada")

    return g
