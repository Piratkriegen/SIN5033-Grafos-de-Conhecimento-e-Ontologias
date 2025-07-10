# arquivo: src/recommender/graph_builder.py
# Python 3

from rdflib import Graph, URIRef
import networkx as nx

from src.base_uri import EX_BASE


def build_graph(rdf_graph: Graph) -> nx.Graph:
    """
    Converte um ``rdflib.Graph`` em um grafo ``networkx`` não-direcionado.

    Deve:
      1. Iterar sobre triplas ``(s, p, o)`` em ``rdf_graph``;
      2. Para cada tripla onde ``p`` seja
         ``EX_BASE + 'assiste'`` ou
         ``EX_BASE + 'pertenceAGenero'``, adicionar nós para ``s``
         e ``o`` e uma aresta ``(s, o)``;
      3. Retornar o grafo ``networkx`` resultante.
    """

    grafo = nx.Graph()

    predicates = [
        URIRef(EX_BASE + "assiste"),
        URIRef(EX_BASE + "pertenceAGenero"),
    ]

    for predicate_uri in predicates:
        for s, p, o in rdf_graph.triples((None, predicate_uri, None)):
            grafo.add_node(s)
            grafo.add_node(o)
            grafo.add_edge(s, o)

    return grafo
