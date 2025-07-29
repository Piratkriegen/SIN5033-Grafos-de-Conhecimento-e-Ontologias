from rdflib import Graph, URIRef
import networkx as nx


def build_graph(rdf_graph: Graph) -> nx.Graph:
    """Create an undirected ``networkx`` graph from two predicates."""

    grafo = nx.Graph()

    predicates = [
        URIRef("http://ex.org/stream#assiste"),
        URIRef("http://ex.org/stream#pertenceAGenero"),
    ]

    for predicate_uri in predicates:
        for s, _, o in rdf_graph.triples((None, predicate_uri, None)):
            grafo.add_node(s)
            grafo.add_node(o)
            grafo.add_edge(s, o)

    return grafo
