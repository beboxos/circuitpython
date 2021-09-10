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
import adafruit_ducky
keyboard = Keyboard(usb_hid.devices)
if layout["lang"]=="fr": 
    from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
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

while True:
    keys[0].set_led(0, 0, 20)
    keypad.update()
    if keys[0].pressed:
        keys[0].set_led(255, 0, 0)
        execute("0")
        keys[0].set_led(0, 0, 0)
    if keys[1].pressed:
        keys[1].set_led(255, 0, 0)
        execute("1")
        keys[1].set_led(0, 0, 0)
    if keys[2].pressed:
        keys[2].set_led(255, 0, 0)
        execute("2")
        keys[2].set_led(0, 0, 0)
    if keys[3].pressed:
        keys[3].set_led(255, 0, 0)
        execute("3")
        keys[3].set_led(0, 0, 0)
    if keys[4].pressed:
        keys[4].set_led(255, 0, 0)
        execute("4")
        keys[4].set_led(0, 0, 0)
    if keys[5].pressed:
        keys[5].set_led(255, 0, 0)
        execute("5")
        keys[5].set_led(0, 0, 0)
    if keys[6].pressed:
        keys[6].set_led(255, 0, 0)
        execute("6")
        keys[6].set_led(0, 0, 0)
    if keys[7].pressed:
        keys[7].set_led(255, 0, 0)
        execute("7")
        keys[7].set_led(0, 0, 0)
    if keys[8].pressed:
        keys[8].set_led(255, 0, 0)
        execute("8")
        keys[8].set_led(0, 0, 0)
    if keys[9].pressed:
        keys[9].set_led(255, 0, 0)
        execute("9")
        keys[9].set_led(0, 0, 0)
    if keys[10].pressed:
        keys[10].set_led(255, 0, 0)
        execute("A")
        keys[10].set_led(0, 0, 0)
    if keys[11].pressed:
        keys[11].set_led(255, 0, 0)
        execute("B")
        keys[11].set_led(0, 0, 0)
    if keys[12].pressed:
        keys[12].set_led(255, 0, 0)
        execute("C")
        keys[12].set_led(0, 0, 0)
    if keys[13].pressed:
        keys[13].set_led(255, 0, 0)
        execute("D")
        keys[13].set_led(0, 0, 0)
    if keys[14].pressed:
        keys[14].set_led(255, 0, 0)
        execute("E")
        keys[14].set_led(0, 0, 0)
    if keys[15].pressed:
        keys[15].set_led(255, 0, 0)
        execute("F")
        keys[15].set_led(0, 0, 0)
    time.sleep(0.2)
    keys[0].set_led(0, 0, 0)
    time.sleep(0.2)
