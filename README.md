## Управление таблицами

Программа предоставляет консольный интерфейс для управления таблицами базы данных.

### Доступные команды

- `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` — создать таблицу  
  Поддерживаемые типы данных: `int`, `str`, `bool`.  
  Столбец `ID:int` добавляется автоматически.

- `list_tables` — показать список всех таблиц.

- `drop_table <имя_таблицы>` — удалить таблицу.

- `help` — показать справочную информацию.

- `exit` — выйти из программы.

### Пример использования

```text
Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

Введите команду: list_tables
- users

Введите команду: drop_table users
Таблица "users" успешно удалена.
```

## Демонстрация работы
[![asciinema](https://asciinema.org/a/72PlXwiGwSnwmvaFk3yEPCfIq.svg)](https://asciinema.org/a/72PlXwiGwSnwmvaFk3yEPCfIq)

## Демонстрация CRUD-операций

[![asciinema](https://asciinema.org/a/WXOGCMQnmGvAWe7ovP27EyLfa.svg)](https://asciinema.org/a/WXOGCMQnmGvAWe7ovP27EyLfa)

## Декораторы и надёжность

В проекте используются декораторы для повышения качества кода и удобства работы:

- **handle_db_errors** — централизованная обработка ошибок (ValueError, KeyError, FileNotFoundError и др.).
  Ошибки отображаются в консоли, приложение не падает.
- **confirm_action(action_name)** — подтверждение опасных операций.
  Перед удалением таблицы или удалением записей запрашивается подтверждение: `[y/n]`.
- **log_time** — замер времени выполнения “медленных” операций (например, insert/select) с выводом:
  `Функция <имя_функции> выполнилась за X.XXX секунд.`

Также для ускорения повторяющихся запросов в `select` используется кэширование результатов на основе замыкания.

## Демонстрация работы CLI (CRUD + декораторы):

[![asciinema](https://asciinema.org/a/gwaSaK0r6QGZ9sxYb90gxTpwo.svg)](https://asciinema.org/a/gwaSaK0r6QGZ9sxYb90gxTpwo)