from rdflib import Graph
from typing import List


def query_by_preference(rdf_graph: Graph, user_uri: str) -> List[str]:
    """Retrieve movies that match a user's declared preferences.

    The SPARQL query checks for preferred genres, actors and directors and
    returns unique movie identifiers that satisfy at least one of these
    criteria.

    Parameters
    ----------
    rdf_graph : Graph
        Ontology graph produced by ``build_ontology_graph``.
    user_uri : str
        Full URI of the user.

    Returns
    -------
    List[str]
        Local names of matching movies without duplicates.
    """
    sparql = f"""
    PREFIX : <http://amazingvideo.org#>

    SELECT DISTINCT ?filme WHERE {{
      {{ <{user_uri}> :prefereTematica ?t .
         ?filme        :tematica       ?t . }}
      UNION
      {{ <{user_uri}> :prefereAtor    ?a .
         ?filme        :temAtor        ?a . }}
      UNION
      {{ <{user_uri}> :prefereDiretor ?d .
         ?filme        :temDiretor     ?d . }}
    }}
    """

    results = rdf_graph.query(sparql)
    filmes: List[str] = []
    for row in results:
        filme_uri = row[0]
        filmes.append(str(filme_uri).split("#")[-1])

    return filmes
