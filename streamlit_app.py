from __future__ import annotations
from typing import List, Tuple

import pandas as pd
import requests
import streamlit as st
from rdflib import Graph, URIRef

from src.base_uri import EX_BASE

from ontology.build_ontology import build_ontology_graph
from pipeline.generate_logical_recommendations import recommend_logical
from pipeline.generate_recommendations import generate_recommendations

DATA_PATH = "data/raw/serendipity_films_full.ttl.gz"
WIKIDATA_URL = "https://query.wikidata.org/sparql"
PLACEHOLDER_IMG = "https://placehold.co/200x300?text=Poster"


@st.cache_resource
def load_graph(path: str = DATA_PATH) -> Graph:
    """Carrega a ontologia inferida.

    Parâmetros
    ----------
    path : str
        Caminho para o dump local.

    Retorna
    -------
    Graph
        Grafo RDF com inferências.
    """

    return build_ontology_graph(path)


@st.cache_data
def load_catalog() -> pd.DataFrame:
    """
    Lista todos os filmes presentes no grafo.
    Observação: prefixamos o parâmetro com _ para que o Streamlit
    não tente hashear o objeto Graph.
    """
    query = f"""
    PREFIX ex: <{EX_BASE}>
    SELECT DISTINCT ?f WHERE {{ ?f a ex:Filme . }}
    """
    # usa o grafo global _graph
    uris = [str(r.f) for r in _graph.query(query)]
    return pd.DataFrame({"uri": uris})


@st.cache_data(show_spinner=False)
def fetch_label_year(uri: str) -> Tuple[str, str | None]:
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


@st.cache_data(show_spinner=False)
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


def get_details(graph: Graph, uri: str) -> dict[str, List[str]]:
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


# --- Configuração inicial ---

_graph = load_graph()
catalog_df = load_catalog()

st.title("Amazing Video Recommender")

selected = st.selectbox(
    "\U0001f50d Selecione um filme",
    options=catalog_df["uri"],
    format_func=lambda u: fetch_label_year(u)[0],
)

if selected:
    with st.expander("Detalhes do filme"):
        title, year = fetch_label_year(selected)
        st.markdown(f"### {title} ({year or 'N/A'})")
        details = get_details(_graph, selected)
        st.write("**Gêneros:**", ", ".join(details["genres"]) or "N/A")
        st.write("**Diretores:**", ", ".join(details["directors"]) or "N/A")
        st.write("**Elenco:**", ", ".join(details["cast"]) or "N/A")

    st.subheader("Você pode gostar também de…")
    recs_log = recommend_logical(selected, DATA_PATH)
    cols = st.columns(len(recs_log))
    for col, uri in zip(cols, recs_log):
        img = fetch_image(uri)
        col.image(img, caption=fetch_label_year(uri)[0], use_column_width=True)

    st.subheader("Ou se surpreenda com…")
    recs_ser = generate_recommendations(
        "user",
        {("user", URIRef(selected)): 5.0},
        DATA_PATH,
        top_n=5,
        alpha=1.0,
        beta=0.0,
    )
    cols = st.columns(len(recs_ser))
    for col, qid in zip(cols, recs_ser):
        uri = f"http://www.wikidata.org/entity/{qid}"
        img = fetch_image(uri)
        col.image(img, caption=fetch_label_year(uri)[0], use_column_width=True)
