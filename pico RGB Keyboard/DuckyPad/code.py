"""
Ducky Pad by BeBoX
vers 10.09.2021
transform pico RGB keybpad in multi Rubber ducky HID script
"""
from rgbkeypad import RgbKeypad
import time
import os
from hid_layout import layout
import usb_hid
from adafruit_hid.keyboard import Keyboard
import ducky_bebox as adafruit_ducky  # BeBoX version: single command mode + ALTGR
keyboard = Keyboard(usb_hid.devices)
if layout["lang"]=="fr": 
    from keyboard_layout_fr import KeyboardLayoutFR
    keyboard_layout = KeyboardLayoutFR(keyboard)  # We're in France :)
else:
    from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
    keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
keypad = RgbKeypad()
keys = keypad.keys
def execute(file):
    duck = adafruit_ducky.Ducky("/ducky/"+file+".txt", keyboard, keyboard_layout)
    result = True
    while result is not False:
        result = duck.loop()
    time.sleep(0.5)
    keypad.clear_all()

# key n (0..15) runs /ducky/<hex digit>.txt  (0.txt .. F.txt)
SCRIPTS = "0123456789ABCDEF"
IDLE = (0, 0, 20)
while True:
    keys[0].set_led(*IDLE)  # heartbeat
    keypad.update()
    for n, key in enumerate(keys):
        if key.pressed:
            key.set_led(255, 0, 0)
            execute(SCRIPTS[n])
            key.set_led(0, 0, 0)
    time.sleep(0.2)
    keys[0].set_led(0, 0, 0)
    time.sleep(0.2)
