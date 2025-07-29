# Amazing Video Recommender

This repository implements a movie recommendation system built on top of a knowledge graph. The ontology describes users, movies and their relationships, and reasoning is applied using OWL RL. The main modules provide SPARQL queries for content-based filtering, collaborative relevance estimation and graph-based novelty metrics.

## Package overview

- `ontology/` – ontology loading and reasoning utilities.
- `content_recommender/` – SPARQL queries for preference-based selection.
- `collaborative_recommender/` – a lightweight rating predictor.
- `serendipity/` – graph metrics used to compute novelty.
- `pipeline/` – orchestration of the recommendation flow.
- `interface/` – Streamlit web interface.
- `app.py` – minimal Flask demo.

## Recommendation workflow

1. `build_ontology_graph()` parses the OWL/TTL dump and expands it with OWL RL rules.
2. `query_by_preference()` retrieves candidate movies matching user preferences.
3. `SurpriseRS` estimates collaborative relevance from explicit ratings.
4. Functions in `serendipity/` compute novelty on the neighborhood graph.
5. `pipeline.engine.rerank()` combines relevance and novelty to produce the final list.

## Running the application

Install the dependencies once:

```bash
pip install -r requirements.txt
```

Launch the Streamlit interface:

```bash
streamlit run interface/streamlit_app.py
```

Or run the small Flask demo:

```bash
python app.py
```

## Tests and formatting

Run style checks and the test suite with:

```bash
black --check .
flake8 .
pytest --maxfail=1 --disable-warnings -q
```
