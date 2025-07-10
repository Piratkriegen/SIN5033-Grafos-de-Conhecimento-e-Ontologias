import importlib.util
import pathlib

from rdflib import Graph

# fmt: off
MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "interface"
    / "app.py"
)
# fmt: on
spec = importlib.util.spec_from_file_location("flask_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
with open(MODULE_PATH, "r", encoding="utf-8") as fh:
    code = fh.read().split("\n_init_app()", maxsplit=1)[0]
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
    f = tmp_path / "g.ttl"
    f.write_text(TTL, encoding="utf-8")

    g = load_graph(path=str(f))
    module.graph = g
    df = load_catalog()

    assert isinstance(g, Graph)
    assert set(df["uri"]) == {
        "http://ex.org/stream#f1",
        "http://ex.org/stream#f2",
    }


def test_load_graph_invalid_path():
    import pytest

    with pytest.raises(Exception):
        load_graph(path="no_such_file.ttl")
