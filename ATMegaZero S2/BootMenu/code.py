"""
ATMegaZero S2 boot menu by BeBoX - v2.0 (2026)

Lists the .py files at the root of CIRCUITPY on the MiniPiTFT and the serial
console. Two buttons move the selection; press both to launch.

v2.0: apps are started with supervisor.set_next_code_file() via
bebox_common.launcher - no more NVM storage nor exec(open()). When the
launched app ends (normally or with an error), this menu comes back.
"""
try:
    from fourwire import FourWire  # CircuitPython 9+
except ImportError:
    from displayio import FourWire  # CircuitPython 8
from adafruit_st7789 import ST7789
import board
import displayio
import digitalio
import time
from bebox_common.launcher import find_apps, launch

# --- display (MiniPiTFT 1.13" 240x135) ---
displayio.release_displays()
spi = board.SPI()
while not spi.try_lock():
    spi.configure(baudrate=32000000)
spi.unlock()
display_bus = FourWire(spi, command=board.IO7, chip_select=board.IO38,
                       reset=board.IO0, baudrate=32000000, polarity=1, phase=1)
display = ST7789(display_bus, width=240, height=135, rotation=270,
                 rowstart=40, colstart=53)

# --- buttons ---
button1 = digitalio.DigitalInOut(board.IO4)
button1.switch_to_input(pull=digitalio.Pull.DOWN)
button2 = digitalio.DigitalInOut(board.IO2)
button2.switch_to_input(pull=digitalio.Pull.DOWN)

MAXLINES = 10
MAXCOLS = 37
PER_PAGE = 7


def clearscreen():
    print("\r\n" * MAXLINES)


apps = find_apps()
print("Debug :", len(apps), "files")
index = 0


def draw(index):
    clearscreen()
    print("**** SELECT APPLICATION TO RUN *****")
    print("-" * (MAXCOLS - 1))
    page = index // PER_PAGE
    for count, path in enumerate(apps):
        if page * PER_PAGE <= count < page * PER_PAGE + PER_PAGE:
            name = path.rsplit("/", 1)[-1][:-3]
            print(("* " if count == index else "  ") + name[:35])


if not apps:
    clearscreen()
    print("No app found at the root of CIRCUITPY.")
    while True:
        time.sleep(1)

draw(index)
selected = False
while not selected:
    if button1.value and not button2.value:          # down
        while not button2.value:
            pass
        if index < len(apps) - 1:
            index += 1
            draw(index)
    if not button1.value and button2.value:          # up
        while not button1.value:
            pass
        if index > 0:
            index -= 1
            draw(index)
    if not button1.value and not button2.value:      # both = launch
        selected = True
    time.sleep(0.1)

clearscreen()
print("Launching :", apps[index])
time.sleep(0.5)
launch(apps[index])
