import board
import busio


_SPI = None
_UART = None
_I2C = None


A0 = board.D14
A1 = board.D15
A2 = board.D16
A3 = board.D17
A4 = board.D18
A5 = board.D19
SCK = board.D25
COPI = board.D24
MOSI = board.D24
CIPO = board.D23
MISO = board.D23
RX = board.D0
TX = board.D1
D14 = board.A0
MISC = board.A0
SCL = board.D11
SDA = board.D10
D5 = board.D20
D6 = board.D21
D9 = board.D5
D10 = board.D6
D11 = board.D9
D12 = board.D12
D13 = board.D13


def SPI():
    global _SPI

    if not _SPI:
        _SPI = busio.SPI(SCK, COPI, CIPO)

    return _SPI


def UART():
    global _UART

    if not _UART:
        _UART = busio.UART(TX, RX)

    return _UART


def I2C():
    global _I2C

    if not _I2C:
        _I2C = busio.I2C(SCL, SDA)

    return _I2C

