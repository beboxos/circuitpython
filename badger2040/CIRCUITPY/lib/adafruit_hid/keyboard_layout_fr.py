"""
`adafruit_hid.keyboard_layout_us.KeyboardLayoutUS`
=======================================================
* Author(s): Dan Halbert
Edited by BeBoX ( depanet@gmail.com ) for French Azerty Keyboard
added support for ALTGR ( RIGHT ALT ) key combo
05.09.2021
"""
from .keycode import Keycode
class KeyboardLayoutFR:
    SHIFT_FLAG = 0x80
    ALTGR_FLAG = 0x40
    ASCII_TO_KEYCODE = (
        b"\x00"  # NUL
        b"\x00"  # SOH
        b"\x00"  # STX
        b"\x00"  # ETX
        b"\x00"  # EOT
        b"\x00"  # ENQ
        b"\x00"  # ACK
        b"\x00"  # BEL \a
        b"\x2a"  # BS BACKSPACE \b (called DELETE in the usb.org document)
        b"\x2b"  # TAB \t
        b"\x28"  # LF \n (called Return or ENTER in the usb.org document)
        b"\x00"  # VT \v
        b"\x00"  # FF \f
        b"\x00"  # CR \r
        b"\x00"  # SO
        b"\x00"  # SI
        b"\x00"  # DLE
        b"\x00"  # DC1
        b"\x00"  # DC2
        b"\x00"  # DC3
        b"\x00"  # DC4
        b"\x00"  # NAK
        b"\x00"  # SYN
        b"\x00"  # ETB
        b"\x00"  # CAN
        b"\x00"  # EM
        b"\x00"  # SUB
        b"\x29"  # ESC
        b"\x00"  # FS
        b"\x00"  # GS
        b"\x00"  # RS
        b"\x00"  # US
        b"\x2c"  # SPACE
        b"\x38"  # ! x1e|SHIFT_FLAG (shift 1)
        b"\x20"  # " x34|SHIFT_FLAG (shift ')
        b"\x60"  # # x20|SHIFT_FLAG (shift 3) 3+ALTGR
        b"\x30" #b"\xa1"  # $ x21|SHIFT_FLAG (shift 4) => b"\x30"
        b"\x34"  # % x22|SHIFT_FLAG (shift 5)
        b"\x1E"  # & x24|SHIFT_FLAG (shift 7)
        b"\x21"  # '
        b"\x22"  # ( x26|SHIFT_FLAG (shift 9)
        b"\x2d"  # ) x27|SHIFT_FLAG (shift 0)
        b"\x32"  # * x25|SHIFT_FLAG (shift 8)
        b"\xae"  # + x2e|SHIFT_FLAG (shift =)
        b"\x10" #b"\x36"  # , => m b"\x10"
        b"\x23"  # -
        b"\xb6"  # .
        b"\xb7"  # /
        b"\xA7"  # 0
        b"\x9e"  # 1
        b"\x9f"  # 2
        b"\xA0"  # 3
        b"\xA1"  # 4
        b"\xA2"  # 5
        b"\xA3"  # 6
        b"\xA4"  # 7
        b"\xA5"  # 8
        b"\xA6"  # 9
        b"\x37"  # : x33|SHIFT_FLAG (shift ;)
        b"\x36"  # ;
        b"\x03"  # < x36|SHIFT_FLAG (shift ,)
        b"\x2e"  # =
        b"\x83"  # > x37|SHIFT_FLAG (shift .)
        b"\x90"  # ? x38|SHIFT_FLAG (shift /)
        b"\x67"  # @ x1f|SHIFT_FLAG (shift 2) old 9f 8 + ALTGR FLAG
        b"\x94"  # A x04|SHIFT_FLAG (shift a) => Q b"\x94"
        b"\x85"  # B x05|SHIFT_FLAG (etc.)
        b"\x86"  # C x06|SHIFT_FLAG
        b"\x87"  # D x07|SHIFT_FLAG
        b"\x88"  # E x08|SHIFT_FLAG
        b"\x89"  # F x09|SHIFT_FLAG
        b"\x8a"  # G x0a|SHIFT_FLAG
        b"\x8b"  # H x0b|SHIFT_FLAG
        b"\x8c"  # I x0c|SHIFT_FLAG
        b"\x8d"  # J x0d|SHIFT_FLAG
        b"\x8e"  # K x0e|SHIFT_FLAG
        b"\x8f"  # L x0f|SHIFT_FLAG
        b"\xb3" #b"\x90"  # M x10|SHIFT_FLAG => : b"\xb3"
        b"\x91"  # N x11|SHIFT_FLAG
        b"\x92"  # O x12|SHIFT_FLAG
        b"\x93"  # P x13|SHIFT_FLAG
        b"\x84"  # Q x14|SHIFT_FLAG => A b"\x84"
        b"\x95"  # R x15|SHIFT_FLAG
        b"\x96"  # S x16|SHIFT_FLAG
        b"\x97"  # T x17|SHIFT_FLAG
        b"\x98"  # U x18|SHIFT_FLAG
        b"\x99"  # V x19|SHIFT_FLAG
        b"\x9d"  # W x1a|SHIFT_FLAG => Z b"\x9d"
        b"\x9b"  # X x1b|SHIFT_FLAG
        b"\x9c"  # Y x1c|SHIFT_FLAG
        b"\x9a"  # Z x1d|SHIFT_FLAG => W b"\x9a"
        b"\x62"  # [
        b"\x65"  # \ backslash
        b"\x6d"  # ]
        b"\x66"  # ^ x23|SHIFT_FLAG (shift 6)
        b"\x25"  # _ x2d|SHIFT_FLAG (shift -)
        b"\x64"  # `
        b"\x14"  # a => q b"\x14"
        b"\x05"  # b
        b"\x06"  # c
        b"\x07"  # d
        b"\x08"  # e
        b"\x09"  # f
        b"\x0a"  # g
        b"\x0b"  # h
        b"\x0c"  # i
        b"\x0d"  # j
        b"\x0e"  # k
        b"\x0f"  # l
        b"\x33" #b"\x10"  # m => ; b"\x33"
        b"\x11"  # n
        b"\x12"  # o
        b"\x13"  # p
        b"\x04"  # q => a b"\x04"
        b"\x15"  # r
        b"\x16"  # s
        b"\x17"  # t
        b"\x18"  # u
        b"\x19"  # v
        b"\x1d"  # w => zb"\x1d"
        b"\x1b"  # x
        b"\x1c"  # y
        b"\x1a"  # z => w b"\x1a"
        b"\x61"  # { x2f|SHIFT_FLAG (shift [)
        b"\x63"  # | x31|SHIFT_FLAG (shift \)
        b"\x6e"  # } x30|SHIFT_FLAG (shift ])
        b"\x5f"  # ~ x35|SHIFT_FLAG (shift `)
        b"\x4c"  # DEL DELETE (called Forward Delete in usb.org document)
    )

    def __init__(self, keyboard):
        self.keyboard = keyboard
    def write(self, string):
        for char in string:
            keycode = self._char_to_keycode(char)
            if keycode & self.SHIFT_FLAG:
                keycode &= ~self.SHIFT_FLAG
                self.keyboard.press(Keycode.SHIFT)
            if keycode & self.ALTGR_FLAG:
                keycode &= ~self.ALTGR_FLAG
                self.keyboard.press(Keycode.RIGHT_ALT)
            self.keyboard.press(keycode)
            self.keyboard.release_all()
    def keycodes(self, char):
        keycode = self._char_to_keycode(char)
        if keycode & self.SHIFT_FLAG:
            return (Keycode.SHIFT, keycode & ~self.SHIFT_FLAG)
        if keycode & self.ALTGR_FLAG:
            return (Keycode.SHIFT, keycode & ~self.ALTGR_FLAG)
        return (keycode,)
    def _char_to_keycode(self, char):
        char_val = ord(char)
        if char_val > 128:
            raise ValueError("Not an ASCII character.")
        keycode = self.ASCII_TO_KEYCODE[char_val]
        if keycode == 0:
            print('keycode = 0 : error skip')
        return keycode
