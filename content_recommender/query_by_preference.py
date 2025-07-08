# content_recommender/query_by_preference.py
from rdflib import Graph
from typing import List

def query_by_preference(rdf_graph: Graph, user_uri: str) -> List[str]:
    """
    Retorna a lista de filmes que casam com as preferências do usuário,
    combinando SPARQL sobre três propriedades:

      - ?user :prefereTematica ?t . ?filme :tematica ?t
      - ?user :prefereAtor    ?a . ?filme :temAtor  ?a
      - ?user :prefereDiretor ?d . ?filme :temDiretor ?d

    Parâmetros
    ----------
    rdf_graph : Graph
        Grafo inferido por build_ontology_graph().
    user_uri : str
        URI completa do usuário (e.g. "http://amazingvideo.org#Usuario123").

    Retorna
    -------
    List[str]
        Lista de local-names (e.g. ["Filme001", "FilmeXYZ"]) sem duplicatas.
    """
    # --- complete com SPARQL + UNION ---
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
    # …aqui o Codex deve:
    #   1. executar `rdf_graph.query(sparql)`
    #   2. iterar sobre os resultados, extrair `str(f)["#"][-1]`
    #   3. devolver lista de strings
    pass
