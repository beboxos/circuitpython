import sys
if sys.implementation.version[0] < 3:
    raise ImportError(
        "{0} is not supported in CircuitPython 2.x or lower".format(__name__)
    )
import struct
import time
from . import find_device
class ConsumerControl:
    def __init__(self, devices):
        self._consumer_device = find_device(devices, usage_page=0x0C, usage=0x01)
        self._report = bytearray(2)
        try:
            self.send(0x0)
        except OSError:
            time.sleep(1)
            self.send(0x0)

    def send(self, consumer_code):
        self.press(consumer_code)
        self.release()

    def press(self, consumer_code):
        struct.pack_into("<H", self._report, 0, consumer_code)
        self._consumer_device.send_report(self._report)

    def release(self):
        self._report[0] = self._report[1] = 0x0
        self._consumer_device.send_report(self._report)
