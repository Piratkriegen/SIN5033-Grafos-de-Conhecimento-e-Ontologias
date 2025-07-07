import pytest
from rdflib import Graph
from rdflib.namespace import RDF, OWL
from rdflib import URIRef
import networkx as nx

from src.recommender.pipeline import generate_recommendations

BASE = "http://ex.org/stream#"

TTL = """\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# classes
:Video   rdf:type owl:Class .
:Usuario rdf:type owl:Class .
:Genero  rdf:type owl:Class .

# instâncias
:user1    rdf:type :Usuario .
:videoA   rdf:type :Video .
:videoB   rdf:type :Video .

# relações semânticas
:user1    :assiste        :videoA .
:videoA   :pertenceAGenero :Genero1 .
:videoB   :pertenceAGenero :Genero1 .
"""

def test_generate_recommendations_basic(tmp_path, monkeypatch):
    # 1) Cria TTL e ratings
    path = tmp_path / "ont.ttl"
    path.write_text(TTL)

    ratings = {
        # só avaliou videoA
        ("user1", "videoA"): 5.0
    }

    # 2) Force a relevância para que videoB fique acima de videoA
    def fake_predict(self, user_id, items):
        return { item: (0.0 if item == "videoA" else 1.0) for item in items }
    monkeypatch.setattr("src.recommender.recommenders.surprise_rs.SurpriseRS.predict", fake_predict)

    # 3) Gera recomendações
    recs = generate_recommendations("user1", ratings, str(path), top_n=2, alpha=1.0, beta=0.0)

    # 4) Como α=1 (só novelty), e betweenness de videoB > videoA,
    #    o primeiro deve ser videoB
    assert recs[0] == "videoB"
    assert recs[1] == "videoA"
