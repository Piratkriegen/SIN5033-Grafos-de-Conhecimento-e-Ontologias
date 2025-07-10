# tests/test_pipeline_integration.py

from collaborative_recommender.surprise_rs import SurpriseRS
from ontology.build_ontology import build_ontology_graph
from pipeline.generate_recommendations import generate_recommendations

BASE = "http://ex.org/stream#"

TTL = """\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Ontologia mínima+dados
:Usuario   a rdf:Class .
:Filme     a rdf:Class .
:Tematica  a rdf:Class .
:acao      a :Tematica .
:Drama     a :Tematica .
:Spielberg a rdf:Resource .

# preferências
:user1 a :Usuario ;
       :prefereTematica :acao ;
       :prefereDiretor  :Spielberg .

# filmes
:videoA a :Filme ;
        :tematica    :acao ;
        :dirigidoPor :Spielberg .
:videoB a :Filme ;
        :tematica    :Drama ;
        :dirigidoPor :Spielberg .
:videoC a :Filme ;
        :tematica    :Drama ;
        :dirigidoPor :Nolan .
"""


def test_full_pipeline(tmp_path, monkeypatch):
    # 1. Gera o arquivo TTL e o grafo inferido
    f = tmp_path / "full.owl"
    f.write_text(TTL)
    # ratings: só avaliou videoA
    ratings = {("user1", "videoA"): 5.0}

    # 2. Monkey-patch para forçar relevância
    def fake_predict(self, user_id, items):
        return {item: (0.0 if item == "videoA" else 1.0) for item in items}

    monkeypatch.setattr(SurpriseRS, "predict", fake_predict)

    graph = build_ontology_graph(str(f))
    # 3. Chamamos o pipeline
    recs = generate_recommendations(
        user_id="user1",
        ratings=ratings,
        ontology_path=str(f),
        top_n=3,
        alpha=1.0,  # só novelty
        beta=0.0,  # ignora relevance
        rdf_graph=graph,
    )

    # 4. Como só novelty conta, videoB (maior distância) vem antes de C
    #    e depois A
    assert recs == ["videoB", "videoC", "videoA"]
