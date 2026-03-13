import json
from pathlib import Path

DATA_FILE = Path("checkins.json")


def load_checkins():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_checkins(checkins):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(checkins, f, indent=2)
