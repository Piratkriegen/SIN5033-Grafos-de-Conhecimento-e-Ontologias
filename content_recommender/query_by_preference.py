# arquivo: content_recommender/query_by_preference.py
# Python 3

from rdflib import Graph
from typing import Any, List


def query_by_preference(
    rdf_graph: Graph,
    user_uri: str
) -> List[str]:
    """
    Executa uma SPARQL sobre o grafo inferido para retornar IDs de filmes
    que casam com as preferências do usuário.

    Por exemplo, se o usuário tem:
      :user1 :prefereTematica :acao .
      :user1 :prefereDiretor  :Spielberg .
    A consulta combina ?filme :tematica :acao OU ?filme :dirigidoPor :Spielberg.

    Parâmetros
    ----------
    rdf_graph : Graph
        Grafo RDFLib já inferido por build_ontology_graph().
    user_uri : str
        URI completa do usuário, ex: "http://ex.org/stream#user1".

    Retorna
    -------
    List[str]
        Lista de local-names (e.g. ["videoA", "videoB"]) dos filmes selecionados.
    """

    query = f"""
    PREFIX : <http://ex.org/stream#>
    SELECT ?filme WHERE {{
        {{ <{user_uri}> :prefereTematica ?t . ?filme :tematica ?t }}
        UNION
        {{ <{user_uri}> :prefereDiretor ?d . ?filme :dirigidoPor ?d }}
    }}
    """

    results = rdf_graph.query(query)
    filmes: List[str] = []
    for row in results:
        filmes.append(str(row[0]).split("#")[-1])
    return filmes
