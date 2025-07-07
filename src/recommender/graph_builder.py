# arquivo: src/recommender/graph_builder.py
# Python 3

from rdflib import Graph, URIRef
import networkx as nx

def build_graph(rdf_graph: Graph) -> nx.Graph:
    """
    Converte um RDFLib Graph em um grafo NetworkX não-direcionado.

    Deve:
      1. Iterar sobre triplas (s, p, o) em rdf_graph
      2. Para cada tripla onde p seja
         - http://ex.org/stream#assiste
         - http://ex.org/stream#pertenceAGenero
        adicionar um nó para s e um nó para o, e uma aresta (s, o)
      3. Retornar o grafo NetworkX resultante
    """
