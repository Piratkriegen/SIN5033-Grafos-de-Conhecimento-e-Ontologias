from __future__ import annotations

import pandas as pd
import requests
import streamlit as st
from rdflib import Graph, URIRef

from ontology.build_ontology import build_ontology_graph
from pipeline.generate_logical_recommendations import recommend_logical
from pipeline.generate_recommendations import generate_recommendations

DATA_PATH = "data/raw/serendipity_films_full.ttl.gz"
WIKIDATA_URL = "https://query.wikidata.org/sparql"


@st.cache_resource
def load_graph(path: str = DATA_PATH) -> Graph:
    """Carrega a ontologia inferida do dump local."""
    return build_ontology_graph(path)


@st.cache_data
def load_catalog(graph: Graph) -> pd.DataFrame:
    """Extrai todos os filmes do grafo."""
    q = """
    PREFIX ex: <http://ex.org/stream#>
    SELECT DISTINCT ?f WHERE { ?f a ex:Filme . }
    """
    uris = [str(r.f) for r in graph.query(q)]
    data = {
        "Título": [uri.split("/")[-1] for uri in uris],
        "Ano": ["" for _ in uris],
        "URI": uris,
    }
    return pd.DataFrame(data)


def fetch_label(uri: str) -> str:
    """Obtém o rótulo em inglês para uma URI do Wikidata."""
    qid = uri.split("/")[-1]
    query = (
        f"SELECT ?l WHERE {{ wd:{qid} rdfs:label ?l FILTER(lang(?l)='en') }} LIMIT 1"
    )
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
            return results[0]["l"]["value"]
    except Exception:
        pass
    return qid


def fetch_label_year(uri: str) -> tuple[str, str | None]:
    """Retorna título e ano usando o endpoint do Wikidata."""
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


def get_details(graph: Graph, uri: str) -> dict[str, list[str]]:
    """Coleta gêneros, diretores e elenco do grafo local."""
    base = "http://www.wikidata.org/prop/direct/"
    p_genre = URIRef(base + "P136")
    p_director = URIRef(base + "P57")
    p_cast = URIRef(base + "P161")

    genres = [fetch_label(str(o)) for o in graph.objects(URIRef(uri), p_genre)]
    directors = [fetch_label(str(o)) for o in graph.objects(URIRef(uri), p_director)]
    cast = [fetch_label(str(o)) for o in graph.objects(URIRef(uri), p_cast)]
    return {"genres": genres, "directors": directors, "cast": cast}


# --- Streamlit UI -----------------------------------------------------------

graph = load_graph()
catalog_df = load_catalog(graph)

st.title("Amazing Video Recommender")
section = st.sidebar.radio("Navegação", ["📺 Catálogo", "🎲 Detalhes & Recomendações"])

if section == "📺 Catálogo":
    search = st.text_input("Filtrar por título")
    filtered = (
        catalog_df[catalog_df["Título"].str.contains(search, case=False)]
        if search
        else catalog_df
    )
    st.dataframe(filtered)
    selection = st.selectbox("Selecione um filme", filtered["URI"])
    st.session_state["selected_film"] = selection

else:
    uri = st.session_state.get("selected_film")
    if not uri:
        st.info("Selecione um filme na aba Catálogo.")
    else:
        title, year = fetch_label_year(uri)
        st.subheader(f"{title} ({year or 'N/A'})")
        details = get_details(graph, uri)
        st.markdown("**Gêneros:** " + ", ".join(details["genres"]) or "N/A")
        st.markdown("**Diretor(es):** " + ", ".join(details["directors"]) or "N/A")
        st.markdown("**Elenco:** " + ", ".join(details["cast"]) or "N/A")

        tab1, tab2 = st.tabs(["Recomendação Lógica", "Serendipidade"])

        with tab1:
            if st.button("Gerar", key="logical"):
                with st.spinner("Carregando recomendações..."):
                    try:
                        recs = recommend_logical(uri, DATA_PATH)
                        for r in recs:
                            st.markdown(f"- [{r.split('/')[-1]}]({r})")
                    except Exception as exc:
                        st.error(str(exc))
        with tab2:
            if st.button("Gerar", key="serendipity"):
                with st.spinner("Carregando recomendações..."):
                    try:
                        ratings = {("user", URIRef(uri)): 5.0}
                        recs = generate_recommendations(
                            user_id="user",
                            ratings=ratings,
                            ontology_path=DATA_PATH,
                            top_n=5,
                            alpha=1.0,
                            beta=0.0,
                        )
                        for qid in recs:
                            url = f"http://www.wikidata.org/entity/{qid}"
                            st.markdown(f"- [{qid}]({url})")
                    except Exception as exc:
                        st.error(str(exc))
