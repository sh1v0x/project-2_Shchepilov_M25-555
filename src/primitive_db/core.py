from __future__ import annotations

from typing import Any, Dict, List

from .decorators import confirm_action, handle_db_errors, log_time

VALID_TYPES = {"int", "str", "bool"}


def _get_table(metadata: dict, table_name: str) -> dict | None:
    table = metadata.get(table_name)
    if table is None:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    # совместимость: если почему-то лежит список колонок, оборачиваем
    if isinstance(table, list):
        metadata[table_name] = {"columns": table}
        return metadata[table_name]

    if not isinstance(table, dict):
        print(f'Ошибка: Некорректные метаданные таблицы "{table_name}".')
        return None

    return table


def _get_columns(metadata: dict, table_name: str) -> List[Dict[str, str]] | None:
    table = metadata.get(table_name)
    if table is None:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    if isinstance(table, dict):
        cols = table.get("columns", [])
        return cols if isinstance(cols, list) else []

    if isinstance(table, list):  # старый формат
        metadata[table_name] = {"columns": table}
        return table

    print(f'Ошибка: Некорректные метаданные таблицы "{table_name}".')
    return None


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: List[str]) -> dict:
    """Создать таблицу в метаданных.

    columns: список строк формата "name:type".
    Автоматически добавляется столбец ID:int в начало списка столбцов.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    user_columns: List[Dict[str, str]] = []

    for col_def in columns:
        if ":" not in col_def:
            print(f"Некорректное значение: {col_def}. Попробуйте снова.")
            return metadata

        name, type_name = col_def.split(":", 1)
        name = name.strip()
        type_name = type_name.strip()

        if type_name not in VALID_TYPES:
            print(f"Некорректное значение: {col_def}. Попробуйте снова.")
            return metadata

        user_columns.append({"name": name, "type": type_name})

    # Добавляем ID:int в начало
    schema: List[Dict[str, str]] = [{"name": "ID", "type": "int"}, *user_columns]
    metadata[table_name] = {"columns": schema}

    cols_desc = ", ".join(f'{c["name"]}:{c["type"]}' for c in schema)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_desc}')

    return metadata


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удалить таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
def list_tables(metadata: dict) -> None:
    """Вывести список всех таблиц."""
    if not metadata:
        print("Таблицы не найдены.")
        return

    for name in metadata.keys():
        print(f"- {name}")


def _convert_value(raw: str, type_name: str) -> Any:
    text = str(raw).strip()

    if type_name == "int":
        return int(text)

    if type_name == "bool":
        lowered = text.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        raise ValueError(f"Некорректное значение: {raw}. Используйте true/false.")

    if type_name == "str":
        if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
            return text[1:-1]
        raise ValueError(
            f"Некорректное значение: {raw}."
            "Строки должны быть в кавычках."
        )

    raise ValueError(f"Неизвестный тип: {type_name}")


    if type_name == "str":
        if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
            return text[1:-1]
        print(f"Некорректное значение: {raw}. Строки должны быть в кавычках.")
        raise ValueError
    
    raise ValueError(f"Неизвестный тип: {type_name}")


@log_time
@handle_db_errors
def insert_row(
    metadata: dict,
    table_name: str,
    values: List[str],
    table_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Добавить запись в таблицу (values — без ID)."""
    columns = _get_columns(metadata, table_name)
    if columns is None:
        return table_data

    non_id_columns = [c for c in columns if c["name"] != "ID"]

    if len(values) != len(non_id_columns):
        print(
            "Некорректное количество значений. "
            f"Ожидается {len(non_id_columns)}, получено {len(values)}. "
            "Попробуйте снова.",
        )
        return table_data

    existing_ids = [
        row.get("ID")
        for row in table_data
        if isinstance(row.get("ID"), int)
    ]
    new_id = max(existing_ids) + 1 if existing_ids else 1

    new_row: Dict[str, Any] = {"ID": new_id}

    for raw_value, col in zip(values, non_id_columns, strict=False):
        new_row[col["name"]] = _convert_value(raw_value, col["type"])
    
    table_data.append(new_row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


def _row_matches(row: Dict[str, Any], where_clause: Dict[str, Any] | None) -> bool:
    if not where_clause:
        return True
    for key, expected in where_clause.items():
        if row.get(key) != expected:
            return False
    return True


@log_time
@handle_db_errors
def select_rows(
    table_data: list[dict[str, Any]],
    where_clause: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not where_clause:
        return table_data

    result: list[dict[str, Any]] = []
    for row in table_data:
        ok = True
        for key, value in where_clause.items():
            if row.get(key) != value:
                ok = False
                break
        if ok:
            result.append(row)
    return result


@confirm_action("удаление записей")
@handle_db_errors
def delete_rows(
    table_data: list[dict[str, Any]],
    where_clause: dict[str, Any],
) -> tuple[list[dict[str, Any]], int]:
    new_data: list[dict[str, Any]] = []
    deleted = 0

    for row in table_data:
        ok = True
        for k, v in where_clause.items():
            if row.get(k) != v:
                ok = False
                break
        if ok:
            deleted += 1
        else:
            new_data.append(row)

    return new_data, deleted


@handle_db_errors
def update_rows(table_data: list[dict], set_clause: dict, where_clause: dict):
    """
    Обновляет строки по where_clause, применяя set_clause.
    Возвращает (новые_данные, количество_обновлённых).
    """
    updated = 0

    def match(row: dict) -> bool:
        if not where_clause:
            return True
        for k, v in where_clause.items():
            if row.get(k) != v:
                return False
        return True

    for row in table_data:
        if match(row):
            for k, v in set_clause.items():
                if k == "ID":
                    continue  # ID нельзя менять
                row[k] = v
            updated += 1

    return table_data, updated


@handle_db_errors
def table_info(metadata: dict, table_name: str, table_data: list[dict]):
    """
    Печатает информацию о таблице: имя, столбцы, количество записей.
    """
    if table_name not in metadata:
        print(f'Таблица "{table_name}" не найдена.')
        return

    cols = metadata[table_name]["columns"]
    cols_str = ", ".join([f'{c["name"]}:{c["type"]}' for c in cols])

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(table_data)}")

