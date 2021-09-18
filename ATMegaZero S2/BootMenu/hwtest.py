from adafruit_st7789 import ST7789
import board, microcontroller
import displayio
import digitalio
import time

#button definition
button1 = digitalio.DigitalInOut(board.IO4) # GPIO23 on Pi IO4 on ATMegaZero S2
button1.switch_to_input(pull=digitalio.Pull.DOWN)
button2 = digitalio.DigitalInOut(board.IO2) # GPIO24 on Pi IO2 on ATMegaZero S2
button2.switch_to_input(pull=digitalio.Pull.DOWN)

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
#all init done

print("Hello World!")
print("*"*37, end="")
print("Button testing\r\nPress Button 1 GPIO23/IO4")
while button1.value:
    time.sleep(0.1)
print("Button 1 ok\r\nPress Button 2 GPIO24/IO2")
while button2.value:
    time.sleep(0.1)
while button2.value==False:
    pass
print("*"*37, end="")
print("All buttons are ok")
print("*"*37, end="")
print("press button 1 to rotate screen, button 2 to quit")
rot = 270
chg=False
while button2.value:
    if chg==True:        
        if rot==0 and chg==True:
            rot=90
            display.rotation=rot
            print("Rotation 90")
            chg=False
        elif rot==90 and chg==True:
            rot=180
            display.rotation=rot
            print("Rotation 180")
            chg=False
        elif rot==180 and chg==True:
            rot=270
            display.rotation=rot
            print("Rotation 270")
            chg=False
        elif rot==270 and chg==True:
            rot=0
            display.rotation=rot
            print("Rotation 0")
            chg=False
        
            
    if button1.value==False:
        while button1.value==True:
            pass
        chg=True
    time.sleep(0.1)
time.sleep(2)
microcontroller.reset()