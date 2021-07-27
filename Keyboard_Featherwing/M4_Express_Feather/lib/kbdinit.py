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