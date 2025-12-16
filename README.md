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