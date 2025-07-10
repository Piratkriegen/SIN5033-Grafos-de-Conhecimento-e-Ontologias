"""Utilidades para carregamento e inferência de ontologias."""

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL
from owlrl import DeductiveClosure, OWLRL_Semantics
import gzip


def load_ontology(path: str) -> Graph:
    """Carrega e valida uma ontologia.

    Parameters
    ----------
    path : str
        Caminho para arquivo ``.ttl`` ou ``.owl``.

    Returns
    -------
    Graph
        Grafo carregado com axiomas explícitos.

    Raises
    ------
    ValueError
        Se ``:Video``, ``:Usuario`` ou ``:Genero`` não estiverem
        definidos como classes.
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
    """Executa inferência OWL RL e retorna o grafo completo.

    Parameters
    ----------
    ontology_path : str
        Caminho para o arquivo de ontologia. Pode ser ``.ttl``, ``.owl`` ou
        versões compactadas ``.gz``.

    Returns
    -------
    Graph
        Grafo com axiomas explícitos e inferidos.
    """
    g = Graph()

    # 1) Se for .ttl.gz ou .owl.gz, descompacta primeiro
    if ontology_path.endswith((".ttl.gz", ".owl.gz", ".rdf.gz")):
        with gzip.open(ontology_path, "rt", encoding="utf-8") as f:
            data = f.read()
        # sempre formato turtle no dump
        g.parse(data=data, format="turtle")

    else:
        # 2) Tenta carregar direto por extensão e faz fallback se precisar
        ext_xml = (".owl", ".rdf", ".xml")
        fmt = "xml" if ontology_path.endswith(ext_xml) else "turtle"
        try:
            g.parse(ontology_path, format=fmt)
        except Exception:
            if fmt == "xml":
                g.parse(ontology_path, format="turtle")
            else:
                raise

    # 3) Roda o reasoner OWL RL
    DeductiveClosure(OWLRL_Semantics).expand(g)
    return g
