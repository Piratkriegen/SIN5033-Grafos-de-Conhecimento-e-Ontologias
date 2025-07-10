from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Dict, Tuple, Optional, Set

import requests
from rdflib import Graph, URIRef

WIKIDATA_URL = "https://query.wikidata.org/sparql"
DEFAULT_ONTOLOGY_PATH = "data/raw/serendipity_films_full.ttl.gz"
OUT_PATH = Path("data/metadata.json")


def _load_graph(path: str) -> Graph:
    """Carrega grafo RDF do arquivo informado."""
    g = Graph()
    if path.endswith((".ttl.gz", ".owl.gz", ".rdf.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            g.parse(data=fh.read(), format="turtle")
    else:
        fmt = "xml" if path.endswith((".owl", ".rdf", ".xml")) else "turtle"
        g.parse(path, format=fmt)
    return g


def extract_uris(ontology_path: str) -> Set[str]:
    """Extrai URIs de entidades presentes na ontologia."""
    graph = _load_graph(ontology_path)
    base = "http://www.wikidata.org/entity/"
    uris: Set[str] = set()
    for s, p, o in graph:
        for node in (s, p, o):
            if isinstance(node, URIRef):
                n = str(node)
                if n.startswith(base):
                    uris.add(n)
    return uris


def fetch_label_year(uri: str) -> Tuple[str, Optional[str]]:
    """Consulta o Wikidata e retorna r\xf3tulo e ano."""
    qid = uri.split("/")[-1]
    query = f"""
    SELECT ?l ?date WHERE {{
      OPTIONAL {{ wd:{qid} rdfs:label ?l FILTER(lang(?l)='en') }}
      OPTIONAL {{ wd:{qid} wdt:P577 ?date }}
    }} LIMIT 1
    """
    try:
        resp = requests.get(
            WIKIDATA_URL,
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=10,
        )
        resp.raise_for_status()
        bindings = resp.json().get("results", {}).get("bindings", [])
        if bindings:
            b = bindings[0]
            label = b.get("l", {}).get("value", qid)
            date = b.get("date", {}).get("value")
            year = date[:4] if date else None
            return label, year
    except Exception:
        pass
    return qid, None


def cache_metadata(
    ontology_path: str = DEFAULT_ONTOLOGY_PATH,
    out_path: Path = OUT_PATH,
) -> None:
    """Gera arquivo JSON com metadados de todas as URIs."""
    uris = extract_uris(ontology_path)
    data: Dict[str, Dict[str, Optional[str]]] = {}
    for uri in uris:
        label, year = fetch_label_year(uri)
        data[uri] = {"label": label, "year": year}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    cache_metadata()
