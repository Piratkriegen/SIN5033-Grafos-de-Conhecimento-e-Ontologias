import pytest
from pipeline.generate_logical_recommendations import recommend_logical
from src.base_uri import EX_BASE

TTL = f"""
@prefix ex: <{EX_BASE}> .
@prefix prop: <http://www.wikidata.org/prop/direct/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:f1 a ex:Filme ;
    prop:P136 ex:g1 ;
    prop:P57 ex:d1 .
ex:f2 a ex:Filme ;
    prop:P136 ex:g1 ;
    prop:P57 ex:d1 .
ex:f3 a ex:Filme ;
    prop:P136 ex:g2 .
"""


def test_recommend_logical_basic(tmp_path):
    f = tmp_path / "graph.ttl"
    f.write_text(TTL)

    recs = recommend_logical(
        EX_BASE + "f1",
        ontology_path=str(f),
        top_n=5,
    )
    assert EX_BASE + "f2" in recs
    assert EX_BASE + "f1" not in recs


def test_recommend_logical_no_match(tmp_path):
    f = tmp_path / "graph.ttl"
    f.write_text(TTL)

    recs = recommend_logical(
        EX_BASE + "f3",
        ontology_path=str(f),
        top_n=5,
    )
    assert recs == []


def test_recommend_logical_invalid_path():
    with pytest.raises(Exception):
        recommend_logical(
            EX_BASE + "f1",
            ontology_path="no_file.ttl",
        )
