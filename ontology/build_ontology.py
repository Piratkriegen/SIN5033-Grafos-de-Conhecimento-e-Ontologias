# src/recommender/ontology_loader.py

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL
from owlready2 import get_ontology, sync_reasoner

def load_ontology(path: str) -> Graph:
    """
    path: caminho para arquivo .ttl ou .owl
    retorna: um RDFLib Graph com todos os axiomas carregados

    Raises
    ------
    ValueError
        Se :Video, :Usuario ou :Genero não estiverem definidos como classes.
    """
    g = Graph()
    fmt = "xml" if path.endswith(('.owl', '.rdf', '.xml')) else "turtle"
    g.parse(path, format=fmt)

    base = "http://ex.org/stream#"
    required = {
        "Video": URIRef(base + "Video"),
        "Usuario": URIRef(base + "Usuario"),
        "Genero": URIRef(base + "Genero"),
    }

    # Aqui mudamos a verificação:
    # procuramos (uri, rdf:type, owl:Class)
    for name, uri in required.items():
        if not any(g.triples((uri, RDF.type, OWL.Class))):
            raise ValueError(f"Classe {name} não encontrada como owl:Class")

    return g


def build_ontology_graph(ontology_path: str) -> Graph:
    """Carrega uma ontologia OWL/XML, roda o raciocinador e retorna um grafo RDFlib.

    Parameters
    ----------
    ontology_path : str
        Caminho para o arquivo ``.owl`` contendo a ontologia.

    Returns
    -------
    Graph
        Grafo ``rdflib`` com axiomas explícitos e inferidos.
    """

    # 1. Carrega a ontologia com Owlready2
    onto = get_ontology(ontology_path).load()

    # 2. Executa o reasoner dentro do contexto da ontologia
    with onto:
        sync_reasoner()

    # 3. Exporta para um RDFLib Graph
    rdf_graph = onto.world.as_rdflib_graph()

    # 4. Retorna o grafo resultante
    return rdf_graph
