import time
from . import find_device

class Mouse:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 2
    MIDDLE_BUTTON = 4
    def __init__(self, devices):
        self._mouse_device = find_device(devices, usage_page=0x1, usage=0x02)
        self.report = bytearray(4)
        try:
            self._send_no_move()
        except OSError:
            time.sleep(1)
            self._send_no_move()
    def press(self, buttons):
        self.report[0] |= buttons
        self._send_no_move()
    def release(self, buttons):
        self.report[0] &= ~buttons
        self._send_no_move()
    def release_all(self):
        self.report[0] = 0
        self._send_no_move()
    def click(self, buttons):
        self.press(buttons)
        self.release(buttons)
    def move(self, x=0, y=0, wheel=0):
        while x != 0 or y != 0 or wheel != 0:
            partial_x = self._limit(x)
            partial_y = self._limit(y)
            partial_wheel = self._limit(wheel)
            self.report[1] = partial_x & 0xFF
            self.report[2] = partial_y & 0xFF
            self.report[3] = partial_wheel & 0xFF
            self._mouse_device.send_report(self.report)
            x -= partial_x
            y -= partial_y
            wheel -= partial_wheel
    def _send_no_move(self):
        self.report[1] = 0
        self.report[2] = 0
        self.report[3] = 0
        self._mouse_device.send_report(self.report)
    @staticmethod
    def _limit(dist):
        return min(127, max(-127, dist))
