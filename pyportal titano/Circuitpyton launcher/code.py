"""
CircuitPython Launcher by BeBoX (c)2021-2026
A simple touch application launcher.
Initially made for Adafruit PyPortal Titano, works on any board
with a resistive touchscreen supported by adafruit_touchscreen
(PyPortal, PyPortal Pynt, PyPortal Titano...).

v2.0 (2026) - CircuitPython 9/10 rewrite
  - apps are started with supervisor.set_next_code_file(): no more
    exec(open()) nor NVM hack, every app runs in a clean interpreter
  - when an app ends (normally or on error) the launcher comes back
  - apps are searched at the root of CIRCUITPY and in /apps
  - Prev / Next page buttons, page indicator
  - exclusion list configurable from settings.toml (LAUNCHER_EXCLUDE)
  - font path fallback (/fonts, /font, or built-in terminalio font)

contact :
email depanet at gmail.com
twitter : https://twitter.com/BeBoXoS
"""
import os
import time
import board
import displayio
import supervisor
import terminalio
import adafruit_touchscreen
from adafruit_display_text.label import Label
from adafruit_button import Button

# --- Settings -------------------------------------------------------------
APP_DIRS = ("/", "/apps")
EXCLUDE = {"code.py", "main.py", "boot.py", "secrets.py", "settings.py",
           "calculator.py"}  # calculator.py is a module of titano_calc.py
# Extra exclusions: LAUNCHER_EXCLUDE = "foo.py,bar.py" in settings.toml
EXCLUDE.update(n.strip() for n in (os.getenv("LAUNCHER_EXCLUDE") or "").split(",") if n.strip())

COLS = 2
ROWS = 4
PER_PAGE = COLS * ROWS
MARGIN = 8
TOP = 44

BLACK = 0x000000
WHITE = 0xFFFFFF
GRAY = 0x666666
ORANGE = 0xFF8800

display = board.DISPLAY
W, H = display.width, display.height


def load_font(name):
    for folder in ("/fonts/", "/font/"):
        try:
            from adafruit_bitmap_font import bitmap_font
            return bitmap_font.load_font(folder + name)
        except (OSError, ImportError):
            pass
    return terminalio.FONT


def find_apps():
    apps = []
    for folder in APP_DIRS:
        try:
            names = os.listdir(folder)
        except OSError:
            continue
        for n in names:
            if n.endswith(".py") and not n.startswith(".") and n not in EXCLUDE:
                apps.append(folder.rstrip("/") + "/" + n)
    return sorted(apps, key=lambda p: p.rsplit("/", 1)[-1].lower())


def launch(path):
    print("Launching", path)
    if hasattr(supervisor, "set_next_code_file"):
        # come back to the launcher when the app ends or crashes
        supervisor.set_next_code_file(path, reload_on_success=True,
                                      reload_on_error=True)
        supervisor.reload()
    else:  # very old CircuitPython fallback
        exec(open(path).read(), {"__name__": "__main__"})


ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)), size=(W, H))

font = load_font("Arial-12.bdf")
title_font = load_font("Arial-Bold-24.bdf")

root = displayio.Group()
bg = displayio.Bitmap(W, H, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = GRAY
root.append(displayio.TileGrid(bg, pixel_shader=bg_palette))
for dx, color in ((0, BLACK), (3, WHITE)):  # drop shadow title
    t = Label(title_font, text="CircuitPython Launcher", color=color,
              anchor_point=(0.5, 0.5), anchored_position=(W // 2 + dx, 20 + dx))
    root.append(t)
page_group = displayio.Group()
root.append(page_group)
display.root_group = root

apps = find_apps()
pages = max(1, (len(apps) + PER_PAGE - 1) // PER_PAGE)
btn_w = (W - MARGIN * (COLS + 1)) // COLS
btn_h = (H - TOP - MARGIN * (ROWS + 2)) // (ROWS + 1)
buttons = []  # (Button, action)


def draw_page(page):
    while len(page_group):
        page_group.pop()
    buttons.clear()
    for i, path in enumerate(apps[page * PER_PAGE:(page + 1) * PER_PAGE]):
        col, row = i % COLS, i // COLS
        b = Button(x=MARGIN + col * (btn_w + MARGIN),
                   y=TOP + MARGIN + row * (btn_h + MARGIN),
                   width=btn_w, height=btn_h,
                   label=path.rsplit("/", 1)[-1][:-3], label_font=font,
                   label_color=BLACK, fill_color=WHITE, style=Button.ROUNDRECT)
        buttons.append((b, path))
    y = TOP + MARGIN + ROWS * (btn_h + MARGIN)
    if not apps:
        page_group.append(Label(font, text="No app found in / or /apps",
                                color=WHITE, x=MARGIN, y=y))
    if pages > 1:
        nav_w = (W - MARGIN * 4) // 3
        for col, label, action in ((0, "< Prev", "prev"), (2, "Next >", "next")):
            buttons.append((Button(x=MARGIN + col * (nav_w + MARGIN), y=y,
                                   width=nav_w, height=btn_h, label=label,
                                   label_font=font, label_color=WHITE,
                                   fill_color=ORANGE, style=Button.ROUNDRECT), action))
        page_group.append(Label(font, text="{}/{}".format(page + 1, pages),
                                color=WHITE, anchor_point=(0.5, 0.5),
                                anchored_position=(W // 2, y + btn_h // 2)))
    for b, _ in buttons:
        page_group.append(b)


page = 0
draw_page(page)
pressed = None
while True:
    point = ts.touch_point
    if point:
        if pressed is None:
            for b, action in buttons:
                if b.contains(point):
                    b.selected = True
                    pressed = (b, action)
                    break
    elif pressed:
        b, action = pressed
        b.selected = False
        pressed = None
        if action == "next":
            page = (page + 1) % pages
            draw_page(page)
        elif action == "prev":
            page = (page - 1) % pages
            draw_page(page)
        else:
            launch(action)
    time.sleep(0.02)
