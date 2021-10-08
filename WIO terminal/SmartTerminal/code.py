"""
Wio Smart terminal for PI by BeBoX
"""
for i in range(12):
    print()
print("Welcome to Wio Smart Terminal For Pi zero")
print("by BeBoX (c) 2021")
print("*"*50)
for i in range(6):
    print()
import board, time
import busio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
# Flag for CardKB
M5CardKB=True
# Hardware COnfiguration for automation example
Button1 = DigitalInOut(board.BUTTON_1)
Button1.direction = Direction.INPUT
Button1.pull = Pull.UP
#i2c for CardKB 
i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass
try: 
    cardkb = i2c.scan()[0]  # should return 95
    if cardkb != 95:
        print("!!! Check I2C config: " + str(i2c))
        print("!!! CardKB not found. I2C device", cardkb,
              "found instead.")
        M5CardKB=False
    else :
        print("CardKB detected Great")
        print()    
except:
    M5CardKB=False
    print("No CardKB detected !")
    print()
    time.sleep(0.5)
ESC = chr(27)
NUL = '\x00'
CR = "\r"
LF = "\n"
c = ''
b = bytearray(1)
buf=""
#invert TX and RX because of PI GPIO connector
uart = busio.UART(board.RX, board.TX, baudrate=115200)
def readuart():
    data = uart.read(1024)  # read up to 1024 bytes
    if data is not None:
        # convert bytearray to string
        data_string = ''.join([chr(b) for b in data])
        print(data_string, end="")    
while True:
    if Button1.value==False:
        while Button1.value==False:
            pass
        #example for kali linux login with button 1
        buf=uart.write(b'root\n')
        readuart()
        buf=uart.write(b'toor\n')
        readuart
#     if present we can use M5CardKB
    if M5CardKB==True:
        i2c.readfrom_into(cardkb, b)
        try:
            c = b.decode()
        except:
            c = NUL
        if c == CR:
            # convert CR return key to LF
            c = LF
        if c != NUL:
            #print(c, end='')
            buf= uart.write(b)
    #Read from UART and Display
    readuart()