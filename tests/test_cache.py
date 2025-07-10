from rdflib import Graph

from pipeline.generate_logical_recommendations import recommend_logical
from pipeline.generate_recommendations import generate_recommendations
from ontology.build_ontology import build_ontology_graph

TTL_LOGICAL = """\
@prefix ex: <http://ex.org/stream#> .
@prefix prop: <http://www.wikidata.org/prop/direct/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:f1 a ex:Filme ;
    prop:P136 ex:g1 ;
    prop:P57 ex:d1 .
ex:f2 a ex:Filme ;
    prop:P136 ex:g1 ;
    prop:P57 ex:d1 .
"""

TTL_PIPELINE = """\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Usuario   a rdf:Class .
:Filme     a rdf:Class .
:Tematica  a rdf:Class .
:acao      a :Tematica .
:Spielberg a rdf:Resource .

:user1 a :Usuario ;
       :prefereTematica :acao ;
       :prefereDiretor  :Spielberg .

:videoA a :Filme ;
        :tematica    :acao ;
        :dirigidoPor :Spielberg .
"""


def test_recommend_logical_reuses_graph(monkeypatch):
    g = Graph()
    g.parse(data=TTL_LOGICAL, format="turtle")
    calls = {"count": 0}

    def fake_loader(path: str) -> Graph:
        calls["count"] += 1
        return g

    monkeypatch.setattr(
        "pipeline.generate_logical_recommendations._load_graph", fake_loader
    )

    recommend_logical("http://ex.org/stream#f1", "dummy.ttl", rdf_graph=g)
    recommend_logical("http://ex.org/stream#f1", "dummy.ttl", rdf_graph=g)

    assert calls["count"] == 0


def test_generate_recommendations_reuses_graph(tmp_path, monkeypatch):
    path = tmp_path / "g.ttl"
    path.write_text(TTL_PIPELINE)
    g = build_ontology_graph(str(path))

    loader_calls = {"count": 0}

    def fake_loader(p: str) -> Graph:
        loader_calls["count"] += 1
        return g

    monkeypatch.setattr(
        "ontology.build_ontology.build_ontology_graph",
        fake_loader,
    )

    def fake_predict(self, user_id, items):
        return {item: 1.0 for item in items}

    monkeypatch.setattr(
        "collaborative_recommender.surprise_rs.SurpriseRS.predict",
        fake_predict,
    )

    ratings = {("user1", "videoA"): 5.0}

    generate_recommendations("user1", ratings, str(path), top_n=1, rdf_graph=g)
    generate_recommendations("user1", ratings, str(path), top_n=1, rdf_graph=g)

    assert loader_calls["count"] == 0
