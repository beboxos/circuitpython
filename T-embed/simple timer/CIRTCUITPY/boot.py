# merci titi :)
import board
import busio
import displayio
from adafruit_st7789 import ST7789

displayio.release_displays()

tft_cs = board.IO10
tft_dc = board.IO13
tft_reset = board.IO9
tft_backlight = board.IO15
spi_clk = board.IO12
spi_mosi = board.IO11

tft_width = 320
tft_height = 170

spi = busio.SPI(spi_clk, spi_mosi)

while not spi.try_lock():
    pass
spi.configure(baudrate=24000000) # Configure SPI for 24MHz
spi.unlock()


display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)

display = ST7789(display_bus, width=tft_width, height=tft_height, backlight_pin=tft_backlight, rotation=90, rowstart=0, colstart=35)
