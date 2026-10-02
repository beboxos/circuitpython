"""
MagTag Boot App Selector by BeBoX - v2.0 (2026)

Lists the .py files at the root of CIRCUITPY on the e-ink display; the four
buttons pick an app (D11..D14) with the last one as "Next page".

v2.0: apps are started with supervisor.set_next_code_file() via
bebox_common.launcher - no more NVM storage nor exec(open()). When the
launched app ends, this menu comes back. Hold button A (D15) at boot while
an app is set to force a return to this menu (handled natively now: any app
simply reloads into code.py when it ends).
"""
import time
import board
from adafruit_magtag.magtag import MagTag
from bebox_common.launcher import find_apps

magtag = MagTag(rotation=180)
BACKGROUND_BMP = "/bmps/fourboxesv_bg.bmp"
try:
    magtag.graphics.set_background(BACKGROUND_BMP)
except (OSError, ValueError):
    pass

# four text slots down the screen
x, y, step = 5, 35, 73
for n in range(4):
    magtag.add_text(text_position=(x, y + n * step), text_scale=1)
    magtag.set_text(" ", n, False)

apps = find_apps()
print("Found", len(apps), "apps")
PER_PAGE = 3
pages = max(1, (len(apps) + PER_PAGE - 1) // PER_PAGE)


def show(page):
    for slot in range(PER_PAGE):
        idx = page * PER_PAGE + slot
        if idx < len(apps):
            magtag.set_text(apps[idx].rsplit("/", 1)[-1][:-3], slot, False)
        else:
            magtag.set_text(" ", slot, False)
    magtag.set_text("Next >>>" if pages > 1 else " ", 3, False)
    magtag.refresh()


page = 0
show(page)
while True:
    for i, b in enumerate(magtag.peripherals.buttons):
        if not b.value:
            if i < 3:  # launch the app in this slot
                idx = page * PER_PAGE + i
                if idx < len(apps):
                    magtag.peripherals.neopixels[3 - i] = (0, 0, 20)
                    print("Launching", apps[idx])
                    time.sleep(0.5)
                    from bebox_common.launcher import launch
                    launch(apps[idx])
            else:  # next page
                magtag.peripherals.neopixels[3 - i] = (0, 20, 0)
                page = (page + 1) % pages
                show(page)
            time.sleep(0.4)
            magtag.peripherals.neopixels[3 - i] = (0, 0, 0)
    time.sleep(0.1)
