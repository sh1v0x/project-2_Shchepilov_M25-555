SUPPORTED_TYPES = {"int", "str", "bool"}


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
   
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    table_columns: list[dict[str, str]] = []

    table_columns.append({"name": "ID", "type": "int"})

    for column in columns:
        if ":" not in column:
            raise ValueError(f"Некорректное значение: {column}")

        name, col_type = column.split(":", 1)

        if col_type not in SUPPORTED_TYPES:
            raise ValueError(f"Некорректное значение: {column}")

        table_columns.append({"name": name, "type": col_type})

    metadata[table_name] = table_columns
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Drop table from metadata."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata
