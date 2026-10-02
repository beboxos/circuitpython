import adafruit_ili9341
import displayio
try:
    from fourwire import FourWire  # CircuitPython 9+
except ImportError:
    from displayio import FourWire  # CircuitPython 8
import board
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
displayio.release_displays()
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
print('Hello World!')
