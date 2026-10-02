"""
Keyboard FeatherWing (FeatherS2) boot menu by BeBoX - v2.0 (2026)

Lists the .py files at the root of CIRCUITPY. The joystick up/down moves the
selection, the stick button launches.

v2.0: apps are started with supervisor.set_next_code_file() via
bebox_common.launcher - no more NVM storage nor exec(open()). When the
launched app ends (normally or with an error), this menu comes back.
"""
import time
import kfw_FeatherS2_board as board
import adafruit_ili9341
import displayio
import bbq10keyboard
import neopixel
from bebox_common.launcher import find_apps, launch
try:
    from fourwire import FourWire  # CircuitPython 9+
except ImportError:
    from displayio import FourWire  # CircuitPython 8

# --- display ---
displayio.release_displays()
spi = board.SPI()
display_bus = FourWire(spi, command=board.D10, chip_select=board.D9)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

# --- keyboard + neopixel ---
i2c = board.I2C()
kbd = bbq10keyboard.BBQ10Keyboard(i2c)
pixels = neopixel.NeoPixel(board.D11, 1)
pixels[0] = 0x000000

MAXLINES = 16
MAXCOLS = 49
PER_PAGE = 14

# joystick key codes reported by the BBQ10 keyboard
KEY_UP, KEY_DOWN, KEY_FIRE = "\x01", "\x02", "\x05"


def clearscreen():
    print("\r\n" * MAXLINES)


apps = find_apps()
print("Debug :", len(apps), "files")
index = 0


def drawmenu(index):
    clearscreen()
    pad = (MAXCOLS - 28) // 2
    print("*" * pad + " SELECT APPLICATION TO RUN " + "*" * pad)
    print("-" * (MAXCOLS - 2))
    page = index // PER_PAGE
    for count, path in enumerate(apps):
        if page * PER_PAGE <= count < page * PER_PAGE + PER_PAGE:
            name = path.rsplit("/", 1)[-1][:MAXCOLS - 2]
            print(("* " if count == index else "  ") + name)


def read_key():
    while kbd.key_count < 2:
        pass
    return kbd.keys[0][1]


if not apps:
    clearscreen()
    print("No app found at the root of CIRCUITPY.")
    while True:
        time.sleep(1)

drawmenu(index)
selected = False
while not selected:
    key = read_key()
    if key == KEY_UP and index > 0:
        index -= 1
        drawmenu(index)
    elif key == KEY_DOWN and index < len(apps) - 1:
        index += 1
        drawmenu(index)
    elif key == KEY_FIRE:
        selected = True
    time.sleep(0.1)

clearscreen()
print("Launching :", apps[index])
time.sleep(0.5)
launch(apps[index])
