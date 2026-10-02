"""
boot.py for BasicPython - make CIRCUITPY writable so `save` works.

By default CircuitPython lets the USB host (your PC) write to CIRCUITPY and
keeps the board's own code read-only, so BasicPython's `save` fails with
"Read-only filesystem". This boot.py gives the board write access when a key
is held at power-up:

  - hold the SELECT / joystick button (or button D0) while resetting
    -> the board can write (save works), the PC mounts CIRCUITPY read-only
  - boot normally
    -> the PC can write (drag & drop), the board cannot save

Adjust BOOT_BUTTON below to a button that exists on your board. If none
matches, the board stays writable (fine for a dev board, your PC then sees
CIRCUITPY as read-only).
"""
import board
import storage

BOOT_BUTTON = ("BUTTON", "D0", "BOOT0", "BUTTON_SELECT")  # first that exists

def _pressed():
    import digitalio
    for name in BOOT_BUTTON:
        pin = getattr(board, name, None)
        if pin is None:
            continue
        btn = digitalio.DigitalInOut(pin)
        btn.switch_to_input(pull=digitalio.Pull.UP)
        held = not btn.value  # active low
        btn.deinit()
        return held
    return True  # no known button: default to board-writable

try:
    if _pressed():
        storage.remount("/", readonly=False)
        print("boot.py: CIRCUITPY is writable by the board (save enabled)")
    else:
        print("boot.py: CIRCUITPY is writable by the USB host")
except Exception as e:  # pylint: disable=broad-except
    print("boot.py:", e)
