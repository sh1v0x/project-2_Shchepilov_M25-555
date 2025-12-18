import os
import sys
import site
import importlib
import inspect

def main():
    print("=== RUNTIME ===")
    print("sys.executable:", sys.executable)
    print("sys.version:", sys.version.replace("\n", " "))
    print("cwd:", os.getcwd())
    print("VIRTUAL_ENV:", os.environ.get("VIRTUAL_ENV"))
    print("PATH head:", os.environ.get("PATH", "").split(":")[:5])
    print()

    print("=== PYTHON PATH (head) ===")
    for p in sys.path[:10]:
        print(" ", p)
    print()

    print("=== SITE-PACKAGES ===")
    try:
        sp = site.getsitepackages()
    except Exception:
        sp = ["<site.getsitepackages not available>"]
    print("getsitepackages:", sp)
    print()

    print("=== PACKAGE ORIGIN ===")
    try:
        import primitive_db
        import primitive_db.engine as eng
        import primitive_db.core as core
        print("primitive_db:", primitive_db.__file__)
        print("engine:", eng.__file__)
        print("core:", core.__file__)
        print()

        print("=== DECORATOR CHECK ===")
        f = core.insert_row
        print("insert_row name:", f.__name__)
        print("has __wrapped__:", hasattr(f, "__wrapped__"))
        # Покажем цепочку обёрток
        chain = []
        cur = f
        for _ in range(10):
            chain.append(getattr(cur, "__name__", str(cur)))
            cur = getattr(cur, "__wrapped__", None)
            if cur is None:
                break
        print("wrap chain:", " -> ".join(chain))
        print()

        print("=== INSERT_ROW SOURCE (first 30 lines) ===")
        src = inspect.getsource(core.insert_row).splitlines()
        for line in src[:30]:
            print(line)
    except Exception as e:
        print("FAILED to import primitive_db:", repr(e))

if __name__ == "__main__":
    main()
