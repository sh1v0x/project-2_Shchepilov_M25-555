import shlex

from prettytable import PrettyTable

from .core import (
    _convert_value,
    create_table,
    delete_rows,
    drop_table,
    insert_row,
    list_tables,
    select_rows,
    table_info,
    update_rows,
)
from .decorators import create_cacher
from .utils import (
    META_FILE,
    delete_table_data_file,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

_select_cache = create_cacher()


def print_help() -> None:
    print("\n***Операции с данными***\n")
    print("Функции:")
    print(
        '<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) '
        "- создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение> where <столбец> = "
        "<значение> - обновить записи"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - "
        "удалить записи"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nКоманды управления таблицами:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _print_rows(rows: list[dict]) -> None:
    if not rows:
        print("(пусто)")
        return

    fields = list(rows[0].keys())
    t = PrettyTable()
    t.field_names = fields
    for row in rows:
        t.add_row([row.get(f) for f in fields])
    print(t)


def _schema_type(metadata: dict, table_name: str, col: str) -> str | None:
    table = metadata.get(table_name)
    if not isinstance(table, dict):
        return None
    cols = table.get("columns", [])
    if not isinstance(cols, list):
        return None
    for c in cols:
        if c.get("name") == col:
            return c.get("type")
    return None


def parse_clause(text: str, metadata: dict, table_name: str) -> dict | None:
    if "=" not in text:
        print(f"Некорректное значение: {text}. Попробуйте снова.")
        return None

    col, raw = text.split("=", 1)
    col = col.strip()
    raw = raw.strip()

    col_type = _schema_type(metadata, table_name, col)
    if col_type is None:
        print(f"Некорректное значение: {col}. Попробуйте снова.")
        return None

    try:
        value = _convert_value(raw, col_type)
    except Exception:
        print(f"Некорректное значение: {raw}. Попробуйте снова.")
        return None

    return {col: value}


def parse_set_clause(text: str, metadata: dict, table_name: str) -> dict | None:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    result: dict = {}
    for p in parts:
        one = parse_clause(p, metadata, table_name)
        if one is None:
            return None
        result.update(one)
    return result


def parse_where_clause(text: str, metadata: dict, table_name: str) -> dict | None:
    parts = [p.strip() for p in text.split("and") if p.strip()]
    result: dict = {}
    for p in parts:
        one = parse_clause(p, metadata, table_name)
        if one is None:
            return None
        result.update(one)
    return result


def run() -> None:
    print("\n***База данных***")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)

        user_input = input("Введите команду: ").strip()
        if not user_input:
            continue

        tokens = shlex.split(user_input)
        cmd = tokens[0].lower()

        if cmd == "exit":
            break

        if cmd == "help":
            print_help()
            continue

        if cmd == "list_tables":
            list_tables(metadata)
            continue

        if cmd == "create_table":
            if len(tokens) < 3:
                print(
                    "Некорректное значение: недостаточно аргументов. "
                    "Попробуйте снова."
                )
                continue
            table_name = tokens[1]
            columns = tokens[2:]
            metadata = create_table(metadata, table_name, columns)
            save_metadata(META_FILE, metadata)
            continue

        if cmd == "drop_table":
            if len(tokens) < 2:
                print(
                    "Некорректное значение: отсутствует имя таблицы. "
                    "Попробуйте снова."
                )
                continue
            table_name = tokens[1]
            metadata = drop_table(metadata, table_name)
            save_metadata(META_FILE, metadata)
            delete_table_data_file(table_name)

            _select_cache.clear()

            continue

        # insert into <table> values (...)
        if cmd == "insert" and len(tokens) >= 4 and tokens[1].lower() == "into":
            table_name = tokens[2]
            lower_input = user_input.lower()
            idx_values = lower_input.find("values")
            if idx_values == -1:
                print(
                    "Некорректное значение: отсутствует ключевое слово values. "
                    "Попробуйте снова."
                )
                continue

            values_str = user_input[idx_values + len("values") :].strip()
            if values_str.startswith("(") and values_str.endswith(")"):
                values_str = values_str[1:-1].strip()

            raw_values = [v.strip() for v in values_str.split(",") if v.strip()]

            table_data = load_table_data(table_name)
            table_data = insert_row(metadata, table_name, raw_values, table_data)
            save_table_data(table_name, table_data)

            _select_cache.clear()

            continue

        # select from <table> [where col = value]
        if cmd == "select" and len(tokens) >= 3 and tokens[1].lower() == "from":
            table_name = tokens[2]
            table_data = load_table_data(table_name)

            lower_input = user_input.lower()
            idx_where = lower_input.find("where")

            if idx_where == -1:
                cache_key = (table_name, None)
                rows = _select_cache(cache_key, lambda: select_rows(table_data))
                _print_rows(rows)
                continue

            where_text = user_input[idx_where + len("where") :].strip()
            where_clause = parse_clause(where_text, metadata, table_name)
            if where_clause is None:
                continue

            # ключ для кэша должен быть хешируемым → dict нельзя, делаем tuple
            where_key = tuple(sorted(where_clause.items()))
            cache_key = (table_name, where_key)

            rows = _select_cache(
                cache_key, 
                lambda: select_rows(table_data, where_clause)
            )
            _print_rows(rows)
            continue


        # update <table> set col = val where col = val
        if cmd == "update" and len(tokens) >= 2:
            table_name = tokens[1]
            lower_input = user_input.lower()

            idx_set = lower_input.find(" set ")
            idx_where = lower_input.find(" where ")

            if idx_set == -1 or idx_where == -1 or idx_where < idx_set:
                print("Некорректное значение. Попробуйте снова.")
                continue

            set_text = user_input[idx_set + len(" set ") : idx_where].strip()
            where_text = user_input[idx_where + len(" where ") :].strip()

            set_clause = parse_set_clause(set_text, metadata, table_name)
            where_clause = parse_where_clause(where_text, metadata, table_name)
            if set_clause is None or where_clause is None:
                continue

            table_data = load_table_data(table_name)
            table_data, updated = update_rows(table_data, set_clause, where_clause)
            save_table_data(table_name, table_data)

            _select_cache.clear()

            if updated > 0:
                print(f'Записи в таблице "{table_name}" успешно обновлены.')
            else:
                print("Подходящие записи не найдены.")
            continue

        # delete from <table> where col = val
        if cmd == "delete" and len(tokens) >= 4 and tokens[1].lower() == "from":
            table_name = tokens[2]
            lower_input = user_input.lower()
            idx_where = lower_input.find("where")
            if idx_where == -1:
                print("Некорректное значение: отсутствует where. Попробуйте снова.")
                continue

            where_text = user_input[idx_where + len("where") :].strip()
            where_clause = parse_clause(where_text, metadata, table_name)
            if where_clause is None:
                continue

            table_data = load_table_data(table_name)
            table_data, deleted = delete_rows(table_data, where_clause)
            save_table_data(table_name, table_data)

            _select_cache.clear()

            if deleted > 0:
                print(f'Записи успешно удалены из таблицы "{table_name}".')
            else:
                print("Подходящие записи не найдены.")
            continue

        # info <table>
        if cmd == "info" and len(tokens) >= 2:
            table_name = tokens[1]
            table_data = load_table_data(table_name)
            table_info(metadata, table_name, table_data)
            continue

        print(f"Функции {cmd} нет. Попробуйте снова.")