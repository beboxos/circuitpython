"""
badger_power - deep sleep helpers for the Badger 2040 (BeBoX, 2026).

The Badger 2040 runs on a small battery, and an e-ink screen keeps its image
with no power. Between updates the RP2040 can be put into deep sleep: it draws
almost nothing and wakes on a button, so a badge can last for months.

Usage (at the very end of your code.py, once the screen shows what you want):

    import badger_power
    badger_power.sleep_until_button()   # wakes on A / B / C / UP / DOWN

or sleep for a fixed time:

    badger_power.sleep_for(600)         # 10 minutes, then re-run code.py

After a deep sleep the board restarts and runs code.py again from the top, so
structure code.py to redraw and then sleep.
"""
import alarm
import board


# Badger 2040 user buttons (active high, with the on-board pull-downs)
_BUTTON_NAMES = ("SW_A", "SW_B", "SW_C", "SW_UP", "SW_DOWN",
                 "BUTTON_A", "BUTTON_B", "BUTTON_C", "BUTTON_UP", "BUTTON_DOWN")


def _button_pins():
    pins = []
    seen = set()
    for name in _BUTTON_NAMES:
        pin = getattr(board, name, None)
        if pin is not None and pin not in seen:
            seen.add(pin)
            pins.append(pin)
    return pins


def sleep_until_button(extra_seconds=None):
    """Deep sleep until any user button is pressed (optionally also a timeout).

    Returns nothing: the board restarts and runs code.py again on wake.
    """
    alarms = []
    for pin in _button_pins():
        try:
            alarms.append(alarm.pin.PinAlarm(pin=pin, value=True, pull=True))
        except (ValueError, RuntimeError):
            pass
    if extra_seconds:
        alarms.append(alarm.time.TimeAlarm(
            monotonic_time=__import__("time").monotonic() + extra_seconds))
    alarm.exit_and_deep_sleep_until_alarms(*alarms)


def sleep_for(seconds):
    """Deep sleep for `seconds`, then restart and run code.py again."""
    import time
    alarm.exit_and_deep_sleep_until_alarms(
        alarm.time.TimeAlarm(monotonic_time=time.monotonic() + seconds))


def woke_from_button():
    """True if the last wake came from a button (vs. a timer or power-on)."""
    return isinstance(alarm.wake_alarm, alarm.pin.PinAlarm)
