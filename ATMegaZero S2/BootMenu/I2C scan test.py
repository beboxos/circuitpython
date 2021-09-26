from adafruit_st7789 import ST7789
import board, displayio, digitalio, time, microcontroller
#button init ***********************************************************************
button1 = digitalio.DigitalInOut(board.IO4) # GPIO23 on Pi IO4 on ATMegaZero S2
button1.switch_to_input(pull=digitalio.Pull.DOWN)
button2 = digitalio.DigitalInOut(board.IO2) # GPIO24 on Pi IO2 on ATMegaZero S2
button2.switch_to_input(pull=digitalio.Pull.DOWN)
#screen initialisation   ***********************************************************
displayio.release_displays()
# setup the SPI bus
spi = board.SPI()
tft_cs = board.IO38   # GPIO8 CE0
tft_dc = board.IO7    # GPIO25
tft_reset = board.IO0 # GPIO21
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
#all init done ***********************************************************************
i2c =board.I2C()
BatAdress = 0x36
print("Button 2 to Exit")
while not i2c.try_lock():
    pass
try:
    while button2.value==True:
        print("I2C addresses found:", [hex(device_address)
              for device_address in i2c.scan()])
        time.sleep(2)

finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
    i2c.unlock()
for n in range(0,10,1):
    print(" ")
print("--------------- RESET ---------------")
for n in range(0,3,1):
    print(" ")
time.sleep(2)
microcontroller.reset()