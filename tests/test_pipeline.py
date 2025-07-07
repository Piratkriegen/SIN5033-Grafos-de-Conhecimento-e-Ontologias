from rdflib import Graph
from rdflib.namespace import RDF
from rdflib import URIRef
import pytest

from ontology.build_ontology import build_ontology_graph
from content_recommender.query_by_preference import query_by_preference
from collaborative_recommender.surprise_rs import SurpriseRS
from serendipity.distance import compute_avg_shortest_path_length
from pipeline.generate_recommendations import generate_recommendations

BASE = "http://ex.org/stream#"
TTL = """…"""  # seu TTL de teste

def test_generate_recommendations_basic(tmp_path, monkeypatch):
    path = tmp_path / "ont.ttl"
    path.write_text(TTL)

    ratings = {("user1", "videoA"): 5.0}

    def fake_predict(self, user_id, items):
        return { item: (0.0 if item == "videoA" else 1.0) for item in items }

    # Aqui o caminho correto para o seu wrapper simples
    monkeypatch.setattr(
        "collaborative_recommender.surprise_rs.SurpriseRS.predict",
        fake_predict
    )

    recs = generate_recommendations("user1", ratings, str(path),
                                   top_n=2, alpha=1.0, beta=0.0)

    assert recs[0] == "videoB"
    assert recs[1] == "videoA"
