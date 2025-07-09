import pytest
from rdflib import URIRef
from pipeline.generate_recommendations import generate_recommendations

# teste de integração usando o dump real de filmes


@pytest.mark.integration
def test_generate_recommendations_real_dump():
    """Executa o pipeline usando o dump real."""
    # usuário de teste
    user_id = "user_test"
    # dicionário de ratings onde o usuário avaliou dois filmes do dump
    ratings = {
        (user_id, URIRef("http://www.wikidata.org/entity/Q44578")): 9.0,
        (user_id, URIRef("http://www.wikidata.org/entity/Q130232")): 9.0,
    }

    # gera recomendações
    recs = generate_recommendations(
        user_id=user_id,
        ratings=ratings,
        ontology_path="data/raw/serendipity_films_full.ttl.gz",
        top_n=5,
        alpha=1.0,
        beta=0.0,
    )

    # retorna lista de strings com tamanho 5
    assert isinstance(recs, list)
    assert len(recs) == 5
    # pelo menos uma recomendação deve ser diferente dos filmes avaliados
    assert any(r not in {"Q44578", "Q130232"} for r in recs)
