import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL

from src.recommender.ontology_loader import load_ontology

def test_load_valid_ontology(tmp_path):
    # 1. Cria um arquivo TTL mínimo
    ttl = tmp_path / "test_ontology.ttl"
    ttl.write_text("""\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

:Video   rdf:type owl:Class .
:Usuario rdf:type owl:Class .
:Genero  rdf:type owl:Class .
""")

    # 2. Carrega a ontologia
    g = load_ontology(str(ttl))
    assert isinstance(g, Graph)

    # 3. Verifica cada classe
    base = "http://ex.org/stream#"
    for cls in ("Video", "Usuario", "Genero"):
        uri = URIRef(base + cls)
        assert any(g.triples((uri, RDF.type, OWL.Class))), \
            f"Faltou declarar {cls} como owl:Class"

def test_load_invalid_ontology(tmp_path):
    # 1. Cria um TTL sem a classe Genero
    ttl = tmp_path / "bad_ontology.ttl"
    ttl.write_text("""\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

:Video   rdf:type owl:Class .
:Usuario rdf:type owl:Class .
""")

    # 2. Deve falhar indicando falta de Genero
    with pytest.raises(ValueError) as exc:
        load_ontology(str(ttl))
    assert "Genero" in str(exc.value)
