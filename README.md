# Zotter
Zotter is a note-taking app that syncs with Zotero. It is designed to run on a homebrew e-paper typewriter, or a cyberdeck, or any device that you can take into a library and take notes on without getting distracted by a web browser.

<pre>
      .----.__
     / c  ^  _`;
     |     .--'
      \   (
      /  -.\
     / .   \
    /  \    |
   ;    `-. `.
   |      /`'.`.
   |      |   \ \
   |    __|    `'
   ;   /   \
  ,'        | zotter v1
 (_`'---._ /--,
   `'---._`'---..__
sid made  `''''--, )
            _.-'`,`
             ````
</pre>

**Zotter is written in Python.** It does not currently have a local files repository and uses Zotero Web API's `POST` and `PATCH` function to upload notes directly to Zotero as JSON objects.

Here is the project structure:

```
/
├── config.json                # Your Zotero credentials (API key & user ID)
├── otter.txt                  # Otter ASCII splash art logo
└── zotter/                    # Python package
    ├── __init__.py            # Marks this directory as a package
    ├── __main__.py            # Entry point when running `python3 -m zotter`
    ├── config.py              # Loads config.json
    ├── state.py               # Global variables (note content, cursor, etc.)
    ├── log.py                 # Error logging
    ├── sync.py                # Handles syncing with Zotero via Web API
    └── ui.py                  # Curses UI
```

**DEPENDENCIES** <br>
The only dependency is `python3` as the project's UI is built using `curses` and it uses standard keyboard input `sys.stdin`
If you are using a custom keyboard, make sure it is running QMK firmware.

**SUGGESTED HARDWARE** <br>
Raspberry Pi Zero 2W (headless) <br>
Waveshare 3.5" IPS Touch Screen for Raspberry Pi GPIO/SPI
Waveshare 4.2" e-Paper Display*

*The problem with `curses` is that a text-based UI cannot draw on most of e-paper displays as they use `framebuffer` and raw pixel data. A translation layer would need to be built that could efficiently render a command line application such as Zotter on e-paper displays. Drawing a low-level bytemap is impractical as we need partial refresh support to avoid artifacting on e-Paper displays.

**License** <br>
It's a little app. Give credit. Contribute here if you can. GNU Public License v3, anyway, included.
