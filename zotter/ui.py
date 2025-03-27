import curses
import threading
import time
from .sync import sync_to_zotero, periodic_sync
from . import state

def splash_menu(stdscr):
    try:
        with open("otter.txt", "r") as f:
            otter_art = [line.rstrip('\n') for line in f.readlines()]
    except FileNotFoundError:
        otter_art = ["zotter v1 - made by sid"]

    curses.curs_set(0)
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    art_fits = all(len(line) <= max_x for line in otter_art)

    if art_fits:
        menu = otter_art + ["", "1. New Note", "2. Existing Note (Coming Soon)", "", "ESC to Exit"]
    else:
        menu = ["zotter v1 - made by sid", "", "1. New Note", "2. Existing Note (Coming Soon)", "", "ESC to Exit"]

    for idx, line in enumerate(menu):
        x = max((max_x - len(line)) // 2, 0)
        y = (max_y // 2 - len(menu) // 2) + idx
        if 0 <= y < max_y:
            stdscr.addstr(y, x, line[:max_x - 1])

    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('1'):
            return "new"
        elif key == 27:
            return "exit"

def editor(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    text_area_height = max_y - 4

    sync_thread = threading.Thread(target=periodic_sync, daemon=True)
    sync_thread.start()

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Synced {state.last_sync_time}")
        stdscr.hline(1, 0, curses.ACS_HLINE, max_x)

        if state.cursor_y < state.view_offset:
            state.view_offset = state.cursor_y
        elif state.cursor_y >= state.view_offset + text_area_height:
            state.view_offset = state.cursor_y - text_area_height + 1

        for idx in range(state.view_offset, min(state.view_offset + text_area_height, len(state.note_content))):
            stdscr.addstr(2 + idx - state.view_offset, 0, state.note_content[idx][:max_x - 1])

        stdscr.hline(max_y - 2, 0, curses.ACS_HLINE, max_x)
        footer_left = "^S Save Note"
        word_count = sum(len(line.strip().split()) for line in state.note_content)
        footer_right = f"{word_count} words"
        stdscr.addstr(max_y - 1, 1, footer_left)
        stdscr.addstr(max_y - 1, max_x - len(footer_right) - 1, footer_right)

        stdscr.move(2 + state.cursor_y - state.view_offset, state.cursor_x)
        stdscr.refresh()

        key = stdscr.getch()

        if key == 27:
            sync_to_zotero()
            state.last_sync = time.time()
            state.last_sync_time = time.strftime("%H:%M:%S")
            break
        elif key in (curses.KEY_BACKSPACE, 127):
            if state.cursor_x > 0:
                line = state.note_content[state.cursor_y]
                state.note_content[state.cursor_y] = line[:state.cursor_x - 1] + line[state.cursor_x:]
                state.cursor_x -= 1
            elif state.cursor_y > 0:
                prev_len = len(state.note_content[state.cursor_y - 1])
                state.note_content[state.cursor_y - 1] += state.note_content[state.cursor_y]
                del state.note_content[state.cursor_y]
                state.cursor_y -= 1
                state.cursor_x = prev_len
        elif key in (curses.KEY_ENTER, 10, 13):
            current_line = state.note_content[state.cursor_y]
            state.note_content[state.cursor_y] = current_line[:state.cursor_x]
            state.note_content.insert(state.cursor_y + 1, current_line[state.cursor_x:])
            state.cursor_y += 1
            state.cursor_x = 0
            sync_to_zotero()
            state.last_sync = time.time()
            state.last_sync_time = time.strftime("%H:%M:%S")
        elif key == 19:
            sync_to_zotero()
            state.last_sync = time.time()
        elif key == curses.KEY_UP:
            if state.cursor_y > 0:
                state.cursor_y -= 1
                state.cursor_x = min(state.cursor_x, len(state.note_content[state.cursor_y]))
        elif key == curses.KEY_DOWN:
            if state.cursor_y < len(state.note_content) - 1:
                state.cursor_y += 1
                state.cursor_x = min(state.cursor_x, len(state.note_content[state.cursor_y]))
        elif key == curses.KEY_LEFT:
            if state.cursor_x > 0:
                state.cursor_x -= 1
            elif state.cursor_y > 0:
                state.cursor_y -= 1
                state.cursor_x = len(state.note_content[state.cursor_y])
        elif key == curses.KEY_RIGHT:
            if state.cursor_x < len(state.note_content[state.cursor_y]):
                state.cursor_x += 1
            elif state.cursor_y < len(state.note_content) - 1:
                state.cursor_y += 1
                state.cursor_x = 0
        elif 0 <= key < 256:
            ch = chr(key)
            line = state.note_content[state.cursor_y]
            state.note_content[state.cursor_y] = line[:state.cursor_x] + ch + line[state.cursor_x:]
            state.cursor_x += 1

    curses.curs_set(0)
