import json
from pathlib import Path
from typing import Any

META_FILE = "db_meta.json"
DATA_DIR = Path("data")


def load_metadata(filepath: str) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_table_data(table_name: str) -> list[dict[str, Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{table_name}.json"

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_table_data(table_name: str, data: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{table_name}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        

def delete_table_data_file(table_name: str) -> None:
    path = DATA_DIR / f"{table_name}.json"
    if path.exists():
        path.unlink()