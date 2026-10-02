# LilyGO T-Embed (ESP32-S3)

The [T-Embed](https://www.lilygo.cc/products/t-embed) is an ESP32-S3 board with a 1.9" 320×170
ST7789 screen, a rotary encoder with push button, a ring of 7 APA102 LEDs and an I2S speaker.

## Simple timer

`simple timer/CIRCUITPY/` is a kitchen timer:

| Action | Effect |
|---|---|
| Turn the knob | Set the time (15 s steps, up to 99 min) |
| Press | Start / pause / resume |
| Long press (1 s) | Cancel, back to setting mode |

When the time is up: 3 beeps and the LEDs flash. The LED ring and the bar at the bottom of the
screen show the remaining time.

### Install (CircuitPython 9 / 10)

1. Flash the **"LILYGO T-Embed ESP32-S3"** CircuitPython build from
   [circuitpython.org](https://circuitpython.org/downloads).
2. Copy the content of `simple timer/CIRCUITPY/` to the board.
3. `pip install circup` then `circup install -r requirements.txt`.

`code.py` uses the built-in `board.DISPLAY` when the firmware provides it and initializes the
ST7789 itself otherwise (`boot.py` does the same for older firmwares, so the console shows up on
screen at boot).

## Multi-tool

`multi tool/CIRCUITPY/` is a menu of time tools in a single file:

| Tool | What it does |
|---|---|
| Timer | Countdown with pause/resume, LED ring + beeps |
| Stopwatch | Count up, press = start/stop, long press = reset |
| Pomodoro | 25 min work / 5 min break cycles |
| Clock | HH:MM:SS, set over Wi-Fi/NTP when `settings.toml` has Wi-Fi |

Controls everywhere: **turn** the knob to move/adjust, **press** to select/start/pause,
**long press (1 s)** to go back to the menu. Install the libraries with
`circup install -r requirements.txt`; add `CIRCUITPY_WIFI_SSID` / `CIRCUITPY_WIFI_PASSWORD`
(and optional `TZ_OFFSET`) to `settings.toml` for the NTP clock.
