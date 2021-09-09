"""
board file for challerger2040Wifi by BeBoX
extracted from original Challenger arduino file : pins_arduino.h
09.09.2021
for contact :
twitter : BeBoXoS
mail : depanet at gmail dot com
"""

import board
import busio


_SPI = None
_UART = None
_UART2 = None
_I2C = None

#LED
LED = board.GP12

#Serial
SERIAL1_TX = board.GP16
SERIAL1_RX = board.GP17
#Connected to ESP8285
SERIAL2_TX = board.GP4
SERIAL2_RX = board.GP5
ESP8285_RST = board.GP19
ESP8285_MODE = board.GP13

#SPI
SPIO_MISO = board.GP24
SPIO_MOSI = board.GP23
SPIO_SCK = board.GP22
SPIO_SS = board.GP21

#Wire
WIRE0_SDA = board.GP0
WIRE0_SCL = board.GP1

SERIAL_HOWMANY= board.GP2
SPI_HOWMANY = board.GP1
WIRE_HOWMANY= board.GP1

LED_BUILTIN = LED
NEOPIXEL = board.GP11

D0 = board.GP16
D1 = board.GP17
D2 = board.GP24
D3 = board.GP23
D4 = board.GP22
D5 = board.GP2
D6 = board.GP3
D7 = board.GP0
D8 = board.GP1
D9 = board.GP6
D10 = board.GP7
D11 = board.GP8
D12 = board.GP9
D13 = board.GP10
D14 = board.GP11
D15 = board.GP12
D16 = board.GP13
D17 = board.GP19

A0 = board.GP26
A1 = board.GP27
A2 = board.GP28
A3 = board.A3
A4 = board.GP25
A5 = board.GP21


def SPI():
    global _SPI
    if not _SPI:
        _SPI = busio.SPI(SPIO_SCK,SPIO_MOSI,SPIO_MISO)
    return _SPI

def UART():
    global _UART
    if not _UART:
        _UART = busio.UART(SERIAL1_TX,SERIAL1_RX)
    return _UART

def UART2():
    global _UART2
    if not _UART2:
        _UART2 = busio.UART(SERIAL2_TX,SERIAL2_RX)
    return _UART2

def I2C():
    global _I2C
    if not _I2C:
        _I2C = busio.I2C(WIRE0_SCL,WIRE0_SDA)
    return _I2C

