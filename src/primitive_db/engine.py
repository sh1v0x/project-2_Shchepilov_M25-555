import shlex

from src.primitive_db.core import create_table, drop_table
from src.primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"


def print_help() -> None:
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    print("\n***База данных***")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)

        try:
            user_input = input("Введите команду: ").strip()
            if not user_input:
                continue

            args = shlex.split(user_input)
            command = args[0]

            if command == "exit":
                break

            if command == "help":
                print_help()
                continue

            if command == "list_tables":
                if not metadata:
                    print("Таблицы отсутствуют.")
                else:
                    for table in metadata:
                        print(f"- {table}")
                continue

            if command == "create_table":
                if len(args) < 3:
                    raise ValueError("Недостаточно аргументов.")

                table_name = args[1]
                columns = args[2:]

                metadata = create_table(metadata, table_name, columns)
                save_metadata(META_FILE, metadata)

                cols_str = ", ".join(
                    f'{col["name"]}:{col["type"]}' for col in metadata[table_name]
                )
                print(
                    f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}'
                )
                continue

            if command == "drop_table":
                if len(args) != 2:
                    raise ValueError("Недостаточно аргументов.")

                table_name = args[1]
                metadata = drop_table(metadata, table_name)
                save_metadata(META_FILE, metadata)

                print(f'Таблица "{table_name}" успешно удалена.')
                continue

            print(f"Функции {command} нет. Попробуйте снова.")

        except ValueError as exc:
            print(f"{exc}. Попробуйте снова.")