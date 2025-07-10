import pytest
from rdflib import Graph

import importlib.util
import pathlib

# fmt: off
MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "interface"
    / "streamlit_app.py"
)
# fmt: on
spec = importlib.util.spec_from_file_location("_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
with open(MODULE_PATH, "r", encoding="utf-8") as fh:
    code = fh.read().split("# --- Configuração inicial ---", maxsplit=1)[0]
exec(code, module.__dict__)

load_graph = module.load_graph
load_catalog = module.load_catalog

TTL = """
@prefix ex: <http://ex.org/stream#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:f1 a ex:Filme .
ex:f2 a ex:Filme .
"""


def test_load_graph_and_catalog(tmp_path):
    # Arrange
    f = tmp_path / "g.ttl"
    f.write_text(TTL, encoding="utf-8")

    # Act
    g = load_graph(path=str(f))
    module._graph = g
    df = load_catalog()

    # Assert
    assert isinstance(g, Graph)
    assert set(df["uri"]) == {
        "http://ex.org/stream#f1",
        "http://ex.org/stream#f2",
    }


def test_load_graph_invalid_path():
    with pytest.raises(Exception):
        load_graph(path="no_such_file.ttl")
