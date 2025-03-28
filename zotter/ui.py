import curses
import threading
import time
from . import state
from .state import word_count
from .sync import sync_to_zotero

def splash_menu(stdscr):
    curses.use_default_colors()
    try:
        with open("otter.txt", "r") as f:
            otter_art = [line.rstrip('\n') for line in f.readlines()]
    except FileNotFoundError:
        otter_art = ["zotter v1 - made by sid"]

    curses.curs_set(0)
    highlight_color = curses.A_BOLD

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        text_area_height = max_y - 4

        # Draw otter art centered
        art_height = len(otter_art)
        start_y = (max_y - art_height) // 2
        for idx, line in enumerate(otter_art):
            y = start_y + idx
            x = max((max_x - len(line)) // 2, 0)
            try:
                stdscr.addstr(y, x, line[:max_x - 1], highlight_color)
            except curses.error:
                pass

        # Draw footer
        SPLASH_ACTIONS = [("N", "New Note"), ("X", "Existing Note"), ("L", "Library"), ("ESC", "Exit")]
        draw_footer(stdscr, SPLASH_ACTIONS, max_y, max_x)

        stdscr.refresh()

        try:
            key = stdscr.getch()
        except curses.error:
            continue

        if key == curses.KEY_RESIZE:
            continue
        elif key in (ord('1'), ord('n'), ord('N')):
            return "new"
        elif key in (27, ord('x'), ord('X'), ord('e'), ord('E')):
            return "exit"

def draw_footer(stdscr, actions, max_y, max_x):
    spacing = 2
    lines = []
    current_line = []
    current_width = 0

    for key, label in actions:
        total_len = len(key) + 2 + 1 + len(label)
        if current_width + total_len + (len(current_line) * spacing) > max_x and current_line:
            lines.append(current_line)
            current_line = []
            current_width = 0
        current_line.append((key, label))
        current_width += total_len
    if current_line:
        lines.append(current_line)

    footer_y = max_y - len(lines)
    for i, line in enumerate(lines):
        slots = len(line)
        total_text_len = sum(len(k) + 2 + 1 + len(l) for k, l in line)
        available_space = max_x - total_text_len
        space_between = available_space // (slots - 1) if slots > 1 else 0

        x = 0
        for j, (key, label) in enumerate(line):
            try:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(footer_y + i, x, f" {key} ")
                stdscr.attroff(curses.A_REVERSE)
                x += len(key) + 2
                stdscr.addstr(footer_y + i, x, f" {label}")
                x += len(label)
                if j < slots - 1:
                    x += space_between
            except curses.error:
                pass

def editor(stdscr):
    """Launch the note editor. Press ESC to return to splash screen."""
    curses.use_default_colors()
    stdscr.nodelay(False)
    curses.curs_set(1)

    note = state.current_note

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        text_area_height = max_y - 4
        word_str = f"{word_count()} words"
        stdscr.addstr(0, 1, word_str)
        sync_str = f"Synced {note.last_sync_time}"
        if len(sync_str) < max_x:
            stdscr.addstr(0, max_x - len(sync_str) - 1, sync_str)
        stdscr.hline(1, 0, curses.ACS_HLINE, max_x)

        if state.cursor_y < state.view_offset:
            state.view_offset = state.cursor_y
        elif state.cursor_y >= state.view_offset + text_area_height:
            state.view_offset = state.cursor_y - text_area_height + 1

        for idx in range(state.view_offset, min(state.view_offset + text_area_height, len(note.content))):
            stdscr.addstr(2 + idx - state.view_offset, 0, note.content[idx][:max_x - 1])

        stdscr.hline(max_y - 2, 0, curses.ACS_HLINE, max_x)

        EDITOR_ACTIONS = [("ESC", "Back to Home"), ("^S", "Save"), ("^A", "Assign"), ("^I", "Cite"), ("^H", "Highlight")]
        draw_footer(stdscr, EDITOR_ACTIONS, max_y, max_x)

        stdscr.move(2 + state.cursor_y - state.view_offset, state.cursor_x)
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_BACKSPACE, 127):
            if state.cursor_x > 0:
                line = note.content[state.cursor_y]
                note.content[state.cursor_y] = line[:state.cursor_x - 1] + line[state.cursor_x:]
                state.cursor_x -= 1
            elif state.cursor_y > 0:
                prev_len = len(note.content[state.cursor_y - 1])
                note.content[state.cursor_y - 1] += note.content[state.cursor_y]
                del note.content[state.cursor_y]
                state.cursor_y -= 1
                state.cursor_x = prev_len
        elif key in (curses.KEY_ENTER, 10, 13):
            current_line = note.content[state.cursor_y]
            note.content[state.cursor_y] = current_line[:state.cursor_x]
            note.content.insert(state.cursor_y + 1, current_line[state.cursor_x:])
            state.cursor_y += 1
            state.cursor_x = 0
            sync_to_zotero()  # TEMPORARY: Also sync on ENTER
        elif key == curses.KEY_UP:
            if state.cursor_y > 0:
                state.cursor_y -= 1
                state.cursor_x = min(state.cursor_x, len(note.content[state.cursor_y]))
        elif key == curses.KEY_DOWN:
            if state.cursor_y < len(note.content) - 1:
                state.cursor_y += 1
                state.cursor_x = min(state.cursor_x, len(note.content[state.cursor_y]))
        elif key == curses.KEY_LEFT:
            if state.cursor_x > 0:
                state.cursor_x -= 1
            elif state.cursor_y > 0:
                state.cursor_y -= 1
                state.cursor_x = len(note.content[state.cursor_y])
        elif key == curses.KEY_RIGHT:
            if state.cursor_x < len(note.content[state.cursor_y]):
                state.cursor_x += 1
            elif state.cursor_y < len(note.content) - 1:
                state.cursor_y += 1
                state.cursor_x = 0
        elif key == 19:  # Ctrl+S
            sync_to_zotero()
        elif key == 27:  # ESC
            return
        elif 0 <= key < 256:
            ch = chr(key)
            line = note.content[state.cursor_y]
            note.content[state.cursor_y] = line[:state.cursor_x] + ch + line[state.cursor_x:]
            state.cursor_x += 1

    curses.curs_set(0)
