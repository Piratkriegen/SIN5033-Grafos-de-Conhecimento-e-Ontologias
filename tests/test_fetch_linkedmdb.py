from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from src.base_uri import EX_BASE

BASE = EX_BASE


def test_linkedmdb_contains_filme():
    g = Graph()
    g.parse("data/raw/linkedmdb_ex.ttl", format="turtle")

    filme = URIRef(BASE + "Filme")
    triples = list(g.triples((None, RDF.type, filme)))
    assert len(triples) > 0
