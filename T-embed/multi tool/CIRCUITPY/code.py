"""
T-Embed Multi-Tool by BeBoX - 2026 (CircuitPython 9/10)

A small menu of time tools for the LilyGO T-Embed (ESP32-S3):

    Timer      countdown with pause/resume, LED ring + bar, beeps
    Stopwatch  count up, press = start/stop, long press = reset
    Pomodoro   25 min work / 5 min break cycles with beeps
    Clock      HH:MM:SS, set over Wi-Fi/NTP when settings.toml has Wi-Fi

Controls everywhere:
    turn knob        move / adjust
    press            select / start / pause
    long press (1 s) back to the menu (or the action named by the app)
"""
import time
import math
import array
import board
import digitalio
import displayio
import rotaryio
import terminalio
import audiobusio
import audiocore
import adafruit_dotstar
from adafruit_display_text import label

LONG_PRESS = 1.0
NUM_LEDS = 7
BRIGHTNESS = 0.1

# --- power rail (battery) ---
try:
    _power = digitalio.DigitalInOut(board.IO46)
    _power.switch_to_output(value=True)
except (AttributeError, ValueError):
    pass

# --- display ---
display = getattr(board, "DISPLAY", None)
if display is None:
    import busio
    from adafruit_st7789 import ST7789
    try:
        from fourwire import FourWire
    except ImportError:
        from displayio import FourWire
    displayio.release_displays()
    spi = busio.SPI(board.IO12, board.IO11)
    bus = FourWire(spi, command=board.IO13, chip_select=board.IO10,
                   reset=board.IO9, baudrate=24_000_000)
    display = ST7789(bus, width=320, height=170, backlight_pin=board.IO15,
                     rotation=90, rowstart=0, colstart=35)
W, H = display.width, display.height

