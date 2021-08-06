import adafruit_ili9341
import displayio
import kfw_FeatherS2_board as board
import neopixel
neopix_pin = board.D11
pixels = neopixel.NeoPixel(neopix_pin, 1)
pixels[0] = 0x000000 #turn off neopixel
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
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
if is_usb == "NO USB":
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
    print('Free memory : ')
    import gc
    print( str(int((gc.mem_free()/1024))/1024)+" MB" )    
