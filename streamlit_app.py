from __future__ import annotations

from typing import List, Tuple

import pandas as pd
import requests
import streamlit as st
from rdflib import Graph, URIRef

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
def load_catalog(_graph: Graph) -> pd.DataFrame:
    """Lista todos os filmes presentes no grafo.

    Parâmetros
    ----------
    _graph : Graph
        Grafo já carregado.

    Retorna
    -------
    pd.DataFrame
        DataFrame contendo as URIs dos filmes.
    """

    query = """
    PREFIX ex: <http://ex.org/stream#>
    SELECT DISTINCT ?f WHERE { ?f a ex:Filme . }
    """
    uris = [str(r.f) for r in _graph.query(query)]
    return pd.DataFrame({"uri": uris})


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


def _select_uri(uri: str) -> None:
    """Atualiza a URI escolhida na sessão."""

    st.session_state.selected_uri = uri


def _show_row_of_posters(uri_list: List[str]) -> None:
    """Exibe uma fileira de capas clicáveis."""

    cols = st.columns(len(uri_list))
    for col, uri in zip(cols, uri_list):
        title, _ = fetch_label_year(uri)
        img = fetch_image(uri)
        col.image(img, use_column_width=True)
        col.button(
            title,
            key=uri,
            on_click=_select_uri,
            args=(uri,),
            use_container_width=True,
        )


# --- Configuração inicial ---

graph = load_graph()
catalog_df = load_catalog(graph)

if "selected_uri" not in st.session_state:
    st.session_state.selected_uri = None

st.title("Amazing Video Recommender")

search = st.text_input("🔍 Buscar filme")
filtered = (
    catalog_df[catalog_df["uri"].str.contains(search, case=False)]
    if search
    else catalog_df
)

uris = filtered["uri"].tolist()
# fmt: off
for i in range(0, len(uris), 5):
    _show_row_of_posters(uris[i:i + 5])
# fmt: on

selected_uri = st.session_state.get("selected_uri")
if selected_uri:
    title, year = fetch_label_year(selected_uri)
    st.header(f"{title} ({year or 'N/A'})")
    details = get_details(graph, selected_uri)
    if details["genres"]:
        st.markdown("**Gêneros:** " + ", ".join(details["genres"]))
    if details["directors"]:
        st.markdown("**Diretores:** " + ", ".join(details["directors"]))
    if details["cast"]:
        st.markdown("**Elenco:** " + ", ".join(details["cast"]))

    st.subheader("Você pode gostar também de...")
    logical = recommend_logical(selected_uri, DATA_PATH)
    _show_row_of_posters(logical)

    st.subheader("Ou você pode se surpreender com...")
    serendip = generate_recommendations(
        "user",
        {("user", URIRef(selected_uri)): 5.0},
        DATA_PATH,
        top_n=5,
        alpha=1.0,
        beta=0.0,
    )
    # fmt: off
    serendip_uris = [
        f"http://www.wikidata.org/entity/{qid}" for qid in serendip
    ]
    # fmt: on
    _show_row_of_posters(serendip_uris)
