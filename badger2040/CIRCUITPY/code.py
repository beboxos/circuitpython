'''
Original Launcher from pimoroni ported and modified for
CircuitPython by BeBoX(c)
email : depanet at gmail.com
twitter : @beboxos
edit from 03.2022
change log : add info
'''
import gc, os , math, microcontroller, digitalio, board, storage
import analogio, time, usb_hid
from adafruit_hid.keyboard import Keyboard
import adafruit_ducky, busio, displayio , terminalio , vectorio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon
import adafruit_miniqr
try:
    keyboard = Keyboard(usb_hid.devices)
    usb=True
except:
    usb=False
flag=False
#HID init

try :
    layout = microcontroller.nvm[0:2].decode() # 2 chars form nvm memory index 0
    #layout = layout.decode().strip()
    #print("Find "+layout+" in mémory")
except:
    layout = "fr" # fr or us fixed value if no data in memory
#print("Keyboard layout :"+layout)
try:    
    if usb==True:
        keyboard = Keyboard(usb_hid.devices)
        if layout=="fr": 
            from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
            keyboard_layout = KeyboardLayoutFR(keyboard)  # We're in France :)
            
        else:
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
            keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
except:
    print("error")
#hack set pin10 3V3 to high
pin3v3 = digitalio.DigitalInOut(microcontroller.pin.GPIO10)
pin3v3.direction = digitalio.Direction.OUTPUT
pin3v3.value = True

display = board.DISPLAY
display.rotation = 270
palette = displayio.Palette(1)
palette[0] = 0xFFFFFF
WHITE = 0xFFFFFF
BLACK = 0x000000
#usb=False
badgescn = displayio.Group()
showqr=False
IMAGE_WIDTH = 104
IMAGE_HEIGHT = 128
def fixlayout(lang):
    global usb, keyboard
    print("fixlayout usb =", end='')
    print(usb)
    try:
        keyboard = Keyboard(usb_hid.devices)
        usb=True
    except:
        usb=False
    layout=lang
    if usb==True:
        keyboard = Keyboard(usb_hid.devices)
        if lang=="fr": 
            from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
            keyboard_layout = KeyboardLayoutFR(keyboard)  # We're in France :)
            
        else:
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
            keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
        #usb=True
        #print(usb)
    else:
        print("not connected on usb")
        #usb=False
    return usb
    #print(tomem[0:2] + " / " + lang + "/" + layout)
        
def callduck(filename):
    if usb==True:
        duck = adafruit_ducky.Ducky(filename, keyboard, keyboard_layout)    
        result = True
        while result is not False:
            result = duck.loop()
    else:
        result = "No usb"
    return result
# button and led init
from digitalio import DigitalInOut, Direction, Pull
button_a = DigitalInOut(board.SW_A)
button_a.direction = Direction.INPUT
button_a.pull = Pull.DOWN
button_b = DigitalInOut(board.SW_B)
button_b.direction = Direction.INPUT
button_b.pull = Pull.DOWN
button_c = DigitalInOut(board.SW_C)
button_c.direction = Direction.INPUT
button_c.pull = Pull.DOWN
button_up = DigitalInOut(board.SW_UP)
button_up.direction = Direction.INPUT
button_up.pull = Pull.DOWN
button_down = DigitalInOut(board.SW_DOWN)
button_down.direction = Direction.INPUT
button_down.pull = Pull.DOWN
# False = up , True = pressed
led = DigitalInOut(board.USER_LED)
led.direction = Direction.OUTPUT
#led.value = 1 for led on
#led.value = 0 for led off

# led on
led.value = 1
# for later eventualy
# Inverted. For reasons.
button_user = board.USER_SW

# vars 
next_page = True
prev_page = False
last_offset = 0
current_page = 0
offsets = []

WIDTH = display.width
HEIGHT = display.height
ARROW_THICKNESS = 3
ARROW_WIDTH = 18
ARROW_HEIGHT = 14
ARROW_PADDING = 2
TEXT_PADDING = 4
TEXT_SIZE = 0.5
TEXT_SPACING = int(34 * TEXT_SIZE)
TEXT_WIDTH = WIDTH - TEXT_PADDING - TEXT_PADDING - ARROW_WIDTH
# fonts
font = bitmap_font.load_font("/fonts/Arial-12.bdf")
font2 = bitmap_font.load_font("/fonts/Arial-Bold-24.bdf")
font3=terminalio.FONT
#font_sizes = (0.5, 0.7, 0.9)

# Approximate center lines for buttons A, B and C
centers = (41, 147, 253)
MAX_BATTERY_VOLTAGE = 400
MIN_BATTERY_VOLTAGE = 320
batlvl = analogio.AnalogIn(board.VBAT_SENSE)
ebook=""
page = 0
font_size = 1
inverted = False
# scan files for HID scripts 
ListHIDFiles = os.listdir("/hid/")
hidfiles =[]
count = 0
for n in ListHIDFiles:
    if n[-4:]==".txt":
        if n[0:2]!="._":
            hidfiles.append((n.replace(".txt",""),count))
            count=count+1
hidfiles.append(("EXIT",count))
# scan files for badges files
files = os.listdir("/badges/")
bfiles = []
count = 0
for n in files:
    if n[-4:]==".txt":
        if n[0:2]!="._":
            bfiles.append((n.replace(".txt",""),count))
            count=count+1        
bfiles.append(("EXIT",count))
# can files for pictures files
files = os.listdir("/images/")
picfiles = []
count = 0
for n in files:
    if n[-4:]==".bmp":
        if n[0:2]!="._":
            picfiles.append((n.replace(".bmp",""),count))
            count=count+1        
