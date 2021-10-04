"""
MagTag Boot app selector by BeBoX (c)2021
"""
#launcher code
import microcontroller, os, time, digitalio, board
from digitalio import DigitalInOut, Direction, Pull
btnA = DigitalInOut(board.D15)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP
try:
    boot=microcontroller.nvm[0:25] #get 25 bytes for boot to launch
    boot=boot.decode().strip()
except:
    boot="nothing"
print("boot in memory : "+boot)
time.sleep(2)
#wait 2 sec for press BtnA
if boot!="code.py":
    #there is a file to launh in memory
    #first set code.py for next boot
    if btnA.value==False:
        while btnA.value==False:
            pass
        Newboot=bytearray(("code.py"+" "*25).encode())
        print("change for code.py")
        microcontroller.nvm[0:25]=Newboot[0:25]
    else:
        print("Run "+boot)
        btnA.deinit() #free button A for next use
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
btnA.deinit() #free button A for next use
from adafruit_magtag.magtag import MagTag
magtag = MagTag(rotation=180)
BACKGROUND_BMP = "/bmps/fourboxesv_bg.bmp"
# ----------------------------
# Backgrounnd bitmap
# ----------------------------
magtag.graphics.set_background(BACKGROUND_BMP)
# ----------------------------
# define Layout
# ----------------------------
x=5
y=35
step=73
for n in range (0,4,1):
    magtag.add_text(text_position=(x,y+(n*step)),text_scale=1)
    magtag.set_text("Item "+str(n),n,False)
# ----------------------------
# Get files from root
# ----------------------------
ListFiles = os.listdir("/")
MenuFiles = []
for n in ListFiles:
    if n[-3:]==".py":
        #need to impove, file to not show in menu
        #exlude secrets.py and of course code.py
        if n!="secrets.py" and n!="code.py":
            MenuFiles.append(n)
#debug
print("Find "+str(len(MenuFiles))+ " Files")
NbItemPage=3
if round(len(MenuFiles)/NbItemPage)==len(MenuFiles)/NbItemPage:
    MaxPage=round(len(MenuFiles)/NbItemPage)
else:
    MaxPage=round(len(MenuFiles)/NbItemPage)+1
#debug
print("N° of page : "+str(MaxPage))
def ShowMenu(start):
    index=0
    for n in range(start, start+3,1):
        try:
            magtag.set_text(MenuFiles[n][:-3],index,False)
        except:
            magtag.set_text(" ",index,False)
        index += 1
    magtag.set_text("Next >>>",index,False)
    magtag.refresh()

page=0
ShowMenu(page)
while True:
    for i, b in enumerate(magtag.peripherals.buttons):
        if not b.value:
            if i<3:
                # App selected
                magtag.peripherals.neopixels[3-i]=(0,0,20)
                try:
                    print(MenuFiles[i+page])
                    MemStore(MenuFiles[i+page])
                    time.sleep(1)
                    microcontroller.reset()
                except:
                    print("Nothing")                   
            else:
                magtag.peripherals.neopixels[3-i]=(0,20,0)
                oldpage=page
                #next Page selected
                print(round(page/3))
                if round(page/3)<MaxPage-1:
                    page += 3
                else:
                    page=0
                if oldpage!=page:
                    ShowMenu(page)
            time.sleep(0.5)
            magtag.peripherals.neopixels[3-i]=(0,0,0)
    time.sleep(0.1)