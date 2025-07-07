# arquivo: src/recommender/graph_builder.py
# Python 3

from rdflib import Graph, URIRef
import networkx as nx

def build_graph(rdf_graph: Graph) -> nx.Graph:
    """
    Converte um ``rdflib.Graph`` em um grafo ``networkx`` não-direcionado.

    Deve:
      1. Iterar sobre triplas ``(s, p, o)`` em ``rdf_graph``;
      2. Para cada tripla onde ``p`` seja
         ``http://ex.org/stream#assiste`` ou
         ``http://ex.org/stream#pertenceAGenero``, adicionar nós para ``s``
         e ``o`` e uma aresta ``(s, o)``;
      3. Retornar o grafo ``networkx`` resultante.
    """

    grafo = nx.Graph()

    predicates = [
        URIRef("http://ex.org/stream#assiste"),
        URIRef("http://ex.org/stream#pertenceAGenero"),
    ]

    for predicate_uri in predicates:
        for s, p, o in rdf_graph.triples((None, predicate_uri, None)):
            grafo.add_node(s)
            grafo.add_node(o)
            grafo.add_edge(s, o)

    return grafo
