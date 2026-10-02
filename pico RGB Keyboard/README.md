# Pimoroni Pico RGB Keypad

![pico](../images/picorgb.jpg)

## DuckyPad

`DuckyPad/` turns the [Pico RGB Keypad](https://shop.pimoroni.com/products/pico-rgb-keypad-base)
into a 16-key macro pad: each key types a [DuckyScript](https://docs.hak5.org/hak5-usb-rubber-ducky)
file over USB HID.

| Key | Script |
|---|---|
| 1st … 16th | `ducky/0.txt` … `ducky/F.txt` |

- The pressed key lights up red while its script runs; key 0 blinks blue when idle.
- Keyboard layout: edit `hid_layout.py` (`"fr"` = French AZERTY with AltGr support, `"us"`).
- `lib/ducky_bebox.py` is a modified `adafruit_ducky` (ALTGR key, a single command can be passed
  instead of a file name). It has its own name so `circup update` never overwrites it.

### Install (CircuitPython 9 / 10)

1. Flash the Raspberry Pi Pico CircuitPython build.
2. Copy the content of `DuckyPad/` to the board.
3. `pip install circup` then `circup install -r requirements.txt`.

> ⚠️ Only use HID scripts on computers you own or are allowed to use.
