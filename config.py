from pathlib import Path
import json, os

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = Path(os.getenv("TWIN_DB_PATH", DATA_DIR / "twin.db"))
PROFILE_PATH = Path(os.getenv("TWIN_PROFILE_PATH", ROOT / "profile.json"))
SOURCES_PATH = Path(os.getenv("TWIN_SOURCES_PATH", ROOT / "sources.json"))
HOST = os.getenv("TWIN_HOST", "127.0.0.1")
PORT = int(os.getenv("TWIN_PORT", "8787"))
REFRESH_MINUTES = max(5, int(os.getenv("TWIN_REFRESH_MINUTES", "30")))

def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_profile():
    return load_json(PROFILE_PATH, {})


def load_sources():
    return load_json(SOURCES_PATH, [])
