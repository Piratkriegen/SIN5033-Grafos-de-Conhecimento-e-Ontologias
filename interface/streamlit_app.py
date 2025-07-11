from __future__ import annotations
from typing import List, Tuple, Dict
import json

import pandas as pd
import requests
import streamlit as st
from rdflib import Graph, URIRef

from ontology.build_ontology import build_ontology_graph
from pipeline.generate_logical_recommendations import recommend_logical

DATA_PATH = "data/raw/serendipity_films_full.ttl.gz"
WIKIDATA_URL = "https://query.wikidata.org/sparql"
PLACEHOLDER_IMG = "https://placehold.co/200x300?text=Poster"
METADATA_PATH = "data/metadata.json"
USERS_PATH = "data/demo_users.json"


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
    query = """
    PREFIX ex: <http://ex.org/stream#>
    SELECT DISTINCT ?f WHERE { ?f a ex:Filme . }
    """
    # usa o grafo global _graph
    uris = [str(r.f) for r in _graph.query(query)]
    return pd.DataFrame({"uri": uris})


@st.cache_data(show_spinner=False)
def load_metadata(
    path: str = METADATA_PATH,
) -> Dict[str, Dict[str, str | None]]:
    """Carrega rótulos e anos pré-processados."""

    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def load_demo_users(path: str = USERS_PATH) -> Dict[str, List[str]]:
    """Lê usuários de demonstração."""

    try:
        with open(path, "r", encoding="utf-8") as fh:
            items = json.load(fh)
        return {u["id"]: u["watched"] for u in items}
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def fetch_label_year(uri: str) -> Tuple[str, str | None]:
    """Obtém rótulo e ano via cache local ou Wikidata."""

    qid = uri.split("/")[-1]
    if qid in _metadata:
        meta = _metadata[qid]
        return meta.get("label", qid), meta.get("year")

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
_metadata = load_metadata()
_demo_users = load_demo_users()

st.title("Amazing Video Recommender")

user = st.selectbox("Usuário de exemplo", options=list(_demo_users))
selected = None
if user:
    watched = _demo_users[user]
    selected = watched[-1]
    with st.expander("Histórico de filmes"):
        for uri in watched:
            lbl, yr = fetch_label_year(uri)
            st.write(f"- {lbl} ({yr or 'N/A'})")

if selected:
    with st.expander("Detalhes do filme"):
        title, year = fetch_label_year(selected)
        st.markdown(f"### {title} ({year or 'N/A'})")
        details = get_details(_graph, selected)
        st.write("**Gêneros:**", ", ".join(details["genres"]) or "N/A")
        st.write("**Diretores:**", ", ".join(details["directors"]) or "N/A")
        st.write("**Elenco:**", ", ".join(details["cast"]) or "N/A")

    st.subheader("Você pode gostar também de…")
    recs_log = recommend_logical(selected, DATA_PATH, rdf_graph=_graph)
    cols = st.columns(len(recs_log))
    for col, uri in zip(cols, recs_log):
        img = fetch_image(uri)
        col.image(img, caption=fetch_label_year(uri)[0], use_column_width=True)
