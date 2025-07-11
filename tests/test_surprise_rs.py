# tests/test_surprise_rs.py
import pytest
from collaborative_recommender.surprise_rs import SurpriseRS


def test_surprise_rs_basic():
    ratings = {
        ("u1", "i1"): 4.0,
        ("u1", "i2"): 2.0,
        ("u2", "i1"): 3.0,
        ("u2", "i2"): 5.0,
    }
    rs = SurpriseRS()
    rs.fit(ratings)

    preds = rs.predict("u1", ["i1", "i2", "i3"])
    assert pytest.approx(preds["i1"], rel=1e-2) == 3.5
    assert pytest.approx(preds["i2"], rel=1e-2) == 3.5
    global_mean = sum(ratings.values()) / len(ratings)
    assert pytest.approx(preds["i3"], rel=1e-2) == global_mean
    assert set(preds.keys()) == {"i1", "i2", "i3"}
