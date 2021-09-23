#HID init
layout = "fr" # fr or us
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
import adafruit_ducky
keyboard = Keyboard(usb_hid.devices)
if layout=="fr": 
    from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
    keyboard_layout = KeyboardLayoutFR(keyboard)  # We're in France :)
else:
    from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
    keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
def callduck(filename):
    duck = adafruit_ducky.Ducky(filename, keyboard, keyboard_layout)    
    result = True
    while result is not False:
        result = duck.loop()
    return result    
#UART
import busio, board, digitalio
uart = busio.UART(board.TX, board.RX, baudrate=9600)
led = digitalio.DigitalInOut(board.BLUE_LED)
led.direction = digitalio.Direction.OUTPUT
led.value=True
#auto run bad USB on boot.txt
try:
    callduck("boot.txt")
except:
    pass
while True:
    time.sleep(0.1)
    data=uart.readline()
    if data is not None:
        led.value=False
        data_string= ''.join([chr(b) for b in data])
        data_string=str(data_string).replace("b'","").replace("\r\n","")
        print(data_string+" -> ", end='')
        reponse = callduck(data_string)
        print(reponse)
        led.value=True