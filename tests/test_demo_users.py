import json
import importlib.util
import pathlib

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1] / "interface" / "streamlit_app.py"
)
spec = importlib.util.spec_from_file_location("_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
with open(MODULE_PATH, "r", encoding="utf-8") as fh:
    code = fh.read().split("# --- Configuração inicial ---", maxsplit=1)[0]
exec(code, module.__dict__)

load_demo_users = module.load_demo_users


def test_load_demo_users(tmp_path):
    data = [
        {"id": "u1", "watched": ["Q1", "Q2"]},
        {"id": "u2", "watched": ["Q3"]},
    ]
    f = tmp_path / "users.json"
    f.write_text(json.dumps(data))
    users = load_demo_users(path=str(f))
    assert users["u1"] == ["Q1", "Q2"]
