from __future__ import annotations

import re
from typing import Any


def parse_clause(query: str, keyword: str) -> str | None:
    """
    Extract clause (SET / WHERE) from query.
    """
    pattern = rf"\b{keyword}\b(.+)$"
    match = re.search(pattern, query, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_set_clause(
    set_clause: str,
    columns: list[dict],
    convert_value,
) -> list[tuple[str, Any]]:
    """
    Parse SET clause into list of (column, value).
    """
    column_types = {col["name"]: col["type"] for col in columns}
    assignments = []

    for part in set_clause.split(","):
        column, raw_value = part.split("=", 1)
        column = column.strip()

        if column not in column_types:
            raise ValueError(f"Unknown column '{column}'")

        value = convert_value(raw_value.strip(), column_types[column])
        assignments.append((column, value))

    return assignments


def parse_where_clause(
    where_clause: str,
    columns: list[dict],
    convert_value,
) -> list[tuple[str, str, Any]]:
    """
    Parse WHERE clause with AND conditions.
    """
    column_types = {col["name"]: col["type"] for col in columns}
    conditions = []

    parts = re.split(r"\s+and\s+", where_clause, flags=re.IGNORECASE)

    for part in parts:
        if "=" not in part:
            raise ValueError("Invalid WHERE condition")

        column, raw_value = part.split("=", 1)
        column = column.strip()

        if column not in column_types:
            raise ValueError(f"Unknown column '{column}'")

        value = convert_value(raw_value.strip(), column_types[column])
        conditions.append((column, "=", value))

    return conditions
