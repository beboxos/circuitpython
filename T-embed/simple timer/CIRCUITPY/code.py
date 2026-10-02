"""
Simple kitchen timer for LilyGO T-Embed (ESP32-S3) - BeBoX
v2.0 (2026) - CircuitPython 9/10 rewrite

Controls
  - turn the knob     : set the time (15 s steps, up to 99 min)
  - press             : start / pause / resume
  - long press (1 s)  : cancel and go back to setting mode
When time is up: 3 beeps + LED flash, then back to setting mode
with the last value.

The 7 LEDs ring and the bar at the bottom of the screen show the
remaining time.
"""
import array
import math
import time

import board
import digitalio
import displayio
import rotaryio
import terminalio
import audiobusio
import audiocore
import adafruit_dotstar
from adafruit_display_text import label

STEP = 15            # seconds per encoder click
MAX_TIME = 99 * 60
LONG_PRESS = 1.0     # seconds
NUM_LEDS = 7
LED_COLOR = (0, 40, 255)
BRIGHTNESS = 0.1     # dotstar brightness is 0.0 .. 1.0

# --- Power (needed on battery for display, LEDs and audio) ---------------
try:
    power = digitalio.DigitalInOut(board.IO46)
    power.switch_to_output(value=True)
except (AttributeError, ValueError):
    pass

# --- Display --------------------------------------------------------------
display = getattr(board, "DISPLAY", None)
if display is None:  # board definition without built-in display
    import busio
    from adafruit_st7789 import ST7789
    try:
        from fourwire import FourWire  # CircuitPython 9+
    except ImportError:
        from displayio import FourWire  # CircuitPython 8
    displayio.release_displays()
    spi = busio.SPI(board.IO12, board.IO11)
    bus = FourWire(spi, command=board.IO13, chip_select=board.IO10,
                   reset=board.IO9, baudrate=24_000_000)
    display = ST7789(bus, width=320, height=170, backlight_pin=board.IO15,
                     rotation=90, rowstart=0, colstart=35)

W, H = display.width, display.height
screen = displayio.Group()
display.root_group = screen

time_label = label.Label(terminalio.FONT, text="01:00", color=0xFFFFFF, scale=5,
                         anchor_point=(0.5, 0.5), anchored_position=(W // 2, H // 2 - 10))
status_label = label.Label(terminalio.FONT, text="SET", color=0x00AAFF, scale=2,
                           anchor_point=(0.5, 0.0), anchored_position=(W // 2, 6))
screen.append(time_label)
screen.append(status_label)

BAR_H = 10
bar_bitmap = displayio.Bitmap(W - 20, BAR_H, 2)
bar_palette = displayio.Palette(2)
bar_palette[0] = 0x202020
bar_palette[1] = 0x00AAFF
screen.append(displayio.TileGrid(bar_bitmap, pixel_shader=bar_palette, x=10, y=H - BAR_H - 10))

# --- Inputs / outputs -----------------------------------------------------
encoder = rotaryio.IncrementalEncoder(board.IO1, board.IO2)
button = digitalio.DigitalInOut(board.IO0)
button.switch_to_input(pull=digitalio.Pull.UP)
leds = adafruit_dotstar.DotStar(board.IO45, board.IO42, NUM_LEDS,
                                brightness=BRIGHTNESS, auto_write=False)

SAMPLE_RATE = 8000
FREQ = 880
wave = array.array("H", [int((math.sin(2 * math.pi * i * FREQ / SAMPLE_RATE) + 1) * 32767)
                         for i in range(SAMPLE_RATE // FREQ)])
beep_sample = audiocore.RawSample(wave, sample_rate=SAMPLE_RATE)
audio = audiobusio.I2SOut(board.IO7, board.IO5, board.IO6)


def fmt(seconds):
    return "{:02d}:{:02d}".format(seconds // 60, seconds % 60)


def show_progress(fraction):
    """fraction 1.0 = full, 0.0 = empty. Updates bar + LED ring."""
    fraction = max(0.0, min(1.0, fraction))
    filled = int(bar_bitmap.width * fraction)
    for x in range(bar_bitmap.width):
        v = 1 if x < filled else 0
        if bar_bitmap[x, 0] != v:
            for y in range(BAR_H):
                bar_bitmap[x, y] = v
    lit = fraction * NUM_LEDS
    for i in range(NUM_LEDS):
        level = max(0.0, min(1.0, lit - i))
        leds[i] = tuple(int(c * level) for c in LED_COLOR)
    leds.show()


def read_button():
    """Return None, 'short' or 'long' (long fires while still held)."""
    if button.value:  # released
        return None
    start = time.monotonic()
    while not button.value:
        if time.monotonic() - start >= LONG_PRESS:
            while not button.value:  # wait for release
                time.sleep(0.01)
            return "long"
        time.sleep(0.01)
    return "short"


def alarm(count=3):
    status_label.text = "TIME'S UP"
    for _ in range(count):
        time_label.text = "00:00"
        leds.fill((255, 255, 255))
        leds.show()
        audio.play(beep_sample, loop=True)
        time.sleep(0.4)
        audio.stop()
        leds.fill(0)
        leds.show()
        time_label.text = ""
        time.sleep(0.4)


def set_mode(seconds):
    status_label.text = "SET"
    status_label.color = 0x00AAFF
    encoder.position = seconds // STEP
    last = None
    while True:
        pos = max(1, min(MAX_TIME // STEP, encoder.position))
        if pos != encoder.position:
            encoder.position = pos
        if pos != last:
            last = pos
            time_label.text = fmt(pos * STEP)
            show_progress(pos * STEP / MAX_TIME)
        if read_button():
            return pos * STEP
        time.sleep(0.02)


def run_mode(total):
    """Count down `total` seconds. Return True when finished, False if cancelled."""
    status_label.text = "RUN"
    status_label.color = 0x00FF00
    end = time.monotonic() + total
    paused_left = None
    while True:
        now = time.monotonic()
        left = paused_left if paused_left is not None else max(0.0, end - now)
        if paused_left is None:
            time_label.text = fmt(int(math.ceil(left)))
            show_progress(left / total)
            if left <= 0:
                return True
        else:  # blink while paused
            time_label.text = fmt(int(math.ceil(left))) if int(now * 2) % 2 else ""
        press = read_button()
        if press == "long":
            return False
        if press == "short":
            if paused_left is None:
                paused_left = left
                status_label.text = "PAUSE"
                status_label.color = 0xFF8800
            else:
                end = time.monotonic() + paused_left
                paused_left = None
                status_label.text = "RUN"
                status_label.color = 0x00FF00
        time.sleep(0.05)


duration = 60
while True:
    duration = set_mode(duration)
    if run_mode(duration):
        alarm()
