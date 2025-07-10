import pytest
from rdflib import Graph
from src.base_uri import EX_BASE

import importlib.util
import pathlib

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "streamlit_app.py"
spec = importlib.util.spec_from_file_location("_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
with open(MODULE_PATH, "r", encoding="utf-8") as fh:
    code = fh.read().split("# --- Configuração inicial ---", maxsplit=1)[0]
exec(code, module.__dict__)

load_graph = module.load_graph
load_catalog = module.load_catalog

TTL = f"""
@prefix ex: <{EX_BASE}> .
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
        EX_BASE + "f1",
        EX_BASE + "f2",
    }


def test_load_graph_invalid_path():
    with pytest.raises(Exception):
        load_graph(path="no_such_file.ttl")
