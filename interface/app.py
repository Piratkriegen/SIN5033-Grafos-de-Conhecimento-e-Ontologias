from __future__ import annotations

from typing import List, Tuple, Dict, Optional

import pandas as pd
import requests
from flask import Flask, render_template, request
from rdflib import Graph, URIRef

from ontology.build_ontology import build_ontology_graph
from pipeline.generate_logical_recommendations import recommend_logical
from pipeline.generate_recommendations import generate_recommendations

DATA_PATH = "data/raw/serendipity_films_full.ttl.gz"
WIKIDATA_URL = "https://query.wikidata.org/sparql"
PLACEHOLDER_IMG = "https://placehold.co/200x300?text=Poster"

app = Flask(__name__)

graph: Graph | None = None
catalog_df: pd.DataFrame | None = None


def load_graph(path: str = DATA_PATH) -> Graph:
    """Carrega a ontologia inferida.

    Parameters
    ----------
    path : str
        Caminho para o arquivo TTL/OWL.

    Returns
    -------
    Graph
        Grafo RDF com inferências.
    """
    return build_ontology_graph(path)


def load_catalog() -> pd.DataFrame:
    """Lista todos os filmes presentes no grafo global."""
    query = """
    PREFIX ex: <http://ex.org/stream#>
    SELECT DISTINCT ?f WHERE { ?f a ex:Filme . }
    """
    uris = [str(r.f) for r in graph.query(query)]
    return pd.DataFrame({"uri": uris})


def fetch_label_year(uri: str) -> Tuple[str, Optional[str]]:
    """Obtém rótulo e ano via Wikidata."""
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


def fetch_image(uri: str) -> str:
    """Retorna URL da imagem (P18) do item no Wikidata."""
    qid = uri.split("/")[-1]
    query = f"SELECT ?img WHERE {{ wd:{qid} wdt:P18 ?img }} LIMIT 1"
    try:
        resp = requests.get(
            WIKIDATA_URL,
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", {}).get("bindings", [])
        if results:
            return results[0]["img"]["value"]
    except Exception:
        pass
    return PLACEHOLDER_IMG


def get_details(graph: Graph, uri: str) -> Dict[str, List[str]]:
    """Coleta gêneros, diretores e elenco do grafo local."""
    base = "http://www.wikidata.org/prop/direct/"
    p_genre = URIRef(base + "P136")
    p_director = URIRef(base + "P57")
    p_cast = URIRef(base + "P161")

    # fmt: off
    genres = [
        fetch_label_year(str(o))[0]
        for o in graph.objects(URIRef(uri), p_genre)
    ]
    directors = [
        fetch_label_year(str(o))[0]
        for o in graph.objects(URIRef(uri), p_director)
    ]
    cast = [
        fetch_label_year(str(o))[0]
        for o in graph.objects(URIRef(uri), p_cast)
    ]
    # fmt: on
    return {"genres": genres, "directors": directors, "cast": cast}


@app.route("/")
def index():
    q = request.args.get("q", "")
    selected = request.args.get("selected")

    filtered = catalog_df
    if q:
        filtered = catalog_df[catalog_df["uri"].str.contains(q, case=False)]

    uris = filtered["uri"].tolist()
    posters = [(u, fetch_image(u), fetch_label_year(u)[0]) for u in uris]

    title = year = None
    details = {"genres": [], "directors": [], "cast": []}
    recs_log: List[Tuple[str, str, str]] = []
    recs_ser: List[Tuple[str, str, str]] = []

    if selected:
        title, year = fetch_label_year(selected)
        details = get_details(graph, selected)

        logical = recommend_logical(selected, DATA_PATH)
        # fmt: off
        recs_log = [
            (u, fetch_image(u), fetch_label_year(u)[0])
            for u in logical
        ]
        # fmt: on

        serendip = generate_recommendations(
            "user",
            {("user", URIRef(selected)): 5.0},
            DATA_PATH,
            top_n=5,
            alpha=1.0,
            beta=0.0,
        )
        # fmt: off
        ser_uris = [
            f"http://www.wikidata.org/entity/{qid}"
            for qid in serendip
        ]
        # fmt: on
        # fmt: off
        recs_ser = [
            (u, fetch_image(u), fetch_label_year(u)[0])
            for u in ser_uris
        ]
        # fmt: on

    return render_template(
        "index.html",
        posters=posters,
        q=q,
        selected=selected,
        title=title,
        year=year,
        genres=details["genres"],
        directors=details["directors"],
        cast=details["cast"],
        recs_log=recs_log,
        recs_ser=recs_ser,
    )


@app.before_request
def init_graph() -> None:
    """Carrega grafo e catálogo apenas na primeira requisição."""
    global graph, catalog_df
    if graph is None:
        graph = load_graph()
        catalog_df = load_catalog()


def create_flask_app() -> Flask:
    """Retorna a aplicação Flask configurada."""

    return app


if __name__ == "__main__":
    app.run(debug=True)
