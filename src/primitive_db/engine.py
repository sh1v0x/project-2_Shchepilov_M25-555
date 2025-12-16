import prompt


def welcome() -> None:
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:
        cmd = prompt.string("Введите команду: ").strip()

        if cmd == "exit":
            break
        if cmd == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
            continue

        # если ввели что-то другое
        print("Неизвестная команда. Введите help для списка команд.")
