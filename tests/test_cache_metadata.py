import json
import importlib.util
import pathlib

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "cache_metadata.py"
)
spec = importlib.util.spec_from_file_location("cache_module", MODULE_PATH)
cache_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cache_module)

extract_uris = cache_module.extract_uris
cache_metadata = cache_module.cache_metadata

TTL = """
@prefix ex: <http://ex.org/stream#> .
@prefix prop: <http://www.wikidata.org/prop/direct/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://www.wikidata.org/entity/Q1> a ex:Filme ;
    prop:P57 <http://www.wikidata.org/entity/Q10> .

<http://www.wikidata.org/entity/Q2> a ex:Filme .
"""


def test_extract_uris(tmp_path):
    f = tmp_path / "g.ttl"
    f.write_text(TTL, encoding="utf-8")

    uris = extract_uris(str(f))

    assert {
        "http://www.wikidata.org/entity/Q1",
        "http://www.wikidata.org/entity/Q2",
        "http://www.wikidata.org/entity/Q10",
    } <= uris


def test_cache_metadata(tmp_path, monkeypatch):
    f = tmp_path / "g.ttl"
    f.write_text(TTL, encoding="utf-8")
    out = tmp_path / "meta.json"

    def fake_fetch(uri: str):
        return ("label_" + uri.split("/")[-1], "2020")

    monkeypatch.setattr(cache_module, "fetch_label_year", fake_fetch)

    cache_metadata(str(f), out)

    data = json.loads(out.read_text(encoding="utf-8"))

    assert set(data) == {
        "http://www.wikidata.org/entity/Q1",
        "http://www.wikidata.org/entity/Q2",
        "http://www.wikidata.org/entity/Q10",
    }
    assert all(v["year"] == "2020" for v in data.values())