picfiles.append(("EXIT",count))
# scan files for ebook/text files 
files = os.listdir("/ebook/")
ebfiles = []
count = 0
for n in files:
    if n[-4:]==".txt":
        if n[0:2]!="._":
            ebfiles.append((n.replace(".txt",""),count))
            count=count+1        
ebfiles.append(("EXIT",count))
# prefs menu
prefsdb= [("fr",0),("us",1),("EXIT",2)]
# main menu with extra functions scan in app folder
#fixed functions
examples = [
    ("keyb", 0),
    ("badge", 1),
    ("image", 2),
    ("ebook", 3),
    ("info", 4),
    ("prefs", 5)
]
count = 6
ListFiles = os.listdir("/apps/")
for n in ListFiles:
    if n[-3:]==".py":
        #need to impove, file to not show in menu
        #exlude secrets.py and of course code.py
        # remove f**cking files made by Mac os ._
        if n!="secrets.py" and n!="code.py"  and n[0:2]!="._":
            examples.append((n.replace(".py",""),count))
            count=count+1

# led off to tell init is done
led.value = 0
# Battery measurement
'''
vbat_adc = machine.ADC(badger2040.PIN_BATTERY)
vref_adc = machine.ADC(badger2040.PIN_1V2_REF)
vref_en = machine.Pin(badger2040.PIN_VREF_POWER)
vref_en.init(machine.Pin.OUT)
vref_en.value(0)


'''
#vbat_adc = analogio.AnalogIn(board.VBAT_SENSE)
#vref_adc = analogio.AnalogIn(board.1V2_REF)
vref_en = analogio.AnalogIn(board.VREF_POWER)

def read_le(s):
    # as of this writting, int.from_bytes does not have LE support, DIY!
    result = 0
    shift = 0
    for byte in bytearray(s):
        result += byte << shift
        shift += 8
    return result

