from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL

from ontology.as_rdflib_graph import as_rdflib_graph


def test_as_rdflib_graph_loads_ttl(tmp_path):
    ttl = tmp_path / "mini.ttl"
    ttl.write_text(
        """\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

:Item rdf:type owl:Class .
""",
        encoding="utf-8",
    )

    g = as_rdflib_graph(str(ttl))
    assert isinstance(g, Graph)
    uri = URIRef("http://ex.org/stream#Item")
    assert (uri, RDF.type, OWL.Class) in g
