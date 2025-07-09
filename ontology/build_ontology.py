# src/recommender/ontology_loader.py

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL
from owlrl import DeductiveClosure, OWLRL_Semantics
import gzip

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
    fmt = "xml" if path.endswith((".owl", ".rdf", ".xml")) else "turtle"
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
    """
    Carrega uma ontologia (TTL, OWL ou TTL.GZ), executa inferências OWL RL
    e retorna um rdflib.Graph com axiomas explícitos e inferidos.
    """
    g = Graph()

    # 1) Se for .ttl.gz ou .owl.gz, descompacta primeiro
    if ontology_path.endswith((".ttl.gz", ".owl.gz", ".rdf.gz")):
        with gzip.open(ontology_path, "rt", encoding="utf-8") as f:
            data = f.read()
        # sempre formato turtle no dump
        g.parse(data=data, format="turtle")

    else:
        # 2) Tenta carregar direto por extensão
        fmt = "xml" if ontology_path.endswith((".owl", ".rdf", ".xml")) else "turtle"
        g.parse(ontology_path, format=fmt)

    # 3) Roda o reasoner OWL RL
    DeductiveClosure(OWLRL_Semantics).expand(g)
    return g
