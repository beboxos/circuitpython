"""
bebox_common.keyboard - one keyboard API for several input devices.

    from bebox_common.keyboard import find_keyboard, KEY_ENTER
    kb = find_keyboard()        # CardKB, BBQ10 or USB serial console
    key = kb.read()             # None, a printable char or a KEY_* token

Supported:
  - M5Stack CardKB                       (I2C 0x5F)
  - BlackBerry Q10 / Keyboard FeatherWing (I2C 0x1F)
  - USB serial console (any terminal, ANSI escape sequences for arrows)
"""
import sys

# Normalized key tokens (anything else returned by read() is a printable char)
KEY_ENTER, KEY_BS, KEY_ESC, KEY_TAB = "ENTER", "BS", "ESC", "TAB"
KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT = "UP", "DOWN", "LEFT", "RIGHT"
KEY_HOME, KEY_END, KEY_SELECT = "HOME", "END", "SELECT"

CARDKB_ADDR = 0x5F
BBQ10_ADDR = 0x1F


class CardKB:
    """M5Stack CardKB: one byte per key, 0x00 when nothing is pressed."""
    name = "CardKB (I2C)"
    _MAP = {0x0D: KEY_ENTER, 0x0A: KEY_ENTER, 0x08: KEY_BS, 0x7F: KEY_BS,
            0x1B: KEY_ESC, 0x09: KEY_TAB, 0xB5: KEY_UP, 0xB6: KEY_DOWN,
            0xB4: KEY_LEFT, 0xB7: KEY_RIGHT, 0x99: KEY_HOME, 0xA4: KEY_END}

    def __init__(self, i2c):
        self.i2c = i2c
        self.buf = bytearray(1)

    def read(self):
        while not self.i2c.try_lock():
            pass
        try:
            self.i2c.readfrom_into(CARDKB_ADDR, self.buf)
        except OSError:
            return None
        finally:
            self.i2c.unlock()
        c = self.buf[0]
        if c == 0:
            return None
        if c in self._MAP:
            return self._MAP[c]
        if 32 <= c < 127:
            return chr(c)
        return None


class BBQ10:
    """BlackBerry Q10 keyboard (bbq10keyboard driver). Reads its key FIFO."""
    name = "BBQ10 (I2C)"
    # Keyboard FeatherWing joystick / side keys reported as control codes
    _MAP = {0x0A: KEY_ENTER, 0x0D: KEY_ENTER, 0x08: KEY_BS, 0x1B: KEY_ESC,
            0x09: KEY_TAB, 0x01: KEY_UP, 0x02: KEY_DOWN, 0x03: KEY_LEFT,
            0x04: KEY_RIGHT, 0x05: KEY_SELECT, 0x06: KEY_HOME, 0x07: KEY_END}
    _STATE_RELEASE = 3  # bbq10keyboard STATE_RELEASE

    def __init__(self, kbd):
        self.kbd = kbd  # a bbq10keyboard.BBQ10Keyboard instance

    def read(self):
        if self.kbd.key_count == 0:
            return None
        state, char = self.kbd.key  # (state, char)
        if state == self._STATE_RELEASE:  # act on press, ignore release
            return None
        code = ord(char)
        if code in self._MAP:
            return self._MAP[code]
        if 32 <= code < 127:
            return char
        return None


class SerialKB:
    """USB serial console (Mu, Thonny, screen, tio...). Non-blocking."""
    name = "USB serial"
    _ESC = {"A": KEY_UP, "B": KEY_DOWN, "C": KEY_RIGHT, "D": KEY_LEFT,
            "H": KEY_HOME, "F": KEY_END, "1": KEY_HOME, "4": KEY_END}

    def __init__(self):
        import supervisor
        self.runtime = supervisor.runtime

    def _getc(self):
        while not self.runtime.serial_bytes_available:
            pass
        return sys.stdin.read(1)

    def read(self):
        if not self.runtime.serial_bytes_available:
            return None
        c = sys.stdin.read(1)
        if c in ("\r", "\n"):
            return KEY_ENTER
        if c in ("\x08", "\x7f"):
            return KEY_BS
        if c == "\t":
            return KEY_TAB
        if c == "\x1b":
            nxt = self._getc()
            if nxt not in "[O":
                return KEY_ESC
            k = self._getc()
            if k in "14":          # ESC [ 1 ~  /  ESC [ 4 ~
                self._getc()
            return self._ESC.get(k)
        if " " <= c <= "~":
            return c
        return None


def find_keyboard(i2c=None):
    """Return the first available keyboard, USB serial console as fallback.

    Pass an existing busio.I2C to reuse it; otherwise one is created from
    board.SCL / board.SDA when possible.
    """
    try:
        if i2c is None:
            import board
            import busio
            i2c = busio.I2C(board.SCL, board.SDA)
        while not i2c.try_lock():
            pass
        found = i2c.scan()
        i2c.unlock()
        if BBQ10_ADDR in found:
            try:
                import bbq10keyboard
                return BBQ10(bbq10keyboard.BBQ10Keyboard(i2c))
            except ImportError:
                pass
        if CARDKB_ADDR in found:
            return CardKB(i2c)
    except Exception:  # no I2C pins, no pull-ups, bus busy...
        pass
    return SerialKB()
