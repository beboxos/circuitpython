'''
BeBoX default code.py

'''
import adafruit_ili9341
import displayio
import kfw_FeatherS2_board as board
import neopixel
import bbq10keyboard
from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
import microcontroller
import time
import os
"""

"""
USB=0

"""

"""
neopix_pin = board.D11
pixels = neopixel.NeoPixel(neopix_pin, 1)
pixels[0] = 0x000000 #set neopixel
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

#calc_group = displayio.Group()
#display.show(calc_group)


klight = 10
slight = 10
import tsc2004
i2c = board.I2C()
kbd = BBQ10Keyboard(i2c)
touch = tsc2004.TSC2004(i2c)
import os
print(os.uname().machine)
def is_usb_connected():
    import storage
    try:
        storage.remount('/', readonly=False)  # attempt to mount readwrite
        storage.remount('/', readonly=True)  # attempt to mount readonly
    except RuntimeError as e:
        return True
    return False
is_usb = "USB" if is_usb_connected() else "NO USB"
if is_usb == "USB":
    # connected on computer
    print('Connected on USB')
    import os
    fs_stat = os.statvfs('/')
    print("Disk size in MB", fs_stat[0] * fs_stat[2] / 1024 / 1024)
    print("Free space in MB", fs_stat[0] * fs_stat[3] / 1024 / 1024)
    import usb_hid
    from adafruit_hid.mouse import Mouse
    from adafruit_hid.keyboard import Keyboard
    #from adafruit_hid.keyboard_layout_US import KeyboardLayoutUS
    from adafruit_hid.keyboard_layout_FR import KeyboardLayoutFR
    from adafruit_hid.keycode import Keycode
    mouse = Mouse(usb_hid.devices)
    keyboard = Keyboard(usb_hid.devices)
    #keyboard_layout = KeyboardLayoutUS(keyboard)
    keyboard_layout = KeyboardLayoutFR(keyboard)
    USB = 1
if is_usb == "NO USB":
    print('not Connected on USB')
    print('Welcome :')
    print('Wifi available around :')
    import wifi
    networks = []
    for network in wifi.radio.start_scanning_networks():
        networks.append(network)
    wifi.radio.stop_scanning_networks()
    networks = sorted(networks, key=lambda net: net.rssi, reverse=True)
    for network in networks:
        print("ssid:",network.ssid, "rssi:",network.rssi)
    import gc
    print('Memory : ' + str(int((gc.mem_free()/1024))/1024)+" MB" )
    USB = 0
    
    #print( str(int((gc.mem_free()/1024))/1024)+" MB" )
def clearScreen():
    for n in range(0,16,1):
        print("")
def showMenu():
    if USB ==1 :
        print("-------------------------------------------------")
        print("*                 joystick                      *")
        print("*       UP/DOWN/LEFT/RIGHT Mouve Mouse          *")
        print("*         Stick Button = Left click             *")
        print("*           Keyboard type HID Key               *")
        print("-------------------------------------------------")
        print("QUIT      KBD LIGHT         Right click     RESET")
        print("-------------------------------------------------")
    else:
        print("-------------------------------------------------")
        print("*                 joystick                      *")
        print("*          LEFT/RIGHT Keyboard light            *")
        print("*                                               *")
        print("*                                               *")
        print("-------------------------------------------------")
        print("QUIT      KBD LIGHT        Factory test     RESET")
        print("-------------------------------------------------")
def ReadKey():
    #print("Read a key")
    while kbd.key_count < 2:
        pass
    keys = kbd.keys
    #print(keys[0])
    return keys
keyRead = ''
key = ''
flight = 1
'''
special keycodes
'\x06'= 'L1'
'\x11'= 'L2'
'\x07'= 'R1'
'\x12'= 'R2'
'\x01'= 'UP'
'\x02'= 'DOWN'
'\x03'= 'LEFT'
'\x04'= 'RIGHT'
'\x05'= 'STICK BUTTON'
'''
showMenu()
while key != '\x06':
    keyRead = ReadKey()
    key = keyRead[0]
    #debug
    #print(key)
    key = key[1]
    if key == '\x01':
        #  up
        if USB ==1 :
            mouse.move(y=-10)
        """
        slight = slight + 2
        if slight>10:
            slight = 10
        kbd.backlight2 = slight /10"""
    if key == '\x02':
        # down
        if USB ==1 :
            mouse.move(y=+10)
        """
        slight = slight - 2
        if slight<0:
            slight = 0
        kbd.backlight2 = slight / 10"""
    if key == '\x04':
        # RIght
        if USB ==1 :
            mouse.move(x=10)
        else:
            klight = klight + 2
            if klight>10:
                klight = 10
            kbd.backlight = klight / 10   # keyboard backlight
    if key == '\x03':
        # kbd light up
        if USB ==1 :
            mouse.move(x=-10)
        else:
            klight = klight - 2
            if klight<0:
                klight = 0
            kbd.backlight = klight / 10   # keyboard backlight
    if key == '\x05':
        #stick fire
        if USB ==1 :
            mouse.click(Mouse.LEFT_BUTTON)
        
    if key =='\x06':
        print("L1 : Quit")
    if key =='\x11':
        flight = -flight
        if flight == 1:
            kbd.backlight = klight / 10
            kbd.backlight2 = slight / 10
        else:
            kbd.backlight = 0
            kbd.backlight2 = 0  
    if key =='\x07':
        if USB ==0 :
            import codetestkbd
            print("R1")
        else:
            mouse.click(Mouse.RIGHT_BUTTON)
    if key =='\x12':
        clearScreen()
        print("-------------------- RESET ----------------------")
        for n in range(0,7,1):
            print("")        
        time.sleep(1)
        microcontroller.reset()
        #print("R2") 
    if key!="":
        if USB ==1 :
            try:
                print(key, end='')
                keyboard_layout.write(key)
            except:
                time.sleep(0.1)
            
#END