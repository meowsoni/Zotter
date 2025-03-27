# __main__.py
from .ui import splash_menu, editor
import curses

def main():
    def wrapped(stdscr):
        choice = splash_menu(stdscr)
        if choice == "new":
            editor(stdscr)

    try:
        curses.wrapper(wrapped)
    except KeyboardInterrupt:
        print("\nExited Zotter cleanly.")

if __name__ == "__main__":
    main()
