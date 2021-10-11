"""
based on the wonderfull piece of code of Scott Shawcroft
original version from https://github.com/tannewt/basicpython
originaly is an experiment to edit Python code like BASIC was edited.
The idea is imagining this as the default mode on a Raspberry Pi 400.

i ported it to Adafruit Pyportal Titano circuitpython
(work on wio terminal under circuitpython too)

i added i2c m5stack keyboard CardKB but can work with any keyboard
i added a dir function to list files in directory

on next update will try to add more features to act as a light os

this make our little gadgets autonomous for running and coding on the go

Enjoy it.

more on my twitter : https://twitter.com/beboxos

"""
#init 
import board
import displayio
import os, microcontroller
import busio 
i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass
cardkb = i2c.scan()[0]  # should return 95
if cardkb != 95:
    print("!!! Check I2C config: " + str(i2c))
    print("!!! CardKB not found. I2C device", cardkb,
          "found instead.")
    import sys
    sys.exit(1)
 
ESC = chr(27)
NUL = '\x00'
CR = "\r"
LF = "\n"

b = bytearray(1)


def ReadKey():
    c = ''
    i2c.readfrom_into(cardkb, b)    
    try:
        c = b.decode()
    except:
        c = ""
    if c == CR:
        # convert CR return key to LF
        c = LF
    return c

def InputFromKB(prompt):
    key=''
    keyRead=''
    datainput=''
    print(prompt, end='')
    while key!="\n":
            key=ReadKey()
            #key = keyRead[0]    
            #key = key[1]
            if key!=NUL:
                if key!="\n":
                    print(key, end='')
                    if key!='\x08':
                        datainput+=key
                    else:
                        datainput=datainput[:-1]
                        #print(key, end="")
                        print(" ", end="")
                        print(key, end="")
    print()
    return datainput
for i in range(20):
    print()
banner =(
"""
***********************************************************
*  ___            _      ___  _  _  _    _                *
* | _ ) __ _  ___(_) __ | _ \| || || |_ | |_   ___  _ _   *
* | _ \/ _` |(_-/| |/ _||  _/ \_. ||  _||   \ / _ \| ' \  *
* |___/\__/_|/__/|_|\__||_|   |__/  \__||_||_|\___/|_||_| *
***********************************************************
v0.02 for Circuitpython devices with CardKB i2c

""")
#print("# Basic Python v0.01               ")
#print("For Circuitpython devices with CardKB i2c")
print(banner)
print("Enter !help for command list")

program = []
top = {}
no_ready = False

while True:
    if no_ready:
        #version for keyboard FeatherWing
        line = InputFromKB(">>>")
        #line = input()
    else:
        #version for keyboard FeatherWing
        line = InputFromKB("READY.\n>>>")        
        #line = input("READY.\n")
    lineno = None
    if " " in line:
        command, remainder = line.split(" ", 1)
        lineno = None
        try:
            lineno = int(command, 10)
        except ValueError:
            pass
    else:
        command = line
    no_ready = False
    if lineno is not None:
        if lineno < 1:
            print("Line must be 1+")
        else:
            if lineno >= len(program):
                program.extend([""] * (lineno - len(program)))
            program[lineno - 1] = remainder
            no_ready = True
    elif command.lower() == "list":
        for i, line in enumerate(program):
            if line:
                print(i+1, line)
    elif command.lower() == "run":
        isolated = {}
        try:
            exec("\n".join(program), isolated, isolated)
        except Exception as e:
            print(e)
    elif command.lower() == "save":
        filename = remainder.strip(" \"")
        with open(filename, "w") as f:
            f.write("\n".join(program))
    elif command.lower() == "load":
        filename = remainder.strip(" \"")
        with open(filename, "r") as f:
            program = f.readlines()
            program = [line.strip("\r\n") for line in program]
    #add on by BeBoX for easy new commands        
    elif command.lower() == "dir":
        print("directory of ",end="")
        path="/"                    
        try:
            path+=remainder.strip(" \"")
        except:
            pass
        files=os.listdir(path)
        print(path)
        for n in files:
            print(n)        
    elif command.lower() == "reset":
        microcontroller.reset()

    elif command.lower() == "exit":
        break
    elif command.lower() == "cd":
        path=remainder
        try:
            os.getcwd(path)
        except Exception as e:
            pass
        print(os.getcwd())
    elif command.lower() == "rm":
        file=remainder
        try:
            os.remove(file)
        except Exception as e:
            print(e)
            
        
    elif command.lower() == "!help":
        print("Listing of available commands :")
        print("list : list current program")
        print("run  : run current program")
        print("load : load a program")
        print("save : save curent program")
        print("dir  : show directory content")
        print("cd   : change directory path")
        print("rm   : remove file")
        print("reset: reset device")
        print("exit : exit to REPL")
        
    else:
        try:
            exec(line, top, top)
        except Exception as e:
            print(e)
