import board
import terminalio
import displayio
import digitalio
import busio
from adafruit_display_text import label
from adafruit_st7789 import ST7789
import adafruit_dotstar as dotstar
import time
import rotaryio
import wifi
#audio
import array
import math
import audiocore
import audiobusio
sample_rate = 8000
tone_volume = 1  # Increase or decrease this to adjust the volume of the tone.
frequency = 440  # Set this to the Hz of the tone you want to generate.
length = sample_rate // frequency  # One freqency period
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = int((math.sin(math.pi * 2 * frequency * i / sample_rate) *
                        tone_volume + 1) * (2 ** 15 - 1))


#button & encoder
encoder = rotaryio.IncrementalEncoder(board.IO1, board.IO2)
last_position = None
button = digitalio.DigitalInOut(board.IO0) #  bouton central
button.switch_to_input(pull=digitalio.Pull.DOWN)
# True si relaché
# False si pressé
#RGB Leds
ledclk = board.IO45
leddata = board.IO42
lednumber = 7
led_strip = dotstar.DotStar(ledclk, leddata, lednumber, brightness=100)
#screen
displayio.release_displays()
tft_cs = board.IO10
tft_dc = board.IO13
tft_reset = board.IO9
tft_backlight = board.IO15
spi_clk = board.IO12
spi_mosi = board.IO11
tft_width = 320
tft_height = 170
spi = busio.SPI(spi_clk, spi_mosi)
while not spi.try_lock():
    pass
spi.configure(baudrate=24000000) # Configure SPI for 24MHz
spi.unlock()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = ST7789(display_bus, width=tft_width, height=tft_height, backlight_pin=tft_backlight, rotation=90, rowstart=0, colstart=35)
# Make the display context
splash = displayio.Group()
display.show(splash)
BORDER_WIDTH = 20
TEXT_SCALE = 5
# Draw a smaller inner black rectangle
inner_bitmap = displayio.Bitmap(
    display.width - (BORDER_WIDTH * 2), display.height - (BORDER_WIDTH * 2), 1
)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Purple
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER_WIDTH, y=BORDER_WIDTH
)
splash.append(inner_sprite)
# Draw a label
text_area = label.Label(
    terminalio.FONT,
    text="00 : 00",
    color=0xFFFFFF,
    scale=TEXT_SCALE,
    anchor_point=(0.5, 0.5),
    anchored_position=(display.width // 2, display.height // 2),
)
splash.append(text_area)
timeset = 60 # default to 60 sec

def countdown(t):
    while button.value == False:
        pass
    ref_time = time.monotonic()
    led = 0
    flag=-1
    while t>=0 and button.value:
        minutes = t // 60
        secondes = t % 60
        text_area.text = "{:02d}".format(minutes)+" : "+"{:02d}".format(secondes)
        if led==0:
            led_strip[6]=(0,0,0)
            led_strip[0]=(1,1,1)
        elif led==7:
            led=0
            led_strip[6]=(0,0,0)
            led_strip[0]=(1,1,1)
        else:
            led_strip[led-1]=(0,0,0)
            led_strip[led]=(1,1,1)       
        if secondes==0 and flag==-1:
            flag=-flag
            for n in range(0,7):
                led_strip[n]=(255,255,255)
            time.sleep(0.2)
            for n in range(0,7):
                led_strip[n]=(0,0,0)        
        if time.monotonic() - ref_time >= 1:
            t-=1
            text_area.text = "{:02d}".format(minutes)+" : "+"{:02d}".format(secondes)
            flag = -1
            ref_time = time.monotonic()
            led_strip[int(secondes // 9)]=(255,255,255)
            time.sleep(0.1)
            led_strip[int(secondes // 9)]=(0,0,0)
        time.sleep(0.006)
        led += 1
    for n in range(0,7):
        led_strip[n]=(0,0,0)
    
def set_time(timesetting):
    while button.value == False:
        pass
    encoder.position = int(timesetting/15)
    while button.value:
        time.sleep(0.1)
        position = encoder.position
        if position < 1:
            position = 1
            encoder.position = 1
        timesetting=position * 15
        minutes = timesetting // 60
        secondes = timesetting % 60
        text_area.text = "{:02d}".format(minutes)+" : "+"{:02d}".format(secondes)
    while not button.value:
        pass
    return timesetting

def beep(nb):
    audio = audiobusio.I2SOut(board.IO7, board.IO5, board.IO6)
    sine_wave_sample = audiocore.RawSample(sine_wave, sample_rate=sample_rate)
    while nb > 0:
        text_area.text = "00 : 00"
        audio.play(sine_wave_sample, loop=True)
        for n in range(0,7):
                led_strip[n]=(255,255,255)
        time.sleep(0.5)
        for n in range(0,7):
                led_strip[n]=(0,0,0)
        audio.stop()
        text_area.text ="   :   "
        time.sleep(0.5)
        nb -= 1
    audio.stop()
    audio.deinit()



while True:
    val = set_time(timeset)
    timeset=val
    countdown(timeset)
    beep(3)
    button.deinit()
    encoder.deinit()
    text_area.text = "00 : 00"
    time.sleep(1)
    encoder = rotaryio.IncrementalEncoder(board.IO1, board.IO2)
    button = digitalio.DigitalInOut(board.IO0) #  bouton central
    button.switch_to_input(pull=digitalio.Pull.DOWN)