# Zotter
Zotter is a note-taking app that syncs with Zotero. It is designed to run on a homebrew e-paper typewriter, or a cyberdeck, or any device that you can take into a library and take notes on without getting distracted by a web browser.

<pre>
      .zzzz.__
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
  ,'        |  zotter v1
 (_`'---._ /--,
   `'---._`'---..__
by sid    `''''--, )
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
Raspberry Pi Zero 2W <br>
Waveshare 3.5" IPS Touch Screen for Raspberry Pi GPIO/SPI <br>
Waveshare 4.2" e-Paper Display*

*The problem with `curses` is that a text-based UI cannot draw on most of e-paper displays as they use `framebuffer` and raw pixel data. A translation layer would need to be built that could efficiently render a command line application such as Zotter on e-paper displays. Drawing a low-level bytemap is impractical as we need partial refresh support to avoid artifacting on e-Paper displays.

# Hardware and Design
Below are mock ups for a prototype product. It is a mechanical keyboard in which Zotter is built into a 'lift over and up' style transparent cover. A wireframe hinge is used for threading wires into the keyboard where there is space for the battery. Friction from the rubber gasket makes the device stay up without need for expensive hinges. A USB-C port is exposed at the back of the keyboard and when plugged the keyboard can be used with any device as a standard USB keyboard. Total cost of device can be as less as $75.

<img src="https://github.com/user-attachments/assets/07429431-ae45-4866-aeb2-33fa98fa928e" alt="28EBC4FB" width="400" />
<img src="https://github.com/user-attachments/assets/ec56edfa-0fb9-493a-9750-858a373c59a9" alt="539A4C38" width="400" />