def map_value(input, in_min, in_max, out_min, out_max):
    return (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min


def get_battery_level():
    # Enable the onboard voltage reference
    #vref_en.value
    # Calculate the logic supply voltage, as will be lower that the usual 3.3V when running off low batteries
    #vdd = 1.24 * (65535 / vref_adc.read_u16())
    #vbat = (vbat_adc.read_u16() / 65535) * 3 * vdd  # 3 in this is a gain, not rounding of 3.3V
    vbat=int((batlvl.value/100)+140)
    # Disable the onboard voltage reference
    #vref_en.value
    '''
    print(batlvl.value)
    print(MIN_BATTERY_VOLTAGE)
    print(MAX_BATTERY_VOLTAGE)
    print(vbat)
    print(int(map_value(vbat, MIN_BATTERY_VOLTAGE, MAX_BATTERY_VOLTAGE, 0, 4)))
    '''
    batlevel = label.Label(font=terminalio.FONT, text=str("{:.2f}v".format((batlvl.value/10000)+1)), color=WHITE, scale=1)
    batlevel.y = 7
    batlevel.x = 235
    mainScreen.append(batlevel)
    return int(map_value(vbat, MIN_BATTERY_VOLTAGE, MAX_BATTERY_VOLTAGE, 0, 4))


def draw_battery(level, x, y):
    mainScreen.append(Rect(x, y, 19, 10, fill=WHITE, outline=WHITE))
    mainScreen.append(Rect(x + 19, y + 3, 2, 4, fill=WHITE, outline=WHITE))
    mainScreen.append(Rect(x + 1, y + 1, 17, 8, fill=BLACK, outline=BLACK))
    if level < 1:
        mainScreen.append(Line(x + 3, y, x + 3 + 10, y + 10, BLACK))
        mainScreen.append(Line(x + 3 + 1, y, x + 3 + 11, y + 10, BLACK))
        mainScreen.append(Line(x + 2 + 2, y - 1, x + 4 + 12, y + 11, WHITE))
        mainScreen.append(Line(x + 2 + 3, y - 1, x + 4 + 13, y + 11, WHITE))
        return
    # Battery Bars
    for i in range(4):
        if level / 4 > (1.0 * i) / 4:
            mainScreen.append(Rect(i * 4 + x + 2, y + 2, 3, 6, fill=WHITE, outline=WHITE))
    
def showlayout(lang):
    #fixlayout(lang)
    print("usb = ",end="")
    print(usb)
    ltext = label.Label(font=terminalio.FONT, text=lang.upper(), color=WHITE, scale=1)
    ltext.y = 7
    ltext.x = 202
    mainScreen.append(ltext)
    '''
    image, palette = adafruit_imageload.load("/assets/icons/"+lang+".bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
    tile_grid = displayio.TileGrid(image, pixel_shader=palette)
    tile_grid.x = 200
    tile_grid.y = 0    
    mainScreen.append(tile_grid)
    '''



def usbconnected():
    global usb
    print("usb connected :",end='')
    print(usb)
    
    if usb==True:
        image, palette = adafruit_imageload.load("/assets/icons/usb.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)        
    else:
        image, palette = adafruit_imageload.load("/assets/icons/blank.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette) 
    tile_grid = displayio.TileGrid(image, pixel_shader=palette)
    tile_grid.x = 216
    tile_grid.y = 0    
    mainScreen.append(tile_grid)
    '''
    if usb==True:
        lang="U"
    else:
        lang=" "
    ltext = label.Label(font=terminalio.FONT, text=lang.upper(), color=WHITE, scale=1)
    ltext.y = 7
    ltext.x = 218
    mainScreen.append(ltext)
    '''
        
def draw_disk_usage(x):
    # f_bfree and f_bavail should be the same?
    # f_files, f_ffree, f_favail and f_flag are unsupported.
    f_bsize, f_frsize, f_blocks, f_bfree, _, _, _, _, _, f_namemax = os.statvfs("/")
    f_total_size = f_frsize * f_blocks
    f_total_free = f_bsize * f_bfree
    f_total_used = f_total_size - f_total_free
    f_used = 100 / f_total_size * f_total_used
    # f_free = 100 / f_total_size * f_total_free
    batbg = Rect(x + 10, 3, 80, 10, fill=BLACK, outline=WHITE)
    batlvl1 = Rect(x + 11, 4, 78, 8, fill=BLACK, outline=BLACK)
    batlvl2 = Rect(x + 12, 5, int(76 / 100.0 * f_used), 6, fill=WHITE, outline=WHITE)
    battxt = label.Label(font=terminalio.FONT, text="{:.0f}%".format(f_used), color=WHITE, scale=1)
    battxt.x = x + 91
    battxt.y = 7
    mainScreen.append(batbg)     #ID3
    mainScreen.append(batlvl1)   #ID4
    mainScreen.append(batlvl2)   #ID5
    mainScreen.append(battxt)    #ID6

# ********************************* groups definition ******************************
mainScreen = displayio.Group()
whiteBG = vectorio.Rectangle(pixel_shader=palette, width=display.width+1, height=display.height, x=0, y=0)
topbar = Rect(0, 0, display.width, 16, fill=BLACK, outline=BLACK)
title = label.Label(font=terminalio.FONT, text="BadgerOS CPython", color=WHITE, scale=1)
title.y = 7
title.x = 3


mainScreen.append(whiteBG) #ID0
mainScreen.append(topbar)  #ID1
mainScreen.append(title)   #ID2
draw_disk_usage(90)
fixlayout(layout) # check if usb is connected
ebgroup = displayio.Group()
# *******************************************************************************


def render(tablist, defaulticon="file"):
    global usb
    groupbefore=len(mainScreen)
    MAX_PAGE = math.ceil(len(tablist) / 3)
    led.value = 1
    max_icons = min(3, len(tablist[(page * 3):]))
    for i in range(max_icons):
        x = centers[i]
        labels, icon = tablist[i + (page * 3)]
        file = labels
        try:
            image, palette = adafruit_imageload.load("/assets/"+file+".bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        except:
            image, palette = adafruit_imageload.load("/assets/"+defaulticon+".bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        
        tile_grid = displayio.TileGrid(image, pixel_shader=palette)
        tile_grid.x = x-32
        tile_grid.y = 24
        mainScreen.append(tile_grid)
        labelicn = label.Label(font, text=labels[:5].upper(), color=BLACK, scale=1)
        w = 50 # 30 seem correct for default font 5x8
        labelicn.x =  x - int(w / 2)
        labelicn.y =  16 + 80
        mainScreen.append(labelicn)
    
    for i in range(MAX_PAGE):
        x = 286
        y = int((128 / 2) - (MAX_PAGE * 10 / 2) + (i * 10))
        if page != i:
            spot = Rect(x, y, 8, 8, fill=WHITE, outline=BLACK)
            mainScreen.append(spot)
        else:
            spot = Rect(x, y, 8, 8, fill=BLACK, outline=BLACK)
            mainScreen.append(spot)    
    draw_battery(get_battery_level(), WIDTH - 22 - 3, 3)
    showlayout(layout)
    print("On render usb =",end='')
    print(usb)
    usbconnected()
    display.show(mainScreen)

    while display.busy==True:
        time.sleep(0.01)     
    display.refresh()
    groupafter=len(mainScreen)
    for i in range(groupbefore,groupafter):
        mainScreen.pop()
    led.value = 0


def launch(file):
    fichier = "/apps/"+file+".py"
    for k in locals().keys():
        if k not in ("gc", "file", "machine"):
            del locals()[k]
    gc.collect()
    try:
        __import__(fichier)  # Try to import _[file] (drop underscore prefix)
    except ImportError:
        pass
    import microcontroller
    microcontroller.reset()

def prefs():
    global page, usb,prefsdb
    print("prefs selection on mainscreen")
    #prefs in lazy way
    before=len(mainScreen)
    page=0
    ex=False
    render(prefsdb,"keyb")
    while ex==False:
        if button_a.value==True:
            led.value=1
            while button_a.value==True:
                pass               
            fixlayout("fr")
            lang="fr"
            tomem=bytearray(lang.encode())
            microcontroller.nvm[0:2]=tomem[0:2]            
            ex=True
            led.value=0
            microcontroller.reset()
        if button_b.value==True:
            led.value=1
            while button_b.value==True:
                pass               
            fixlayout("us")
            lang="us"
            tomem=bytearray(lang.encode())
            microcontroller.nvm[0:2]=tomem[0:2]            
            ex=True
            led.value=0
            microcontroller.reset()
        if button_c.value==True:
            led.value=1
            while button_c.value==True:
                pass               
            ex=True
            led.value=0            
    # work zone
    after=len(mainScreen)

# important root routine ------------------------------------------------------------
def launch_example(index):
    global page, font_size, inverted, flag
    #print("index : "+str(index))
    #print(examples[(page * 3) + index][0])
    if (page * 3) + index == 0:
        hidexit=False
        led.value=1
        if flag==False:
            fixlayout(layout)
            flag=True
        led.value=0
        #special action rubber ducky
        while button_a.value==True:
            time.sleep(0.01)
        # keyb
        print("Keyboard emul zone")
        render(hidfiles,"text")
        while hidexit==False:
            if button_a.value==True:
                while button_a.value==True:
                    time.sleep(0.01)
                if hidbutton(1)==False:
                    hidexit=True
            if button_b.value==True:
                while button_b.value==True:
                    time.sleep(0.01)                
                if hidbutton(2)==False:
                    hidexit=True
            if button_c.value==True:
                while button_c.value==True:
                    time.sleep(0.01)                
                if hidbutton(3)==False:
                    hidexit=True
            if button_up.value==True:
                hidbutton(4)
            if button_down.value==True:
                hidbutton(5)            
            time.sleep(0.01)
        page=0
        flag=False
        render(examples,"file")
        return
    if (page * 3) + index == 1:
        #badge section
        badgeexit=False
        while button_b.value==True:
            time.sleep(0.01)
        print("badge zone")
        
        render(bfiles,"userid")
        while badgeexit==False:
            if button_a.value==True:
                while button_a.value==True:
                    time.sleep(0.01)
                if badgebutton(1)==False:
                    badgeexit=True
            if button_b.value==True:
                while button_b.value==True:
                    time.sleep(0.01)                
                if badgebutton(2)==False:
                    badgeexit=True
            if button_c.value==True:
                while button_c.value==True:
                    time.sleep(0.01)                
                if badgebutton(3)==False:
                    badgeexit=True
            if button_up.value==True:
                badgebutton(4)
            if button_down.value==True:
                badgebutton(5)            
            time.sleep(0.01)
        page=0
        render(examples,"file")
        return            
    if (page * 3) + index == 2:
        # show image routine
        imgexit=False
        oldpage=page
        while button_b.value==True:
            time.sleep(0.01)
        print("image zone")
        
        render(picfiles,"bmp")
        while imgexit==False:
            if button_a.value==True:
                while button_a.value==True:
                    time.sleep(0.01)
                if imgbutton(1)==False:
                    imgexit=True
            if button_b.value==True:
                while button_b.value==True:
                    time.sleep(0.01)                
                if imgbutton(2)==False:
                    imgexit=True
            if button_c.value==True:
                while button_c.value==True:
                    time.sleep(0.01)                
                if imgbutton(3)==False:
                    imgexit=True
            if button_up.value==True:
                imgbutton(4)
            if button_down.value==True:
                imgbutton(5)            
            time.sleep(0.01)
        page=oldpage
        render(examples,"file")
        return         
    if (page * 3) + index == 3:
        # ebook Reader function
        ebexit=False
        oldpage = 1
        page = 0
        while button_a.value==True:
            time.sleep(0.01)
        print("ebook zone")
        print(ebfiles)
        render(ebfiles,"text")
        print("rendered")
        while ebexit==False:
            if button_a.value==True:
                while button_a.value==True:
                    time.sleep(0.01)
                if ebookbutton(1)==False:
                    ebexit=True
            if button_b.value==True:
                while button_b.value==True:
                    time.sleep(0.01)                
                if ebookbutton(2)==False:
                    ebexit=True
            if button_c.value==True:
                while button_c.value==True:
                    time.sleep(0.01)                
                if ebookbutton(3)==False:
                    ebexit=True
            if button_up.value==True:
                ebookbutton(4)
            if button_down.value==True:
                ebookbutton(5)            
            time.sleep(0.01)        
        # back to main
        print('exit ebook')
        try:
            ebook.close()
        except:
            print("ebook allready closed")
        page=1
        render(examples,"file")
        return          
    if (page * 3) + index == 4:
        # info
        print("infos ...")
        old=len(mainScreen)
        LINE_HEIGHT = 16
        y = 16 + int(LINE_HEIGHT / 2)
        labelt = label.Label(font3, text="Made by Pimoroni, powered by Circuitpython", color=BLACK, scale=1)
        labelt.x =  0
        labelt.y =  y
        mainScreen.append(labelt)
        y += LINE_HEIGHT
        labelt = label.Label(font3, text="Dual-core RP2040, 133MHz, 264KB RAM", color=BLACK, scale=1)
        labelt.x =  0
        labelt.y =  y
        mainScreen.append(labelt)
        y += LINE_HEIGHT
        labelt = label.Label(font3, text="2MB Flash (1MB OS, 1MB Storage)", color=BLACK, scale=1)
        labelt.x =  0
        labelt.y =  y
        mainScreen.append(labelt)
        y += LINE_HEIGHT
        labelt = label.Label(font3, text="296x128 pixel Black/White e-Ink", color=BLACK, scale=1)
        labelt.x =  0
        labelt.y =  y
        mainScreen.append(labelt)
        y += LINE_HEIGHT
        y += LINE_HEIGHT
        labelt = label.Label(font3, text="For more info: https://pimoroni.com/badger2040", color=BLACK, scale=1)
        labelt.x =  0
        labelt.y =  y
        mainScreen.append(labelt)
        y += LINE_HEIGHT
        labelt = label.Label(font3, text="Launcher made by BeBox inspired by original. v1.0", color=BLACK, scale=1)
        labelt.x =  0
        labelt.y =  y
        mainScreen.append(labelt)
        display.show(mainScreen)
        while display.busy==True:
            time.sleep(0.01)         
        display.refresh()
        new=len(mainScreen)
        for i in range(old, new):
            mainScreen.pop()
        while button_a.value==False and button_b.value==False and button_c.value==False and button_up.value==False and button_down.value==False:
            led.value=1
            time.sleep(0.5)
            led.value=0
            time.sleep(0.5)
        render(examples,"file")    
        return
    if (page * 3) + index == 5:
        # prefs
        print("prefs ...")
        oldpage=page
        prefs()
        page=oldpage
        render(examples,"file")  
        
        return
    else:    
        try:
            print(examples[(page * 3) + index][0])
            launch(examples[(page * 3) + index][0])
            return True
        except IndexError:
            return False

def ebookbutton(pin):
    global page, font_size, inverted
    #if button_user.value():  # User button is NOT held down
    print("ebook bouton : "+str(pin))
    if pin == 1:
        if ebselect(0)==False:
            return False
    if pin == 2:
        if ebselect(1)==False:
            return False
    if pin == 3:
        if ebselect(2)==False:
            return False
    if pin == 4:
        MAX_PAGE = math.ceil(len(bfiles) / 3)
        if page > 0:
            page -= 1
            render(ebfiles,"text")
    if pin == 5:
        MAX_PAGE = math.ceil(len(bfiles) / 3)
        if page < MAX_PAGE - 1:
            page += 1
            render(ebfiles,"text")

def ebselect(index):
    global page, font_size, inverted
    try:
        name = ebfiles[(page * 3) + index][0]
        print("/ebook/"+name+".txt")
        if name == "EXIT":
            return False
        else:
            #wait release
            while button_a.value==True or button_b.value==True or button_c.value==True:
                time.sleep(0.01) 
            # ici
            ebookfile= "/ebook/"+name+".txt"
            readebook(ebookfile)                      
            render(ebfiles,"text")
            return True   
    except:
        print("Error in button selection")
def readebook(efile):
    global next_page, prev_page,last_offset,current_page, ebook
    print("go to read" + efile + " ebook")
    ebook = open(efile, "r")
    #goup is ebgroup, draw frame only one time :)
    draw_frame()
    while True:
        # Was the next page button pressed?
        if next_page:
            current_page += 1

            # Is the next page one we've not displayed before?
            if current_page > len(offsets):
                offsets.append(ebook.tell())  # Add its start position to the offsets list
            led.value=1
            #draw_frame()
            render_page()
            led.value=0
            next_page = False  # Clear the next page button flag

        # Was the previous page button pressed?
        if prev_page:
            if current_page > 1:
                current_page -= 1
                ebook.seek(offsets[current_page - 1])  # Retrieve the start position of the last page
                led.value=1
                #draw_frame()
                render_page()
                led.value=0
            prev_page = False  # Clear the prev page button flag
        if button_a.value==True:
            return True
        if button_b.value==True:
            return True
        if button_c.value==True:
            return True
        if button_up.value==True:
            while button_up.value==True:
                time.sleep(0.01)
            ebbutton(4)
        if button_down.value==True:
            while button_down.value==True:
                time.sleep(0.01)        
            ebbutton(5)
        time.sleep(0.1)    

def imgbutton(pin):
    global page, font_size, inverted
    #if button_user.value():  # User button is NOT held down
    if pin == 1:
        if img(0)==False:
            return False
    if pin == 2:
        if img(1)==False:
            return False
    if pin == 3:
        if img(2)==False:
            return False
    if pin == 4:
        MAX_PAGE = math.ceil(len(picfiles) / 3)
        if page > 0:
            page -= 1
            render(picfiles,"bmp")
    if pin == 5:
        MAX_PAGE = math.ceil(len(picfiles) / 3)
        if page < MAX_PAGE - 1:
            page += 1
            render(picfiles,"bmp")

def img(index):
    try:
        name = picfiles[(page * 3) + index][0]
        print("/image/"+name+".bmp")
        if name == "EXIT":
            return False
        else:
            #wait release
            while button_a.value==True or button_b.value==True or button_c.value==True:
                time.sleep(0.01) 
            led.value=1
            # ici
            mainScreen.append(Rect(0, 0, display.width +1, display.height, fill=WHITE, outline=WHITE))
            image, palette = adafruit_imageload.load("/images/"+name+".bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
            tile_grid = displayio.TileGrid(image, pixel_shader=palette)
            tile_grid.x = 0
            tile_grid.y = 0
            mainScreen.append(tile_grid)
            display.show(mainScreen)
            display.refresh()
            mainScreen.pop() #kill pic
            mainScreen.pop() #kill whiteBG
            led.value=0
            #wait a a b or c button
            while button_a.value==False and button_b.value==False and button_c.value==False:
                time.sleep(0.01)            
            #wait release
            while button_a.value==True or button_b.value==True or button_c.value==True:
                time.sleep(0.01)                         
            render(picfiles,"bmp")
            return True
    except:
        print("wrong selection")

def badgebutton(pin):
    global page, font_size, inverted
    #if button_user.value():  # User button is NOT held down
    if pin == 1:
        if badge(0)==False:
            return False
    if pin == 2:
        if badge(1)==False:
            return False
    if pin == 3:
        if badge(2)==False:
            return False
    if pin == 4:
        MAX_PAGE = math.ceil(len(bfiles) / 3)
        if page > 0:
            page -= 1
            render(bfiles,"userid")
    if pin == 5:
        MAX_PAGE = math.ceil(len(bfiles) / 3)
        if page < MAX_PAGE - 1:
            page += 1
            render(bfiles,"userid")

def badge(index):
    global showqr
    try:
        name = bfiles[(page * 3) + index][0]
        print("/badge/"+name+".txt")
        if name == "EXIT":
            #hidexit=True
            return False
        else:
            #wait release
            while button_a.value==True or button_b.value==True or button_c.value==True:
                time.sleep(0.01) 
            led.value=1
            draw_badge(name)
            led.value=0
            #wait a a b or c button
            while button_a.value==False and button_b.value==False and button_c.value==False:
                if button_up.value==True:
                    while button_up.value==True:
                        time.sleep(0.01)
                    led.value=1
                    showqr=False
                    print(showqr)
                    draw_badge(name)
                    led.value=0
                if button_down.value==True:
                    while button_down.value==True:
                        time.sleep(0.01)
                    led.value=1
                    showqr=True
                    print(showqr)
                    draw_badge(name)
                    led.value=0
                time.sleep(0.01)            
            #wait release
            while button_a.value==True or button_b.value==True or button_c.value==True:
                time.sleep(0.01)                         
            render(bfiles,"userid")
            showqr=False
    except:
        print("Error in badge selection")
    return True


def hid(index):
    try:
        name = hidfiles[(page * 3) + index][0]
        print("/hid/"+name+".txt")
        if name == "EXIT":
            hidexit=True
            return False
        else:
            led.value=1
            callduck("/hid/"+name+".txt")
            led.value=0
            return True
    except:
        print("wrong selection")
        for n in range(0,20):
            led.value=1
            time.sleep(0.1)
            led.value=0
            time.sleep(0.1)

def hidbutton(pin):
    global page, font_size, inverted, usb, layout, flag
    #if button_user.value():  # User button is NOT held down
    if pin == 1:
        if hid(0)==False:
            return False
    if pin == 2:
        if hid(1)==False:
            return False
    if pin == 3:
        if hid(2)==False:
            return False
    if pin == 4:
        MAX_PAGE = math.ceil(len(hidfiles) / 3)
        if page > 0:
            page -= 1
            render(hidfiles,"text")
    if pin == 5:
        MAX_PAGE = math.ceil(len(hidfiles) / 3)
        if page < MAX_PAGE - 1:
            page += 1
            render(hidfiles,"text")

def button(pin):
    global page, font_size, inverted
    #print( "button pin : "+ str(pin))
    #if button_user.value():  # User button is NOT held down
    if pin == 1:
        launch_example(0)
    if pin == 2:
        launch_example(1)
    if pin == 3:
        launch_example(2)
    if pin == 4:
        MAX_PAGE = math.ceil(len(examples) / 3)
        if page > 0:
            page -= 1
            render(examples)
        else:
            page= MAX_PAGE -1
            render(examples)
    if pin == 5:
        MAX_PAGE = math.ceil(len(examples) / 3)
        if page < MAX_PAGE - 1:
            page += 1
            render(examples)
        else:
            page=0
            render(examples)

def draw_badge(file):
    global showqr
    print(showqr)
    #Constants cans be customised
    
    COMPANY_HEIGHT = 40
    DETAILS_HEIGHT = 20
    NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
    TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 2
    LEFT_PADDING = 5
    NAME_PADDING = 10
    DETAIL_SPACING = 20
    OVERLAY_BORDER = 40
    OVERLAY_SPACING = 20    
    if showqr==False:
        try:
            image, palette = adafruit_imageload.load("/badges/"+file+".bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        except:
            image, palette = adafruit_imageload.load("/badges/user.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        tile_grid = displayio.TileGrid(image, pixel_shader=palette)
        tile_grid.x = display.width - IMAGE_WIDTH 
        tile_grid.y = 0    
    f = open("/badges/"+file+".txt","r")
    company = f.readline()
    name = f.readline()
    detail1_title = f.readline()
    detail1_text = f.readline()
    detail2_title = f.readline()
    detail2_text = f.readline()
    f.close()    
    # clear scren (black)
    badgescn.append(Rect(0, 0, display.width+1, display.height, fill=BLACK, outline=BLACK))   #ID 
    # Draw a border around the image
    badgescn.append(Line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0, WHITE))
    badgescn.append(Line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1, WHITE))
    badgescn.append(Line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1, WHITE))
    badgescn.append(Line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1, WHITE))
    # Draw the company
    ctxt=label.Label(font=font2, text=company, color=WHITE, scale=1)
    ctxt.x = LEFT_PADDING
    ctxt.y = (COMPANY_HEIGHT // 2) 
    badgescn.append(ctxt)

    # Draw a white background behind the name
    badgescn.append(Rect(1, COMPANY_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT, fill=WHITE, outline=WHITE))
    # Draw the name, scaling it based on the available width
    fsize = 3 
    name_length = len(name)*(fsize*12)
    if name_length >= (TEXT_WIDTH - NAME_PADDING):
        fsize=2
        name_length = len(name)*(fsize*6)
        if name_length >= (TEXT_WIDTH - NAME_PADDING):
            fsize=1
            name_length = len(name)*(fsize*6)  
    name_length = len(name)*18
    ntxt=label.Label(font=font2, text=name, color=BLACK, scale=1)
    ntxt.x = (TEXT_WIDTH - name_length) // 2
    ntxt.y = (NAME_HEIGHT // 2) + COMPANY_HEIGHT 
    badgescn.append(ntxt)
    # Draw a white backgrounds behind the details
    badgescn.append(Rect(1, HEIGHT - DETAILS_HEIGHT * 2, TEXT_WIDTH, DETAILS_HEIGHT - 1, fill=WHITE, outline=WHITE))
    badgescn.append(Rect(1, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH, DETAILS_HEIGHT - 1, fill=WHITE, outline=WHITE))
    # Draw the first detail's title and text
    name_length = len(detail1_title)*8
    ntxt=label.Label(font=font, text=detail1_title, color=BLACK, scale=1)
    ntxt.x = LEFT_PADDING 
    ntxt.y = HEIGHT - ((DETAILS_HEIGHT * 3) // 2) 
    badgescn.append(ntxt)    
    ntxt=label.Label(font=font, text=detail1_text, color=BLACK, scale=1)
    ntxt.x = LEFT_PADDING + name_length + DETAIL_SPACING
    ntxt.x = 97
    ntxt.y = HEIGHT - ((DETAILS_HEIGHT * 3) // 2) 
    badgescn.append(ntxt)    
    # Draw the second detail's title and text
    name_length = len(detail2_title)*8
    ntxt=label.Label(font=font, text=detail2_title, color=BLACK, scale=1)
    ntxt.x = LEFT_PADDING
    ntxt.y = HEIGHT - (DETAILS_HEIGHT // 2) 
    badgescn.append(ntxt)      
    ntxt=label.Label(font=font, text=detail2_text, color=BLACK, scale=1)
    ntxt.x = LEFT_PADDING + name_length + DETAIL_SPACING
    ntxt.x = 97
    ntxt.y = HEIGHT - (DETAILS_HEIGHT // 2) 
    badgescn.append(ntxt)      
    # Draw badge image
    if showqr==False:
        print("Show pic")
        badgescn.append(tile_grid)
    else:
        print("show QR")
        badgeQR(file)
    display.show(badgescn)
    display.refresh()
    for i in range(0, len(badgescn)):
        badgescn.pop()

def bitmap_QR(matrix):
    # monochome (2 color) palette
    BORDER_PIXELS = 2

    # bitmap the size of the screen, monochrome (2 colors)
    bitmap = displayio.Bitmap(
        matrix.width + 2 * BORDER_PIXELS, matrix.height + 2 * BORDER_PIXELS, 2
    )
    # raster the QR code
    for y in range(matrix.height):  # each scanline in the height
        for x in range(matrix.width):
            if matrix[x, y]:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 1
            else:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 0
    return bitmap

def badgeQR(file):
    f = open("/badges/"+file+".txt","r")
    company = f.readline()
    name = f.readline()
    detail1_title = f.readline()
    detail1_text = f.readline()
    detail2_title = f.readline()
    detail2_text = f.readline()
    telfix = f.readline()
    telmob = f.readline()
    email = f.readline()
    site = f.readline().strip()
    f.close()
    texte="BEGIN:VCARD\n"
    texte+="N:"+name.strip()+";\n"
    texte+="TEL;TYPE=work:"+telfix.strip()+"\n"
    texte+="TEL;TYPE=cell:"+telmob.strip()+"\n"
    texte+="EMAIL;TYPE=work:"+email.strip()+"\n"
    texte+="ORG:"+company.strip()+"\n"
    texte+="TITLE:"+detail1_title.strip()+" "+detail1_text.strip()+"\n"
    texte+="NOTE:"+detail2_title.strip()+" "+detail2_text.strip()+"\n"
    #texte+="ADR;Type=WORK:"+adr+"\n"
    texte+="URL:"+site+"\n"
    texte+="VERSION:3.0\nEND:VCARD\n"
    print(texte)
    print(len(texte))
    #depart=len(badgescn)
    qr = adafruit_miniqr.QRCode(qr_type=9, error_correct=adafruit_miniqr.L)
    qr.add_data(texte.encode('ascii'))
    qr.make()
    qr_bitmap = bitmap_QR(qr.matrix)
    badgescn.append(Rect((display.width - IMAGE_WIDTH), 0, IMAGE_WIDTH, IMAGE_HEIGHT, fill=WHITE, outline=WHITE))
    scale = min(
    board.DISPLAY.width // qr_bitmap.width, board.DISPLAY.height // qr_bitmap.height
)
    
    pos_x = (display.width - IMAGE_WIDTH)+int((display.width-(display.width - IMAGE_WIDTH)-qr_bitmap.width)/2)
    pos_y = int((display.height-qr_bitmap.height)/2)
    badgescn.append(Rect(pos_x, pos_y, IMAGE_WIDTH, IMAGE_HEIGHT, fill=WHITE, outline=WHITE))
    qr_img = displayio.TileGrid(qr_bitmap, pixel_shader=palette, x=pos_x, y=pos_y)
    print(qr_bitmap.width)
    print(qr_bitmap.height)
    badgescn.append(qr_img)
    #display.show(badgescn)
    #display.refresh()
    #fin=len(badgescn)
    #for i in range(depart,fin):
    #    badgescn.pop()
        
# Draw a upward arrow
def draw_up(x, y, width, height, thickness, padding):
    border = (thickness // 4) + padding
    ebgroup.append(Line(x + border, y + height - border,
                 x + (width // 2), y + border, WHITE))
    ebgroup.append(Line(x + (width // 2), y + border,
                 x + width - border, y + height - border, WHITE))
# Draw a downward arrow
def draw_down(x, y, width, height, thickness, padding):
    border = (thickness // 2) + padding
    ebgroup.append(Line(x + border, y + border,
                 x + (width // 2), y + height - border, WHITE))
    ebgroup.append(Line(x + (width // 2), y + height - border,
                 x + width - border, y + border, WHITE))

# Draw the frame of the text reader
def draw_frame():
    ebgroup.append(Rect(0, 0, display.width +1, display.height, fill=WHITE, outline=WHITE))
    ebgroup.append(Rect(WIDTH - ARROW_WIDTH, 0, ARROW_WIDTH +1, HEIGHT, fill=BLACK, outline=BLACK))
    draw_up(WIDTH - ARROW_WIDTH, (HEIGHT // 4) - (ARROW_HEIGHT // 2),
                ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
    draw_down(WIDTH - ARROW_WIDTH, ((HEIGHT * 3) // 4) - (ARROW_HEIGHT // 2),
              ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)


def ebbutton(pin):
    global next_page, prev_page, change_font_size, change_font
    if pin == 5:
        next_page = True

    if pin == 4:
        prev_page = True
# ------------------------------
#         Render page
# ------------------------------

def render_page():
    global next_page, prev_page, change_font_size, change_font, ebook
    inipop = len(ebgroup)
    row = 0
    line = ""
    pos = ebook.tell()
    next_pos = pos
    add_newline = False
    led.value=1
    while True:
        # Read a full line and split it into words
        words = ebook.readline().split(" ")

        # Take the length of the first word and advance our position
        next_word = words[0]
        if len(words) > 1:
            next_pos += len(next_word) + 1
        else:
            next_pos += len(next_word)  # This is the last word on the line

        # Advance our position further if the word contains special characters
        if '\u201c' in next_word:
            next_word = next_word.replace('\u201c', '\"')
            next_pos += 2
        if '\u201d' in next_word:
            next_word = next_word.replace('\u201d', '\"')
            next_pos += 2
        if '\u2019' in next_word:
            next_word = next_word.replace('\u2019', '\'')
            next_pos += 2

        # Rewind the file back from the line end to the start of the next word
        ebook.seek(next_pos)

        # Strip out any new line characters from the word
        next_word = next_word.strip()

        # If an empty word is encountered assume that means there was a blank line
        if len(next_word) == 0:
            add_newline = True

        # Append the word to the current line and measure its length
        appended_line = line
        if len(line) > 0 and len(next_word) > 0:
            appended_line += " "
        appended_line += next_word
        appended_length = len(appended_line)*6

        # Would this appended line be longer than the text display area, or was a blank line spotted?
        if appended_length >= TEXT_WIDTH or add_newline:

            # Yes, so write out the line prior to the append
            print(line)
            title = label.Label(font=terminalio.FONT, text=line, color=BLACK, scale=1)
            title.y = (row * TEXT_SPACING) + (TEXT_SPACING // 2) + TEXT_PADDING
            title.x = TEXT_PADDING
            ebgroup.append(title)
            # Clear the line and move on to the next row
            line = ""
            row += 1

            # Have we reached the end of the page?
            if (row * TEXT_SPACING) + TEXT_SPACING >= HEIGHT:
                print("+++++")
                endpop=len(ebgroup)
                display.show(ebgroup)
                display.refresh()
                # pop lines for later :)
                for lp in range(inipop,endpop):
                    ebgroup.pop()
                # Reset the position to the start of the word that made this line too long
                ebook.seek(pos)
                return
            else:
                # Set the line to the word and advance the current position
                line = next_word
                pos = next_pos

            # A new line was spotted, so advance a row
            if add_newline:
                print("")
                row += 1
                if (row * TEXT_SPACING) + TEXT_SPACING >= HEIGHT:
                    print("+++++")
                    endpop=len(ebgroup)
                    display.show(ebgroup)
                    while display.busy==True:
                        time.sleep(0.01)
                    display.refresh()
                    # pop lines for later :)
                    for lp in range(inipop,endpop):
                        ebgroup.pop()
                    return
                add_newline = False
        else:
            # The appended line was not too long, so set it as the line and advance the current position
            line = appended_line
            pos = next_pos

# instant rubber ducky function if connected on usb at boot off course
# try if button a b c ... pressed at boot
# launch script with name of button if present a.txt b.txt etc ..
# special pentest
fixlayout(layout)
if usb==True:
    pressed=False
    if button_a.value==True:
        led.value=1
        print("wait release a button to type text")
        while button_a.value==True:
            pass   
        pressed=True
        try:
            x = open("a.txt","r")
            x.close()
            print("running script in a.txt")
            callduck("a.txt")
        except:
            print("button a pressed but no a.txt present, continue ...")
        led.value=0
    if button_b.value==True:
        led.value=1
        print("wait release b button to type text")
        while button_b.value==True:
            pass   
        pressed=True
        try:
            x = open("b.txt","r")
            x.close()
            print("running script in b.txt")
            callduck("b.txt")
        except:
            print("button b pressed but no b.txt present, continue ...")
        led.value=0
    if button_c.value==True:
        led.value=1
        print("wait release c button to type text")
        while button_c.value==True:
            pass   
        pressed=True
        try:
            x = open("c.txt","r")
            x.close()
            print("running script in c.txt")
            callduck("c.txt")
        except:
            print("button c pressed but no c.txt present, continue ...")
        led.value=0
    if button_up.value==True:
        led.value=1
        print("wait release up button to type text")
        while button_up.value==True:
            pass   
        pressed=True
        try:
            x = open("up.txt","r")
            x.close()
            print("running script in up.txt")
            callduck("up.txt")
        except:
            print("button up pressed but no up.txt present, continue ...")
        led.value=0    
    if button_down.value==True:
        led.value=1
        print("wait release down button to type text")
        while button_down.value==True:
            pass   
        pressed=True
        try:
            x = open("down.txt","r")
            x.close()
            print("running script in down.txt")
            callduck("down.txt")        
        except:
            print("button down pressed buy no down.txt present, continue ...")
        led.value=0   

    if pressed==True:
        # ok need to press a key to continue , or unplug to not change display
        print("Now you can unplug Badger2040 or press a button to continue on launcher")
        while button_a.value==False and button_b.value==False and button_c.value==False and button_up.value==False and button_down.value==False:
            led.value=1
            time.sleep(0.5)
            led.value=0
            time.sleep(0.5)


#let's display something 
render(examples, "files")
'''
# Wait for wakeup button to be released
while button_a.value==True or button_b.value==True or button_c.value==True or button_up.value==True or button_down.value==True:
    pass
'''
# main loop root 
while True:
    if button_a.value==True:
        button(1)
    if button_b.value==True:
        button(2)
    if button_c.value==True:
        button(3)
    if button_up.value==True:
        button(4)
    if button_down.value==True:
        button(5)
    time.sleep(0.01)
