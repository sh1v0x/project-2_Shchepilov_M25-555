import time
from functools import wraps
from typing import Any, Callable


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден."
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

        # ВАЖНО: безопасный возврат вместо None
        if func.__name__ in {"delete_rows", "update_rows"}:
            return args[0], 0
        return args[0] if args else None

    return wrapper


def confirm_action(action_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()

            if answer != "y":
                print("Операция отменена.")

                # ВАЖНО: вернуть "данные без изменений", чтобы engine не получил None
                if func.__name__ in {"delete_rows", "update_rows"}:
                    return args[0], 0  # (table_data, count)
                return args[0] if args else None  # metadata или table_data

            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()

        duration = end - start
        print(
            f'Функция {func.__name__} выполнилась за {duration:.3f} секунд.'
        )

        return result
    return wrapper


def create_cacher():
    cache: dict[Any, Any] = {}

    def cache_result(key: Any, value_func: Callable[[], Any]):
        if key in cache:
            return cache[key]
        value = value_func()
        cache[key] = value
        return value

    def clear():
        cache.clear()

    cache_result.clear = clear  # <- прикрепляем метод к функции
    return cache_result