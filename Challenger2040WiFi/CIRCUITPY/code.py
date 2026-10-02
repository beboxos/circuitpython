"""
Challenger RP2040 WiFi demo - BeBoX
v2.0 (2026) - CircuitPython 9/10

The board is a RP2040 + an ESP8285 running Espressif "AT" firmware on UART.
CircuitPython now has an official build for it ("iLabs Challenger RP2040
WiFi"), and adafruit_espatcontrol drives the AT firmware:

  1. NeoPixel test (red / green / blue)
  2. Wi-Fi access point scan
  3. Connection with the credentials of settings.toml

Pins: the official build names them ESP_TX / ESP_RX / WIFI_RESET / WIFI_MODE,
the GPIO numbers from pins_arduino.h are used as a fallback.
"""
import os
import time
import board
import busio
import digitalio
import neopixel
from adafruit_espatcontrol import adafruit_espatcontrol


def pin(name, fallback):
    return getattr(board, name, getattr(board, fallback))


# --- 1. NeoPixel ----------------------------------------------------------
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
for color in (0xFF0000, 0x00FF00, 0x0000FF, 0x000000):
    pixels[0] = color
    time.sleep(0.4)

# --- 2. ESP8285 -----------------------------------------------------------
mode = digitalio.DigitalInOut(pin("WIFI_MODE", "GP13"))
mode.switch_to_output(value=True)  # high = run firmware (low = flash mode)
reset = digitalio.DigitalInOut(pin("WIFI_RESET", "GP19"))
uart = busio.UART(pin("ESP_TX", "GP4"), pin("ESP_RX", "GP5"),
                  baudrate=115200, receiver_buffer_size=2048)

esp = adafruit_espatcontrol.ESP_ATcontrol(uart, 115200, reset_pin=reset, debug=False)
print("Resetting ESP8285...")
esp.hard_reset()
print("AT firmware:", esp.version)

print("Scanning access points...")
for ap in esp.scan_APs():
    # ap = [encryption, ssid, rssi, mac, channel, ...]
    print("  {:<32} {:>4} dBm  ch {}".format(ap[1], ap[2], ap[4]))
pixels[0] = 0x0000FF

# --- 3. Connection --------------------------------------------------------
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
if ssid:
    print("Connecting to", ssid)
    try:
        esp.connect({"ssid": ssid, "password": password})
        print("Connected, IP:", esp.local_ip)
        pixels[0] = 0x00FF00
    except (RuntimeError, adafruit_espatcontrol.OKError) as e:
        print("Connection failed:", e)
        pixels[0] = 0xFF0000
else:
    print("No CIRCUITPY_WIFI_SSID in settings.toml: skipping connection")
