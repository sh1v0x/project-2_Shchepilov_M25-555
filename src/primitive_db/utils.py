import json
import os

from .constants import DATA_DIR

ENCODING = "utf-8"
JSON_INDENT = 2
JSON_ENSURE_ASCII = False

def _table_path(table_name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{table_name}.json")

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


def load_table_data(table_name: str) -> list[dict[str, object]]:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _table_path(table_name)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_table_data(table_name: str, data: list[dict[str, object]]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _table_path(table_name)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_table_data_file(table_name: str) -> None:
    path = _table_path(table_name)
    if os.path.exists(path):
        os.remove(path)