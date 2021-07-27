# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
Simple button example.
"""
from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
import adafruit_ili9341
import adafruit_sdcard
import digitalio
import displayio
import neopixel
import storage
import analogio
import time
import os
import board


# Touch Libraries
has_stmpe610 = True
try:
    from adafruit_stmpe610 import Adafruit_STMPE610_SPI
except:
    has_stmpe610 = False

has_tca2004 = True
try:
    import tsc2004
except:
    has_tca2004 = False

# Optional Pico Adapter
#try:
#    import kfw_pico_board as board
#except:
#    import board


# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
touch_cs = board.D6
sd_cs = board.D5
neopix_pin = board.D11

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

try:
    i2c = board.I2C()
except Exception as e:
    print('I2C: Fail,', e)
    all_passed = False


"""
---------------------------------------------------------------------------------------
"""
import board
import displayio
import terminalio
import adafruit_touchscreen
from adafruit_button import Button

# use built in display (MagTag, PyPortal, PyGamer, PyBadge, CLUE, etc.)
# see guide for setting up external displays (TFT / OLED breakouts, RGB matrices, etc.)
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/display-and-display-bus
#display = board.DISPLAY

# --| Button Config |-------------------------------------------------
BUTTON_X = 110
BUTTON_Y = 95
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_STYLE = Button.ROUNDRECT
BUTTON_FILL_COLOR = 0x00FFFF
BUTTON_OUTLINE_COLOR = 0xFF00FF
BUTTON_LABEL = "HELLO WORLD"
BUTTON_LABEL_COLOR = 0x000000
# --| Button Config |-------------------------------------------------

# Setup touchscreen (PyPortal)
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((5200, 59000), (5800, 57000)),
    size=(320, 240),
)

# Make the display context
splash = displayio.Group()
display.show(splash)

# Make the button
button = Button(
    x=BUTTON_X,
    y=BUTTON_Y,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    style=BUTTON_STYLE,
    fill_color=BUTTON_FILL_COLOR,
    outline_color=BUTTON_OUTLINE_COLOR,
    label=BUTTON_LABEL,
    label_font=terminalio.FONT,
    label_color=BUTTON_LABEL_COLOR,
)

# Add button to the display context
splash.append(button)

# Loop and look for touches
while True:
    p = ts.touch_point
    
    if p:
        print(p)
        if button.contains(p):
            button.selected = True
        else:
            button.selected = False  # if touch is dragged outside of button
    else:
        button.selected = False  # if touch is released
