# SIN5033-Grafos-de-Conhecimento-e-Ontologias

Este repositório implementa um sistema de recomendação de filmes baseado em grafos de conhecimento. A ontologia descreve usuários, filmes e seus relacionamentos e é enriquecida com inferências OWL RL. Sobre este grafo são executadas consultas SPARQL para recomendações baseadas em conteúdo e cálculos de métricas de serendipidade para reranqueamento das sugestões.

## Estrutura dos pacotes

- `ontology/` &ndash; carregamento da ontologia e inferência com `owlrl`.
- `content_recommender/` &ndash; consultas SPARQL para recomendações por preferência.
- `serendipity/` &ndash; cálculo de métricas de grafo (centralidade, distância etc.).
- `pipeline/` &ndash; orquestração do fluxo de recomendação e reranqueamento.
- `interface/` &ndash; interface web em Streamlit (`interface/streamlit_app.py`).
- `app.py` &ndash; pequena demonstração em Flask.

## Fluxo de recomendação

1. `build_ontology_graph()` carrega o arquivo OWL/TTL e aplica deduções OWL RL.
2. `query_by_preference()` extrai candidatos que casam com as preferências declaradas pelo usuário.
3. `SurpriseRS` estima relevância colaborativa a partir dos ratings.
4. Métricas em `serendipity/` calculam novidade em um grafo de vizinhança.
5. `pipeline.engine.rerank()` combina relevância e novidade para produzir a lista final.

## Executando a aplicação

Instale as dependências uma vez:

```bash
pip install -r requirements.txt
```

Interface Streamlit:

```bash
streamlit run interface/streamlit_app.py
```

Demonstrador Flask:

```bash
python app.py
```

## Executando os testes

Rode as ferramentas de estilo e a suíte de testes:

```bash
black --check .
flake8 .
pytest --maxfail=1 --disable-warnings -q
```

