from adafruit_st7789 import ST7789
import board
import displayio
import digitalio
import time

button1 = digitalio.DigitalInOut(board.IO4) # GPIO23 on Pi
button1.switch_to_input(pull=digitalio.Pull.DOWN)
button2 = digitalio.DigitalInOut(board.IO2) # GPIO24 on Pi
button2.switch_to_input(pull=digitalio.Pull.DOWN)
displayio.release_displays()

# setup the SPI bus
spi = board.SPI()
tft_cs = board.IO38  # arbitrary, pin not used
tft_dc = board.IO7
tft_reset = board.IO0

while not spi.try_lock():
    spi.configure(baudrate=32000000)
spi.unlock()
display_bus = displayio.FourWire(
    spi,
    command=tft_dc,
    chip_select=tft_cs,
    reset=tft_reset,
    baudrate=32000000,
    polarity=1,
    phase=1,    
)


#print("spi.frequency: {}".format(spi.frequency))

# Number of pixels in the display for MiniPiTFT 1.13" 240x135
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 135

# create the display
display = ST7789(
    display_bus,
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT,
    rotation=270,  # The rotation can be adjusted to match your configuration.
    rowstart=40, #specific MiniPiTFT 1.13" 240x135
    colstart=53  #specific MiniPiTFT 1.13" 240x135
    )
print("Hello World!")
print("Button testing\r\nPress Button 1 GPIO23")
while button1.value:
    time.sleep(0.1)
print("Button 1 ok\r\nPress Button 2 GPIO24")
while button2.value:
    time.sleep(0.1)
print("All buttons are ok")