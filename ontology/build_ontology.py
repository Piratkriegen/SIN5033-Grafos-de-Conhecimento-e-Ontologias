from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL
from owlrl import DeductiveClosure, OWLRL_Semantics
import gzip


def load_ontology(path: str) -> Graph:
    """Load an ontology file and verify basic classes.

    Parameters
    ----------
    path : str
        Path to a ``.ttl`` or ``.owl`` file.

    Returns
    -------
    Graph
        RDFLib graph containing all loaded axioms.

    Raises
    ------
    ValueError
        If ``:Video``, ``:Usuario`` or ``:Genero`` are not defined as
        ``owl:Class``.
    """
    g = Graph()
    fmt = "xml" if path.endswith((".owl", ".rdf", ".xml")) else "turtle"
    g.parse(path, format=fmt)

    base = "http://ex.org/stream#"
    required = {
        "Video": URIRef(base + "Video"),
        "Usuario": URIRef(base + "Usuario"),
        "Genero": URIRef(base + "Genero"),
    }

    for name, uri in required.items():
        if not any(g.triples((uri, RDF.type, OWL.Class))):
            raise ValueError(f"Class {name} not found as owl:Class")

    return g


def build_ontology_graph(ontology_path: str) -> Graph:
    """Load an ontology, run OWL RL reasoning and return the inferred graph."""
    g = Graph()

    if ontology_path.endswith((".ttl.gz", ".owl.gz", ".rdf.gz")):
        with gzip.open(ontology_path, "rt", encoding="utf-8") as f:
            data = f.read()
        g.parse(data=data, format="turtle")

    else:
        ext_xml = (".owl", ".rdf", ".xml")
        fmt = "xml" if ontology_path.endswith(ext_xml) else "turtle"
        try:
            g.parse(ontology_path, format=fmt)
        except Exception:
            if fmt == "xml":
                g.parse(ontology_path, format="turtle")
            else:
                raise

    DeductiveClosure(OWLRL_Semantics).expand(g)
    return g
