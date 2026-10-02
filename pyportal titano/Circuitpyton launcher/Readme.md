<h1> CircuitPython Launcher For PyPortal Titano </h1>

![Launcher](launcher.png) <br/>

[demo video](https://www.youtube.com/watch?v=-bFsBaRWSHk)

A touch application launcher for CircuitPython. It builds its menu from the `.py` files found at
the root of CIRCUITPY and in `/apps`: 8 apps per page, with **< Prev** / **Next >** buttons when
there are more.

## v2.0 (2026) — CircuitPython 9 / 10

- Apps are started with `supervisor.set_next_code_file()`: each app runs in a fresh interpreter
  (no more `exec(open())`, no more NVM storage, no more 21-character file name limit).
- When an app ends — normally or with an error — the launcher comes back automatically.
  An app can also return to the menu at any time with `supervisor.reload()`.
- Hidden files: `code.py`, `main.py`, `boot.py`, `secrets.py`, `settings.py` and `calculator.py`
  (module of the calculator). Add your own in `settings.toml`:

  ```toml
  LAUNCHER_EXCLUDE = "my_module.py,test.py"
  ```

- Fonts are searched in `/fonts` then `/font`; the built-in font is used if none is found.

## Install

1. Copy the content of this folder to the PyPortal (rename `font/` to `fonts/` or keep it, both work).
2. `pip install circup` then `circup install -r requirements.txt`.
3. Fill in `settings.toml` if your apps need Wi-Fi.

## Included apps

| File | App |
|---|---|
| `titano_calc.py` (+ `calculator.py`) | Touch calculator |
| `light sensor view.py` | Light sensor sparkline graph |

## Ideas for next versions

- Physical buttons navigation (boards without touchscreen)
- Apps on SD card
- Landscape / portrait switch
- App icons (BMP next to the `.py` file)
