import pytest
from rdflib import Graph
from rdflib.namespace import RDF
from rdflib import URIRef
import networkx as nx

from src.recommender.graph_builder import build_graph

BASE = "http://ex.org/stream#"

TEST_TTL = """\
@prefix : <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# definição de classes
:Video   rdf:type owl:Class .
:Usuario rdf:type owl:Class .
:Genero  rdf:type owl:Class .

# instâncias
:user1   rdf:type :Usuario .
:video1  rdf:type :Video .
:genre1  rdf:type :Genero .

# relações de interesse
:user1   :assiste           :video1 .
:video1  :pertenceAGenero   :genre1 .
"""

def test_build_graph(tmp_path):
    # 1. Cria e carrega o TTL
    path = tmp_path / "g.ttl"
    path.write_text(TEST_TTL)
    g_rdf = Graph()
    g_rdf.parse(str(path), format="turtle")

    # 2. Constrói o grafo NetworkX
    g_nx = build_graph(g_rdf)
    assert isinstance(g_nx, nx.Graph)

    # 3. Verifica nós e arestas
    u = URIRef(BASE + "user1")
    v = URIRef(BASE + "video1")
    c = URIRef(BASE + "genre1")
    # todos os nós devem existir
    for node in (u, v, c):
        assert g_nx.has_node(node), f"Faltou o nó {node}"
    # as duas arestas devem estar lá
    assert g_nx.has_edge(u, v), "Aresta user1--video1 faltando"
    assert g_nx.has_edge(v, c), "Aresta video1--genre1 faltando"
