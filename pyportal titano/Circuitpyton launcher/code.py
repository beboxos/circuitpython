"""
Circuitpython Launcher by BeBoX(c)2021
this is a simple touch launcher
initialy made for Adafruit PyPortal Titano
can be normaly ported to any circuitpython card
that support adafruit touchscreen library
in further version will add possibility to use
GPIO buttons.

contact :
email depanet at gmail.com
twitter : https://twitter.com/BeBoXoS

"""
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
    try:
        exec(open("./"+boot).read())
    except:
        print("error opening : " + boot)
time.sleep(1)
def MemStore(file):
    Newboot=bytearray((file+".py"+" "*25).encode())
    print("change for "+file+".py")
    microcontroller.nvm[0:25]=Newboot[0:25]    

# code.py boot selector by BeBoX
import board , displayio, adafruit_touchscreen
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_button import Button
from collections import namedtuple
Coords = namedtuple("Point", "x y")
# Settings
SCREEN_WIDTH = board.DISPLAY.width
SCREEN_HEIGHT = board.DISPLAY.height
BUTTON_WIDTH = int(SCREEN_WIDTH / 5) # was 60
BUTTON_HEIGHT = int(SCREEN_WIDTH / 10) # was 30
BUTTON_MARGIN = 8
MAX_DIGITS = 29
BLACK = 0x0
ORANGE = 0xFF8800
BLUE = 0x0088FF
WHITE = 0xFFFFFF
GRAY = 0x666666
LABEL_OFFSET = int(SCREEN_WIDTH - (SCREEN_WIDTH/7))
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(SCREEN_WIDTH, SCREEN_HEIGHT))

# Make the display context
calc_group = displayio.Group(max_size=25)
board.DISPLAY.show(calc_group)
# Make a background color fill
color_bitmap = displayio.Bitmap(SCREEN_WIDTH, SCREEN_HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = GRAY
bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
calc_group.append(bg_sprite)
board.DISPLAY.show(calc_group)
# Load the font
font = bitmap_font.load_font("/fonts/Arial-12.bdf")
# Title Font
font2 = bitmap_font.load_font("/fonts/Arial-Bold-24.bdf")
#Title
title = Label(font2, text="CircuitPython Launcher", color=BLACK)
title.y = 20
title.x = 47
title2 = Label(font2, text="CircuitPython Launcher", color=WHITE)
title2.y = 24
title2.x = 51
calc_group.append(title)
calc_group.append(title2)
board.DISPLAY.show(calc_group)

buttons = []

# Some button functions
def button_grid(row, col):
    return Coords(BUTTON_MARGIN * (row + 1) + BUTTON_WIDTH * row + 20,
                  BUTTON_MARGIN * (col + 1) + BUTTON_HEIGHT * col + 40)

def add_button(row, col, label, width=1, color=WHITE, text_color=BLACK):
    pos = button_grid(row, col)
    new_button = Button(x=pos.x, y=pos.y,
                        width=BUTTON_WIDTH * width + BUTTON_MARGIN * (width - 1),
                        height=BUTTON_HEIGHT, label=label, label_font=font,
                        label_color=text_color, fill_color=color, style=Button.ROUNDRECT)
    buttons.append(new_button)
    return new_button

def find_button(label):
    result = None
    for _, btn in enumerate(buttons):
        if btn.label == label:
            result = btn
    return result

ListFiles = os.listdir("/")
MenuFiles = []
for n in ListFiles:
    if n[-3:]==".py":
        #need to impove, file to not show in menu
        #exlude secrets.py and of course code.py
        if n!="secrets.py" and n!="code.py" and n!="calculator.py":
            MenuFiles.append(n)
#print(MenuFiles)
index = 0
def DrawMenu(start):
    col =0
    lig =0
    global index
    index = 0
    for n in MenuFiles:
        if index-start<9 and index>=start:
            print(MenuFiles[index]+" "+str(index)+" at "+str(col)+","+str(lig))
            add_button(col, lig, MenuFiles[index][:-3],2)
            if col==0:
                col=2
            else:
                col=0
                lig=lig+1
        index=index+1
                
    if index-start>9:
        add_button(2, 4, "Next ... "+str(int((index-start)/9)),2, ORANGE, WHITE)
    else:
        if start!=0:
            add_button(2, 4, "Next ... 0",2, ORANGE, WHITE)

    for b in buttons:
        calc_group.append(b)

#initial page
DrawMenu(0)
print(len(buttons))

board.DISPLAY.show(calc_group)
button = ""
while True:
    point = ts.touch_point
    if point is not None:
        # Button Down Events
        for _, b in enumerate(buttons):
            if b.contains(point) and button == "":
                b.selected = True
                button = b.label
                if button[:8]!="Next ...":
                    matching = [s for s in MenuFiles if button in s]
                    print(matching)
                    #time.sleep(100)
                    try:
                        MemStore(matching[0][:-3])
                        print (matching[0][:-3])
                        microcontroller.reset()
                    except:
                        print("error not found")
                else:
                    # Next button
                    b.selected = False
                    print("o-------------o")
                    page=int(button[-1])
                    for n in range(len(calc_group),2,-1):
                        try:
                            calc_group.pop(n)
                        except:
                            pass
                    buttons=[]
                    button = ""
                    DrawMenu(page*9)               
    elif button != "":
        # Button Up Events
        b = find_button(button)
        b.selected = False
        button = ""