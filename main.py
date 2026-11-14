import sys

from browser_history import BrowserHistory, DEFAULT_CAPACITY

MENU = """
=============== BROWSER HISTORY MENU ===============
  visit <url> [title]   open a new page (clears forward history)
  back [n]              go back n pages      (default 1)
  forward [n]           go forward n pages   (default 1)
  current               show the active page + metadata
  history               show the whole history, cursor = [<]
  delete <url>          delete a URL from history (can be restored)
  restore               restore the most recently deleted URL
  clear                 delete ALL history
  export <file.txt>     save history to a text file
  import <file.txt>     load history from a text file
  menu                  show this menu again
  quit                  exit
====================================================
"""

#reads the optional number after each command. 
def _int_arg(parts, default=1):
    if len(parts) < 2:
        return default
    try:
        return int(parts[1])
    except ValueError:
        raise ValueError(f"'{parts[1]}' is not a whole number")

#splits the line into different parts and checks the command. 
def handle(browser, line):
    parts = line.strip().split()
    if not parts:
        return True
    cmd = parts[0].lower()

    if cmd in ("quit", "exit", "q"):
        return False
    elif cmd == "menu":
        print(MENU)
    elif cmd == "visit":
        if len(parts) < 2:
            print("usage: visit <url> [title]")
        else:
            browser.visit(parts[1], " ".join(parts[2:]) or None)
            print(f"Visited: {parts[1]}")
    elif cmd == "back":
        print("Now on:", browser.back(_int_arg(parts)))
    elif cmd == "forward":
        print("Now on:", browser.forward(_int_arg(parts)))
    elif cmd == "current":
        page = browser.current_page()
        print(page if page else "(no active page - history is empty)")
    elif cmd == "history":
        browser.display_history()
    elif cmd == "delete":
        if len(parts) < 2:
            print("usage: delete <url>")
        else:
            n = browser.delete_url(parts[1])
            print(
                f"Deleted {n} page(s)." if n else "URL not found in history.")
    elif cmd == "restore":
        url = browser.restore()
        if url:
            print("Restored:", url)
        elif browser.deleted_count():
            print("Cannot restore: history is at full capacity.")
        else:
            print("Nothing to restore.")
    elif cmd == "clear":
        browser.delete_history()
        print("All history deleted.")
    elif cmd == "export":
        if len(parts) < 2:
            print("usage: export <file.txt>")
        else:
            print(
                f"Exported {browser.export_history(parts[1])} page(s) to {parts[1]}")
    elif cmd == "import":
        if len(parts) < 2:
            print("usage: import <file.txt>")
        else:
            print(
                f"Imported {browser.import_history(parts[1])} page(s) from {parts[1]}")
    else:
        print(f"Unknown command '{cmd}'. Type 'menu' for the list.")
    return True

#read the loop and handling each commands, bad inputs and errors.
def main(argv):
    capacity = DEFAULT_CAPACITY
    if len(argv) > 1:
        try:
            capacity = int(argv[1])
        except ValueError:
            print("capacity must be an integer")
            return 1
    try:
        homepage = input(
            "Enter homepage URL [https://home.example]: ").strip() or "https://home.example"
    except (EOFError, KeyboardInterrupt):
        print()
        return 0
    try:
        browser = BrowserHistory(homepage, capacity)
    except (ValueError, TypeError) as err:      # e.g. capacity < 1
        print("Error:", err)
        return 1
    print(MENU)
    running = True
    while running:
        try:
            line = input("browser> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            running = handle(browser, line)
        except (ValueError, TypeError, OSError) as err:   # bad input / file problems
            print("Error:", err)
    print("Goodbye!")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
