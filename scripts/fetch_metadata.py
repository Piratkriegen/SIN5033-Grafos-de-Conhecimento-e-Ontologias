import json
import gzip
from pathlib import Path
from rdflib import Graph, URIRef
import requests

DATA_PATH = Path("data/raw/serendipity_films_full.ttl.gz")
OUT_PATH = Path("data/metadata.json")
WIKIDATA_URL = "https://query.wikidata.org/sparql"


def load_uris(path: Path) -> list[str]:
    """Extrai URIs de filmes do dump local."""
    g = Graph()
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = f.read()
    g.parse(data=data, format="turtle")
    ex = "http://ex.org/stream#"
    query = "PREFIX ex: <http://ex.org/stream#> SELECT DISTINCT ?f WHERE { ?f a ex:Filme . }"
    return [str(r.f) for r in g.query(query)]


def fetch_label_year(uri: str) -> tuple[str, str | None]:
    """Consulta label e ano de lançamento no Wikidata."""
    qid = uri.split("/")[-1]
    sparql = f"SELECT ?l ?date WHERE {{ OPTIONAL {{ wd:{qid} rdfs:label ?l FILTER(lang(?l)='en') }} OPTIONAL {{ wd:{qid} wdt:P577 ?date }} }} LIMIT 1"
    try:
        resp = requests.get(
            WIKIDATA_URL,
            params={"query": sparql},
            headers={"Accept": "application/sparql-results+json"},
            timeout=10,
        )
        resp.raise_for_status()
        bindings = resp.json().get("results", {}).get("bindings", [])
        if bindings:
            b = bindings[0]
            label = b.get("l", {}).get("value", qid)
            date = b.get("date", {}).get("value")
            return label, date[:4] if date else None
    except Exception:
        pass
    return qid, None


def build_metadata() -> None:
    """Gera arquivo JSON com labels e anos."""
    uris = load_uris(DATA_PATH)
    data = {}
    for uri in uris:
        label, year = fetch_label_year(uri)
        data[uri.split("/")[-1]] = {"label": label, "year": year}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    build_metadata()
