from adafruit_st7789 import ST7789
import board, displayio, digitalio, time

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
#launcher code
import microcontroller, os, time
try:
    boot=microcontroller.nvm[0:25] #get 25 bytes for boot to launch
    boot=boot.decode().strip()
except:
    boot="nothing"
print("boot in memory : "+boot)
if boot!="code.py":
    #there is a file to launh in memory
    #first set code.py for next boot
    Newboot=bytearray(("code.py"+" "*25).encode())
    print("change for code.py")
    microcontroller.nvm[0:25]=Newboot[0:25]
    print("Run "+boot)
    #time.sleep(5)
    #exec(open("./"+boot).read())
    try:
        exec(open("./"+boot).read())
    except:
        print("error opening : " + boot)
time.sleep(0.1)
def MemStore(file):
    Newboot=bytearray((file+" "*25).encode())
    print("change for "+file)
    microcontroller.nvm[0:25]=Newboot[0:25]    

# END of boot code area
#button init ***********************************************************************
button1 = digitalio.DigitalInOut(board.IO4) # GPIO23 on Pi IO4 on ATMegaZero S2
button1.switch_to_input(pull=digitalio.Pull.DOWN)
button2 = digitalio.DigitalInOut(board.IO2) # GPIO24 on Pi IO2 on ATMegaZero S2
button2.switch_to_input(pull=digitalio.Pull.DOWN)
#screen initialisation   ***********************************************************
# screen specs
maxlines = 10 #max 10 lines
maxcols = 37 #max 37 chars

def clearscreen():
    print("\r\n"*maxlines)
#Read root memory
ListFiles = os.listdir("/")
MenuFiles = []
for n in ListFiles:
    if n[-3:]==".py":
        #need to impove, file to not show in menu
        #exlude secrets.py and of course code.py
        if n!="secrets.py" and n!="code.py":
            MenuFiles.append(n)
print("Debug : "+str(len(MenuFiles))+" files")
maxpage=7
page=0 #page n° max 8 apps by page
index=0 #curent pointer
def drawmenu(page, index):
    global MenuFiles
    clearscreen()
    print('**** SELECT APPLICATION TO RUN *****')
    print('-'*(maxcols-1))
    count=0
    for n in MenuFiles:
        if count>=(page*maxpage) and count<(page*maxpage)+maxpage:
            try:
                test=MenuFiles[count]
                if index==count:
                    print("* ", end="")
                else:
                    print("  ", end="")
                print(test[:35])
            except:
                #out of range
                pass
        count=count+1

drawmenu(0,0)
selected = -1
while selected==-1:
    if button1.value==True and button2.value==False:
        #wait release button
        while button2.value==False:
            pass
        if index<len(MenuFiles)-1:
            index=index+1
            page=int(index/maxpage)
            drawmenu(page,index)
    if button1.value==False and button2.value==True:
        #wait release button
        while button1.value==False:
            pass
        if index>0:
            index=index-1
            page=int(index/maxpage)
            drawmenu(page,index)
    if button1.value==False and button2.value==False:
        selected=True
    time.sleep(0.1)
clearscreen()
print("Selected  : "+str(index)+ " > " + MenuFiles[index])
MemStore(MenuFiles[index])
time.sleep(0.5)
print("\r\n"*int(maxlines/2))
print("-------------   RESET   ------------")
print("\r\n"*int((maxlines/2)-2))
time.sleep(0.5)
microcontroller.reset()