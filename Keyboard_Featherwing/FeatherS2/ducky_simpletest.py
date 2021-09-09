# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Dylan Herrada for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
from hid_layout import layout
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
import adafruit_ducky
keyboard = Keyboard(usb_hid.devices)
if layout["lang"]=="fr": 
    from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
    keyboard_layout = KeyboardLayoutFR(keyboard)  # We're in France :)
else:
    from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
    keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :) 

time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems


duck = adafruit_ducky.Ducky("duckyscript.txt", keyboard, keyboard_layout)

result = True
while result is not False:
    result = duck.loop()
