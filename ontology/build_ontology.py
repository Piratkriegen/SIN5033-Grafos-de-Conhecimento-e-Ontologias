# src/recommender/ontology_loader.py

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL
from owlrl import DeductiveClosure, OWLRL_Semantics

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
    # tenta normalmente Turtle; se falhar (ex.: conteúdo XML), faz fallback
    try:
        g.parse(path, format="turtle")
    except Exception:
        g.parse(path, format="xml")

    base = "http://ex.org/stream#"
    required = {
        "Video":   URIRef(base + "Video"),
        "Usuario": URIRef(base + "Usuario"),
        "Genero":  URIRef(base + "Genero"),
    }

    for name, uri in required.items():
        if not any(g.triples((uri, RDF.type, OWL.Class))):
            raise ValueError(f"Classe {name} não encontrada como owl:Class")

    return g

def build_ontology_graph(ontology_path: str) -> Graph:
    """
    Carrega uma ontologia (OWL/XML ou TTL), aplica inferência OWL-RL
    e retorna um rdflib.Graph com axiomas explícitos e inferidos.
    """
    # 1. Carrega sem validação de classes, usando fallback de formatos
    g = Graph()
    try:
        g.parse(ontology_path, format="turtle")
    except Exception:
        g.parse(ontology_path, format="xml")

    # 2. Executa a inferência OWL-RL
    DeductiveClosure(OWLRL_Semantics).expand(g)
    return g
