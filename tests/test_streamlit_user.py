import importlib.util
import pathlib

import pytest

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1] / "interface" / "streamlit_app.py"
)
spec = importlib.util.spec_from_file_location("_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
with open(MODULE_PATH, "r", encoding="utf-8") as fh:
    code = fh.read().split("# --- Configuração inicial ---", maxsplit=1)[0]
exec(code, module.__dict__)

load_users = module.load_users
generate_recommendations = module.generate_recommendations

TTL = """\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Usuario   a rdf:Class .
:Filme     a rdf:Class .
:Tematica  a rdf:Class .
:acao      a :Tematica .
:Drama     a :Tematica .
:Spielberg a rdf:Resource .

:user1 a :Usuario ;
       :prefereTematica :acao ;
       :prefereDiretor  :Spielberg .

:videoA a :Filme ;
        :tematica    :acao ;
        :dirigidoPor :Spielberg .
:videoB a :Filme ;
        :tematica    :Drama ;
        :dirigidoPor :Spielberg .
"""


def test_load_users(tmp_path):
    j = tmp_path / "u.json"
    j.write_text('{"user1": {"videoA": 5.0}}', encoding="utf-8")

    users = load_users(path=str(j))

    assert users == {"user1": {"videoA": 5.0}}


def test_recommendations_with_user_ratings(tmp_path, monkeypatch):
    ttl_path = tmp_path / "g.ttl"
    ttl_path.write_text(TTL, encoding="utf-8")
    json_path = tmp_path / "u.json"
    json_path.write_text('{"user1": {"videoA": 5.0}}', encoding="utf-8")

    users = load_users(path=str(json_path))
    ratings = {("user1", vid): r for vid, r in users["user1"].items()}

    def fake_predict(self, user_id, items):
        return {item: (0.0 if item == "videoA" else 1.0) for item in items}

    monkeypatch.setattr(
        "collaborative_recommender.surprise_rs.SurpriseRS.predict", fake_predict
    )

    recs = generate_recommendations(
        "user1", ratings, str(ttl_path), top_n=2, alpha=1.0, beta=0.0
    )

    assert recs == ["videoB", "videoA"]
