import pytest
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS
from ontology.build_ontology import build_ontology_graph

def test_infers_subclasses_via_owlrl(tmp_path):
    # 1. Cria um OWL simples com rdfs:subClassOf
    owl = tmp_path / "test.owl"
    owl.write_text("""
    @prefix : <http://ex.org/stream#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    :Filme        a rdfs:Class .
    :Documentario a rdfs:Class ; rdfs:subClassOf :Filme .
    :doc1         a :Documentario .
    """, encoding="utf-8")

    # 2. Gera o grafo com inferências OWL-RL
    g = build_ontology_graph(str(owl))

    # 3. Deve ter inferido: doc1 rdf:type Filme
    doc1 = URIRef("http://ex.org/stream#doc1")
    filme = URIRef("http://ex.org/stream#Filme")
    assert any(g.triples((doc1, RDF.type, filme)))
