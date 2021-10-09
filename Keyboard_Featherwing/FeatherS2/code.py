import microcontroller
import time
import os
maxfilelegth=50
try:
    boot=microcontroller.nvm[0:maxfilelegth] #get 25 bytes for boot to launch
    boot=boot.decode().strip()
except:
    boot="nothing"
print("boot in memory : "+boot)
if boot!="code.py":
    #there is a file to launh in memory
    #first set code.py for next boot
    Newboot=bytearray(("code.py"+" "*maxfilelegth).encode())
    print("change for code.py")
    microcontroller.nvm[0:maxfilelegth]=Newboot[0:maxfilelegth]
    print("Run "+boot)
    #time.sleep(5)
    #exec(open("./"+boot).read())
    try:
        exec(open("./"+boot).read())
        print("Reseting , return to boot menu")
        time.sleep(2)
        microcontroller.reset()
    except Exception as e:
        import kfw_FeatherS2_board as board
        import adafruit_ili9341
        import displayio
        spi = board.SPI()
        tft_cs = board.D9
        tft_dc = board.D10
        displayio.release_displays()
        display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
        display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
        print("error opening : " + boot)
        print("Error : " + str(e))
        time.sleep(5)
        microcontroller.reset()
time.sleep(0.1)
def MemStore(file):
    Newboot=bytearray((file+" "*maxfilelegth).encode())
    print("change for "+file)
    microcontroller.nvm[0:maxfilelegth]=Newboot[0:maxfilelegth]    

# END of boot code area
#init display
import kfw_FeatherS2_board as board
import adafruit_ili9341
import displayio
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

import bbq10keyboard
from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
i2c = board.I2C()
kbd = BBQ10Keyboard(i2c)
import tsc2004
touch = tsc2004.TSC2004(i2c)
import neopixel
neopix_pin = board.D11
pixels = neopixel.NeoPixel(neopix_pin, 1)
pixels[0] = 0x000000 #set neopixel to black

maxlines = 16 #max lines
maxcols = 49 #max chars

def clearscreen():
    print("\r\n"*maxlines)
#Read root memory
ListFiles = os.listdir("/")
MenuFiles = []
for n in ListFiles:
    if n[-3:]==".py":
        #need to impove, file to not show in menu
        #exlude secrets.py and of course code.py
        if n!="secrets.py" and n!="code.py" and n!="program.py"and n!="lexer.py"and n!="basicparser.py"and n!="basictoken.py"and n!="flowsignal.py" and n!="kfw_pico_board.py" and n!="hid_layout.py":
            MenuFiles.append(n)
print("Debug : "+str(len(MenuFiles))+" files")
maxpage=14
page=0 #page n° max 8 apps by page
index=0 #curent pointer
def drawmenu(page, index):
    global MenuFiles
    clearscreen()
    print('*'*(int((maxcols-28)/2))+' SELECT APPLICATION TO RUN '+'*'*(int((maxcols-28)/2)))
    print('-'*(maxcols-2))
    count=0
    for n in MenuFiles:
        if count>=(page*maxpage) and count<(page*maxpage)+maxpage:
            try:
                test=MenuFiles[count]
                if index==count:
                    print("* ", end="")
                else:
                    print("  ", end="")
                print(test[:(maxcols-2)])
            except:
                #out of range
                pass
        count=count+1

drawmenu(0,0)
selected = -1
def ReadKey():
    #print("Read a key")
    while kbd.key_count < 2:
        pass
    keys = kbd.keys
    #print(keys[0])
    return keys
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
while selected==-1:
    keyRead = ReadKey()
    key = keyRead[0]    
    key = key[1]
    if key == '\x01':
        #  up
        if index>0:
            index=index-1
            page=int(index/maxpage)
            drawmenu(page,index)
    if key == '\x02':
        # down
        if index<len(MenuFiles)-1:
            index=index+1
            page=int(index/maxpage)
            drawmenu(page,index)
    if key == '\x05':
        #stick fire
        selected=1
    time.sleep(0.1)
clearscreen()
print("Selected  : "+str(index)+ " > " + MenuFiles[index])
MemStore(MenuFiles[index])
time.sleep(0.5)
print("\r\n"*int(maxlines/2))
print('*'*(int((maxcols-12)/2))+'   RESET   '+'*'*(int((maxcols-12)/2)))
#print("-------------   RESET   -----------")
print("\r\n"*int((maxlines/2)-2))
time.sleep(0.5)
microcontroller.reset()