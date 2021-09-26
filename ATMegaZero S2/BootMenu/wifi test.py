import wifi
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

def netlist():
    networks = []
    print("-"*37, end="")
    print("networks : ")
    for network in wifi.radio.start_scanning_networks():
        networks.append(network)
    wifi.radio.stop_scanning_networks()
    networks = sorted(networks, key=lambda net: net.rssi, reverse=False)
    for network in networks:
        print("ssid:",network.ssid, "rssi:",network.rssi)
    print("-"*37, end="")
netlist()     
print("Button 2 to Exit, 1 to test again")
while button2.value:
    if button1.value==False:
        while button1.value==False:
            pass
        netlist()
    pass
for n in range(0,10,1):
    print(" ")
print("--------------- RESET ---------------")
for n in range(0,3,1):
    print(" ")
time.sleep(2)
microcontroller.reset()