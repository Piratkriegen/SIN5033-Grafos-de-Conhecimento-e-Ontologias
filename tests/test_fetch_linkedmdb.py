from rdflib import Graph, URIRef
from rdflib.namespace import RDF

BASE = "http://ex.org/stream#"


def test_linkedmdb_contains_filme():
    g = Graph()
    g.parse("data/raw/linkedmdb_ex.ttl", format="turtle")

    filme = URIRef(BASE + "Filme")
    triples = list(g.triples((None, RDF.type, filme)))
    assert len(triples) > 0
