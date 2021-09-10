#Ciruitpython demo
#custom bord import
#import challenger2040wifi as board
import board
import busio
import digitalio
import neopixel
import time

neopix_pin = board.NEOPIXEL
pixels = neopixel.NeoPixel(neopix_pin,1)
#neopixel test
pixels[0]= 0x090000 #red
time.sleep(0.5)
pixels[0]= 0x000900 #green
time.sleep(0.5)
pixels[0]= 0x000009 #blue
time.sleep(0.5)
pixels[0]= 0x000000 #off
time.sleep(0.5)
#to do wifi demo scan AP etc..
wifi=busio.UART(board.ESP_TX, board.ESP_RX, baudrate=115200)
wrst = digitalio.DigitalInOut(board.WIFI_RESET)
wmde = digitalio.DigitalInOut(board.WIFI_MODE)
wrst.direction = digitalio.Direction.OUTPUT
wmde.direction = digitalio.Direction.OUTPUT
wrst.value = 0
wmde.value = 1
wrst.value = 1
print (wifi.read())
wifi.write(bytearray('AT\r\n'))
print (wifi.read())
