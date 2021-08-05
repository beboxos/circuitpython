import adafruit_ili9341
import displayio
import kfw_FeatherS2_board as board
import neopixel
neopix_pin = board.D11
pixels = neopixel.NeoPixel(neopix_pin, 1)
pixels[0] = 0x000000 #turn off neopixel
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
print('Hello World!')
