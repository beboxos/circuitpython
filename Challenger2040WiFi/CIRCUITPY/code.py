#Ciruitpython demo
#custom bord import
import challenger2040wifi as board

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
