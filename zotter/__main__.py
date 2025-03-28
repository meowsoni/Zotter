# __main__.py
import curses
from .controller import run

def main():
    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        print("\nExited Zotter cleanly.")

if __name__ == "__main__":
    main()
