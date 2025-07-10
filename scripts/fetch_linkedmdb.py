"""Baixa um subconjunto do LinkedMDB e mapeia para a ontologia local.

O script envia uma consulta CONSTRUCT ao endpoint de SPARQL do LinkedMDB e
reinterpreta algumas classes e propriedades usando a base do projeto:

  mdb:film     -> ex:Filme
  mdb:actor    -> ex:temAtor
  mdb:director -> ex:temDiretor
  mdb:genre    -> ex:tematica

O resultado é salvo em ``data/raw/linkedmdb_ex.ttl``.
"""

from pathlib import Path

from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, TURTLE

from src.base_uri import EX_BASE

ENDPOINT = "http://data.linkedmdb.org/sparql"
BASE = EX_BASE
OUT_PATH = Path("data/raw/linkedmdb_ex.ttl")


def fetch_linkedmdb() -> None:
    """Envia consulta ao LinkedMDB e serializa o grafo resultante."""

    query = f"""
    PREFIX mdb: <http://data.linkedmdb.org/resource/movie/>
    PREFIX ex: <{BASE}>
    CONSTRUCT {{
        ?film a ex:Filme .
        ?film ex:temAtor ?actor .
        ?film ex:temDiretor ?director .
        ?film ex:tematica ?genre .
    }}
    WHERE {{
        ?film a mdb:film .
        OPTIONAL {{ ?film mdb:actor ?actor }}
        OPTIONAL {{ ?film mdb:director ?director }}
        OPTIONAL {{ ?film mdb:genre ?genre }}
    }}
    LIMIT 50
    """

    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(TURTLE)

    data = sparql.query().convert()

    rdf_graph = Graph()
    rdf_graph.parse(data=data, format="turtle")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rdf_graph.serialize(OUT_PATH, format="turtle")


if __name__ == "__main__":
    fetch_linkedmdb()
