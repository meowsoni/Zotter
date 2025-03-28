import curses
from . import state
from .state import Note
from .ui import splash_menu, editor

def run(stdscr):
    while True:
        choice = splash_menu(stdscr)

        if choice == "new":
            state.current_note = Note()
            state.cursor_y = 0
            state.cursor_x = 0
            state.view_offset = 0
            editor(stdscr)

        elif choice == "exit":
            break
