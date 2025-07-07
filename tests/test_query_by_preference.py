import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from content_recommender.query_by_preference import query_by_preference

BASE = "http://ex.org/stream#"

TTL = """\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

:user1 a :Usuario ;
       :prefereTematica :acao ;
       :prefereDiretor  :Spielberg .

:video1 a :Video ;
        :tematica       :acao ;
        :dirigidoPor    :Spielberg .

:video2 a :Video ;
        :tematica       :drama ;
        :dirigidoPor    :Spielberg .

:video3 a :Video ;
        :tematica       :drama ;
        :dirigidoPor    :Nolan .
"""

def test_query_by_preference(tmp_path):
    f = tmp_path / "g.ttl"
    f.write_text(TTL)
    g = Graph().parse(str(f), format="turtle")
    # chamamos diretamente: ele deve devolver video1 e video2
    results = query_by_preference(g, BASE + "user1")
    assert set(results) == {"video1", "video2"}