screen = displayio.Group()
display.root_group = screen
title = label.Label(terminalio.FONT, text="", color=0x00AAFF, scale=2,
                    anchor_point=(0.5, 0.0), anchored_position=(W // 2, 6))
big = label.Label(terminalio.FONT, text="", color=0xFFFFFF, scale=5,
                  anchor_point=(0.5, 0.5), anchored_position=(W // 2, H // 2))
hint = label.Label(terminalio.FONT, text="", color=0x888888, scale=1,
                   anchor_point=(0.5, 1.0), anchored_position=(W // 2, H - 6))
for item in (title, big, hint):
    screen.append(item)

# --- inputs / outputs ---
encoder = rotaryio.IncrementalEncoder(board.IO1, board.IO2)
button = digitalio.DigitalInOut(board.IO0)
button.switch_to_input(pull=digitalio.Pull.UP)
leds = adafruit_dotstar.DotStar(board.IO45, board.IO42, NUM_LEDS,
                                brightness=BRIGHTNESS, auto_write=False)

SAMPLE_RATE = 8000
_wave_cache = {}


def _tone(freq):
    if freq not in _wave_cache:
        length = SAMPLE_RATE // freq
        wave = array.array("H", [int((math.sin(2 * math.pi * i / length) + 1)
                                     * 32767) for i in range(length)])
        _wave_cache[freq] = audiocore.RawSample(wave, sample_rate=SAMPLE_RATE)
    return _wave_cache[freq]


_audio = audiobusio.I2SOut(board.IO7, board.IO5, board.IO6)


def beep(freq=880, ms=150):
    _audio.play(_tone(freq), loop=True)
    time.sleep(ms / 1000.0)
    _audio.stop()


def fmt(seconds):
    seconds = int(seconds)
    if seconds >= 3600:
        return "{:d}:{:02d}:{:02d}".format(seconds // 3600,
                                           (seconds % 3600) // 60, seconds % 60)
    return "{:02d}:{:02d}".format(seconds // 60, seconds % 60)


def ring(fraction, color=(0, 40, 255)):
    fraction = max(0.0, min(1.0, fraction))
    lit = fraction * NUM_LEDS
    for i in range(NUM_LEDS):
        level = max(0.0, min(1.0, lit - i))
        leds[i] = tuple(int(c * level) for c in color)
    leds.show()


def read_button():
    """None, 'short' or 'long' (long fires while still held, then waits)."""
    if button.value:
        return None
    start = time.monotonic()
    while not button.value:
        if time.monotonic() - start >= LONG_PRESS:
            while not button.value:
                time.sleep(0.01)
            return "long"
        time.sleep(0.01)
    return "short"


# ============================================================
# Apps - each returns when the user long-presses (back to menu)
# ============================================================

def app_timer():
    title.text = "TIMER"
    step = 15
    seconds = 60
    encoder.position = seconds // step
    # set phase
    while True:
        pos = max(1, min(99 * 60 // step, encoder.position))
        if pos != encoder.position:
            encoder.position = pos
        seconds = pos * step
        big.text = fmt(seconds)
        hint.text = "turn=set  press=start  hold=menu"
        ring(seconds / (99 * 60))
        b = read_button()
        if b == "long":
            return
        if b == "short":
            break
    # run phase
    end = time.monotonic() + seconds
    paused = None
    while True:
        left = paused if paused is not None else max(0.0, end - time.monotonic())
        if paused is None:
            big.text = fmt(math.ceil(left))
            ring(left / seconds)
            hint.text = "press=pause  hold=menu"
            if left <= 0:
                break
        else:
            big.text = fmt(math.ceil(left)) if int(time.monotonic() * 2) % 2 else ""
            hint.text = "PAUSED  press=resume"
        b = read_button()
        if b == "long":
            leds.fill(0)
            leds.show()
            return
        if b == "short":
            if paused is None:
                paused = left
            else:
                end = time.monotonic() + paused
                paused = None
        time.sleep(0.03)
    for _ in range(3):
        leds.fill((255, 255, 255))
        leds.show()
        beep(880, 300)
        leds.fill(0)
        leds.show()
        time.sleep(0.2)


def app_stopwatch():
    title.text = "STOPWATCH"
    elapsed = 0.0
    running = False
    start = 0.0
    while True:
        now = elapsed + (time.monotonic() - start if running else 0)
        big.text = fmt(now)
        hint.text = ("press=stop  hold=menu" if running
                     else "press=start  hold=reset/menu")
        ring((now % 60) / 60.0, (0, 255, 80))
        b = read_button()
        if b == "short":
            if running:
                elapsed = now
                running = False
            else:
                start = time.monotonic()
                running = True
        elif b == "long":
            if running:
                return
            if now > 0:          # first long press resets
                elapsed = 0.0
            else:                # second (already zero) returns
                return
        time.sleep(0.03)


def app_pomodoro():
    title.text = "POMODORO"
    phases = [("WORK", 25 * 60, (255, 60, 0)), ("BREAK", 5 * 60, (0, 180, 255))]
    idx = 0
    while True:
        name, duration, color = phases[idx]
        end = time.monotonic() + duration
        while True:
            left = max(0.0, end - time.monotonic())
            big.text = fmt(math.ceil(left))
            hint.text = name + "  hold=menu"
            ring(left / duration, color)
            if left <= 0:
                break
            if read_button() == "long":
                leds.fill(0)
                leds.show()
                return
            time.sleep(0.05)
        beep(660 if name == "WORK" else 990, 400)
        idx = (idx + 1) % len(phases)


def app_clock():
    title.text = "CLOCK"
    synced = _ntp_sync()
    while True:
        t = time.localtime()
        big.text = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
        hint.text = ("NTP synced  hold=menu" if synced
                     else "no Wi-Fi  hold=menu")
        ring(t.tm_sec / 60.0, (120, 120, 120))
        if read_button() == "long":
            return
        time.sleep(0.1)


def _ntp_sync():
    try:
        import os
        import wifi
        import socketpool
        import rtc
        import adafruit_ntp
        ssid = os.getenv("CIRCUITPY_WIFI_SSID")
        if not ssid:
            return False
        wifi.radio.connect(ssid, os.getenv("CIRCUITPY_WIFI_PASSWORD"))
        pool = socketpool.SocketPool(wifi.radio)
        tz = int(os.getenv("TZ_OFFSET") or 0)
        ntp = adafruit_ntp.NTP(pool, tz_offset=tz)
        rtc.RTC().datetime = ntp.datetime
        return True
    except Exception:
        return False


# ============================================================
# Menu
# ============================================================

APPS = [("Timer", app_timer), ("Stopwatch", app_stopwatch),
        ("Pomodoro", app_pomodoro), ("Clock", app_clock)]


def menu():
    big.scale = 3
    encoder.position = 0
    last = None
    while True:
        sel = encoder.position % len(APPS)
        if sel != last:
            last = sel
            title.text = "T-EMBED"
            big.text = APPS[sel][0]
            hint.text = "turn=choose  press=open"
            ring((sel + 1) / len(APPS))
        b = read_button()
        if b == "short":
            big.scale = 5
            APPS[sel][1]()
            big.scale = 3
            last = None  # force redraw
            encoder.position = sel
        time.sleep(0.03)


menu()
