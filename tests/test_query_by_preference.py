from rdflib import Graph
from content_recommender.query_by_preference import query_by_preference
from src.base_uri import AMAZING_BASE

BASE = AMAZING_BASE

TTL = f"""\
@prefix : <{BASE}> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Usuário com 3 tipos de preferência
:user1 a :Usuario ;
       :prefereTematica :Acao ;
       :prefereAtor    :DiCaprio ;
       :prefereDiretor :Nolan .

# Filmes
:filmeA a :Filme ;
        :tematica :Acao     ;
        :temAtor    :DiCaprio ;
        :temDiretor :Spielberg .
:filmeB a :Filme ;
        :tematica :Drama    ;
        :temAtor    :DiCaprio ;
        :temDiretor :Nolan      .
:filmeC a :Filme ;
        :tematica :Terror   ;
        :temAtor    :Someone   ;
        :temDiretor :Nolan      .
:filmeD a :Filme ;
        :tematica :Comedia  ;
        :temAtor    :Someone   ;
        :temDiretor :Spielberg .

"""


def test_query_by_preference_extended(tmp_path):
    f = tmp_path / "g.ttl"
    f.write_text(TTL)
    g = Graph().parse(str(f), format="turtle")

    # filtra por temática OR ator OR diretor
    results = query_by_preference(g, BASE + "user1")
    assert set(results) == {"filmeA", "filmeB", "filmeC"}
    # (filmeA: tema+ator, filmeB: ator+diretor, filmeC: diretor)
