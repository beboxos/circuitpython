"""
DuckyPad by BeBoX - v2.0 (2026)

Turns the Pimoroni Pico RGB Keypad into a multi-page macro pad.

  - The bottom-right key (15) is the PAGE key: tap it to cycle pages.
    Each page has its own LED color.
  - Keys 0..14 run that page's DuckyScript file, or send a media key on
    the built-in MEDIA page.

Pages come from /ducky:
  - /ducky/1/0.txt .. /ducky/1/E.txt   (page 1), /ducky/2/...  (page 2), ...
  - if there are no numbered sub-folders, the flat /ducky/0.txt .. E.txt is
    used as page 1 (keeps old layouts working).
  - a MEDIA page is always added last (volume / play / track keys).

Edit hid_layout.py to choose the keyboard layout ("fr" AZERTY / "us").

Only use HID scripts on computers you own or are allowed to use.
"""
import os
import time
import usb_hid
from rgbkeypad import RgbKeypad
from hid_layout import layout
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import ducky_bebox as adafruit_ducky  # BeBoX: single-command mode + ALTGR

keyboard = Keyboard(usb_hid.devices)
if layout["lang"] == "fr":
    from keyboard_layout_fr import KeyboardLayoutFR
    keyboard_layout = KeyboardLayoutFR(keyboard)
else:
    from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
    keyboard_layout = KeyboardLayoutUS(keyboard)
consumer = ConsumerControl(usb_hid.devices)

keypad = RgbKeypad()
keys = keypad.keys

PAGE_KEY = 15               # bottom-right key cycles pages
SCRIPTS = "0123456789ABCDE"  # files run by keys 0..14
PAGE_COLORS = [(0, 0, 40), (0, 40, 0), (40, 0, 0), (40, 40, 0),
               (40, 0, 40), (0, 40, 40)]
MEDIA_COLOR = (40, 20, 0)

# Media keys mapped to keys 0..6 on the MEDIA page
MEDIA = [
    ("Vol-", ConsumerControlCode.VOLUME_DECREMENT),
    ("Vol+", ConsumerControlCode.VOLUME_INCREMENT),
    ("Mute", ConsumerControlCode.MUTE),
    ("Play", ConsumerControlCode.PLAY_PAUSE),
    ("Next", ConsumerControlCode.SCAN_NEXT_TRACK),
    ("Prev", ConsumerControlCode.SCAN_PREVIOUS_TRACK),
    ("Stop", ConsumerControlCode.STOP),
]


def _discover_pages():
    """Return a list of page specs: a folder path, or the string 'MEDIA'."""
    pages = []
    try:
        entries = sorted(os.listdir("/ducky"))
    except OSError:
        entries = []
    for name in entries:
        full = "/ducky/" + name
        try:
            if os.stat(full)[0] & 0x4000:  # is a directory
                pages.append(full)
        except OSError:
            pass
    if not pages:              # no sub-folders: flat /ducky is page 1
        pages.append("/ducky")
    pages.append("MEDIA")
    return pages


PAGES = _discover_pages()


def run_script(folder, name):
    path = folder + "/" + name + ".txt"
    try:
        duck = adafruit_ducky.Ducky(path, keyboard, keyboard_layout)
    except OSError:
        return
    result = True
    while result is not False:
        result = duck.loop()


def show_page(page):
    spec = PAGES[page]
    if spec == "MEDIA":
        for n, key in enumerate(keys):
            key.set_led(*(MEDIA_COLOR if n < len(MEDIA) else (0, 0, 0)))
    else:
        color = PAGE_COLORS[page % len(PAGE_COLORS)]
        for n, key in enumerate(keys):
            key.set_led(*(color if n < len(SCRIPTS) else (0, 0, 0)))
    keys[PAGE_KEY].set_led(80, 80, 80)  # the page key is always lit white


page = 0
show_page(page)
while True:
    keypad.update()
    for n, key in enumerate(keys):
        if not key.pressed:
            continue
        if n == PAGE_KEY:
            page = (page + 1) % len(PAGES)
            show_page(page)
            time.sleep(0.25)
            break
        key.set_led(255, 0, 0)
        spec = PAGES[page]
        if spec == "MEDIA":
            if n < len(MEDIA):
                consumer.send(MEDIA[n][1])
        elif n < len(SCRIPTS):
            run_script(spec, SCRIPTS[n])
        time.sleep(0.2)
        show_page(page)
        break
    time.sleep(0.02)
