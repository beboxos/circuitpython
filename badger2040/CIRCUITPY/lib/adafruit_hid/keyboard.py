import time
from micropython import const
from .keycode import Keycode
from . import find_device
_MAX_KEYPRESSES = const(6)
class Keyboard:
    LED_NUM_LOCK = 0x01
    LED_CAPS_LOCK = 0x02
    LED_SCROLL_LOCK = 0x04
    LED_COMPOSE = 0x08
    def __init__(self, devices):
        self._keyboard_device = find_device(devices, usage_page=0x1, usage=0x06)
        self.report = bytearray(8)
        self.report_modifier = memoryview(self.report)[0:1]
        self.report_keys = memoryview(self.report)[2:]
        try:
            self.release_all()
        except OSError:
            time.sleep(1)
            self.release_all()
    def press(self, *keycodes):
        for keycode in keycodes:
            self._add_keycode_to_report(keycode)
        self._keyboard_device.send_report(self.report)
    def release(self, *keycodes):
        for keycode in keycodes:
            self._remove_keycode_from_report(keycode)
        self._keyboard_device.send_report(self.report)

    def release_all(self):
        for i in range(8):
            self.report[i] = 0
        self._keyboard_device.send_report(self.report)
    def send(self, *keycodes):
        self.press(*keycodes)
        self.release_all()
    def _add_keycode_to_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            self.report_modifier[0] |= modifier
        else:
            for i in range(_MAX_KEYPRESSES):
                if self.report_keys[i] == keycode:
                    return
            for i in range(_MAX_KEYPRESSES):
                if self.report_keys[i] == 0:
                    self.report_keys[i] = keycode
                    return
            raise ValueError("Trying to press more than six keys at once.")
    def _remove_keycode_from_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            self.report_modifier[0] &= ~modifier
        else:
            for i in range(_MAX_KEYPRESSES):
                if self.report_keys[i] == keycode:
                    self.report_keys[i] = 0
    @property
    def led_status(self):
        return self._keyboard_device.last_received_report
    def led_on(self, led_code):
        return bool(self.led_status[0] & led_code)
