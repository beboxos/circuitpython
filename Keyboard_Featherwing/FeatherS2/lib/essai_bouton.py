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
import kfw_FeatherS2_board as board
neopix_pin = board.D11
pixels = neopixel.NeoPixel(neopix_pin, 1)
pixels[0] = 0x000000 #turn off neopixel
LCDX=320
LCDY=240
TXMAX=370
TYMAX=370
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
display = adafruit_ili9341.ILI9341(display_bus, width=LCDX, height=LCDY)

try:
    i2c = board.I2C()
except Exception as e:
    print('I2C: Fail,', e)
    all_passed = False
    
def GetTouch(data):
    y=240-int(0.68*((data[0]/10)-16))
    x=int(0.87*((data[1]/10)-16))
    if y<0:
        y=0
    if x<0:
        x=0
    if y>LCDY:
        y=LCDY
    if x>LCDX:
        y=LCDX
    print("X= " + str(x) + ",Y= " + str(y))
    tp = (x,y)
    return tp
"""



"""

import board
import displayio
import terminalio
#import adafruit_touchscreen
from adafruit_button import Button

# use built in display (MagTag, PyPortal, PyGamer, PyBadge, CLUE, etc.)
# see guide for setting up external displays (TFT / OLED breakouts, RGB matrices, etc.)
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/display-and-display-bus
#display = board.DISPLAY

# --| Button Config |-------------------------------------------------
BUTTON_X = 100
BUTTON_Y = 50
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_STYLE = Button.ROUNDRECT
BUTTON_FILL_COLOR = 0x00FFFF
BUTTON_OUTLINE_COLOR = 0xFF00FF
BUTTON_LABEL = "HELLO WORLD"
BUTTON_LABEL_COLOR = 0x000000
# --| Button Config |-------------------------------------------------
ts = tsc2004.TSC2004(i2c)
"""
print('Touch the screen')
try:
    if has_tca2004:
        ts = tsc2004.TSC2004(i2c)
        while not ts.touched:
            pass
    elif has_stmpe610:
        ts = Adafruit_STMPE610_SPI(spi, digitalio.DigitalInOut(touch_cs))
        while ts.buffer_empty:
            pass
    else:
        raise Exception('No touch libraries!')

    print('Touch: Pass,', ts.read_data())
except Exception as e:
    print('Touch: Fail,', e)
    all_passed = False
    
"""
# Setup touchscreen (PyPortal)
#ts = adafruit_touchscreen.Touchscreen(
#    board.TOUCH_XL,
#    board.TOUCH_XR,
#    board.TOUCH_YD,
#    board.TOUCH_YU,
#    calibration=((5200, 59000), (5800, 57000)),
#    size=(480, 320),
#)

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
    #p = ts.touch_point
    p = ts.read_data()
    
    if p:
        y=240-int(0.68*((p[0]/10)-16))
        x=int(0.87*((p[1]/10)-16))
        if y<0:
            y=0
        if x<0:
            x=0
        print("X= " + str(x) + ",Y= " + str(y))
        point = GetTouch(p)
        #tp = (x,y)
        if button.contains(point):
            print("bouton touched")
            button.selected = True
            time.sleep(0.2)
            button.selected = False 
        else:
            print("bouton not touched")
            button.selected = False  # if touch is dragged outside of button
    else:
        button.selected = False  # if touch is released
