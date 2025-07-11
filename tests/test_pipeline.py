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

# preferências do usuário
:user1 a :Usuario ;
       :prefereTematica :acao ;
       :prefereDiretor  :Spielberg .

# filmes candidatos
:videoA a :Filme ;
        :tematica    :acao ;
        :dirigidoPor :Spielberg .
:videoB a :Filme ;
        :tematica    :Drama ;
        :dirigidoPor :Spielberg .
"""


def test_generate_recommendations_basic(tmp_path, monkeypatch):
    path = tmp_path / "ont.ttl"
    path.write_text(TTL)

    ratings = {("user1", "videoA"): 5.0}

    def fake_predict(self, user_id, items):
        return {item: (0.0 if item == "videoA" else 1.0) for item in items}

    # Aqui o caminho correto para o seu wrapper simples
    monkeypatch.setattr(
        "collaborative_recommender.surprise_rs.SurpriseRS.predict",
        fake_predict,
    )

    recs = generate_recommendations(
        "user1", ratings, str(path), top_n=2, alpha=1.0, beta=0.0
    )

    assert recs[0] == "videoB"
    assert recs[1] == "videoA"
