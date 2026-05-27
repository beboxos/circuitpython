"""
based on the wonderful piece of code of Scott Shawcroft
original version from https://github.com/tannewt/basicpython
originally is an experiment to edit Python code like BASIC was edited.
The idea is imagining this as the default mode on a Raspberry Pi 400.

i ported it to Adafruit Pyportal Titano CircuitPython
(works on WIO terminal under CircuitPython too)

i added i2c m5stack keyboard CardKB but can work with any keyboard

Change log:
v0.03 - arrow keys history + inline editing
v0.04 - Bug fixes + new commands: new, cat, mkdir, cp, mv, mem, ver, del, renum
      - Fixed: cd command (was using getcwd instead of chdir)
      - Fixed: dir without argument no longer crashes
      - Fixed: backspace/insert inline editing rewritten cleanly
      - Added: ANSI helper functions (less duplication)
      - Added: file sizes in dir listing
      - Added: delete line by entering "N" with no code (BASIC style)
      - Better error messages on save/load/rm

more on twitter: https://twitter.com/beboxos
"""

import board
import os
import gc
import sys
import microcontroller
import busio

# I2C CardKB init
i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass
cardkb = i2c.scan()[0]  # should return 95
if cardkb != 95:
    print("!!! Check I2C config: " + str(i2c))
    print("!!! CardKB not found. I2C device", cardkb, "found instead.")
    sys.exit(1)

NUL = '\x00'
LF  = "\n"
BS  = '\x08'

buffer  = []
bufidx  = 0
curseur = 0
b       = bytearray(1)


# --- ANSI helpers ---

def ansi(seq):
    return '\x1b[' + seq

def clear_screen():
    print(ansi("2J") + ansi("H"), end="")

def cursor_left(n=1):
    if n > 0:
        print(ansi(str(n) + "D"), end="")

def cursor_right(n=1):
    if n > 0:
        print(ansi(str(n) + "C"), end="")

def clear_line():
    print(ansi("2K"), end="")


# --- Keyboard ---

def ReadKey():
    i2c.readfrom_into(cardkb, b)
    try:
        c = b.decode()
    except Exception:
        c = b
    if c == "\r":
        c = LF
    return c


def _replace_input(old, new):
    """Erase current input on screen and print new string."""
    n = max(len(old), len(new))
    cursor_left(len(old))
    print(' ' * n, end="")
    cursor_left(n)
    print(new, end="")


def InputFromKB(prompt):
    global bufidx, buffer, curseur
    buffer.append('')
    bufidx  = len(buffer) - 1
    key       = ''
    datainput = ''
    print(prompt, end='')

    while key != LF:
        try:
            key = ReadKey()
        except Exception:
            continue

        if key == NUL:
            continue

        if key == LF:
            break

        elif key == b'\xb5':  # up — history back
            if bufidx > 0:
                bufidx -= 1
            _replace_input(datainput, buffer[bufidx])
            datainput = buffer[bufidx]
            curseur   = len(datainput)

        elif key == b'\xb6':  # down — history forward
            if bufidx < len(buffer) - 1:
                bufidx += 1
            _replace_input(datainput, buffer[bufidx])
            datainput = buffer[bufidx]
            curseur   = len(datainput)

        elif key == b'\xb7':  # right arrow
            if curseur < len(datainput):
                print(datainput[curseur], end="")
                curseur += 1

        elif key == b'\xb4':  # left arrow
            if curseur > 0:
                cursor_left()
                curseur -= 1

        elif key == BS:  # backspace
            if curseur > 0:
                if curseur == len(datainput):
                    print(BS + ' ' + BS, end="")
                    datainput = datainput[:-1]
                else:
                    first     = datainput[:curseur - 1]
                    end       = datainput[curseur:]
                    cursor_left()
                    print(end + ' ', end="")
                    cursor_left(len(end) + 1)
                    datainput = first + end
                curseur -= 1

        else:  # printable character
            if curseur == len(datainput):
                print(key, end='')
                datainput += key
            else:
                first = datainput[:curseur]
                end   = datainput[curseur:]
                print(key + end, end="")
                cursor_left(len(end))
                datainput = first + key + end
            curseur += 1

    buffer[bufidx] = datainput
    print()
    curseur = 0
    return datainput


# --- Filesystem helpers ---

def _file_size(path):
    """Return file size in bytes, or -1 if directory."""
    try:
        st = os.stat(path)
        if st[0] & 0x4000:
            return -1
        return st[6]
    except Exception:
        return 0


def _copy_file(src, dst):
    with open(src, 'rb') as fin:
        with open(dst, 'wb') as fout:
            while True:
                chunk = fin.read(512)
                if not chunk:
                    break
                fout.write(chunk)


# --- Banner ---

clear_screen()
print("""
***********************************************************
*  ___            _      ___  _  _  _    _                *
* | _ ) __ _  ___(_) __ | _ \\| || || |_ | |_   ___  _ _   *
* | _ \\/ _` |(_-/| |/ _||  _/ \\_.  ||  _||   \\ / _ \\| ' \\  *
* |___/\\__/_|/__/|_|\\__||_|   |__/  \\__||_||_|\\___/|_||_| *
***********************************************************
v0.04 for CircuitPython devices with CardKB i2c
""")
print("Enter !help for command list\n")

program  = []
top      = {}
no_ready = False

# --- Main REPL loop ---

while True:
    prompt   = ">>>" if no_ready else "READY.\n>>>"
    line     = InputFromKB(prompt)
    no_ready = False

    remainder = ''
    if " " in line:
        command, remainder = line.split(" ", 1)
    else:
        command = line

    # Detect bare line number
    lineno = None
    try:
        lineno = int(command, 10)
    except (ValueError, TypeError):
        pass

    # ---- Line number entry (BASIC style) ----
    if lineno is not None:
        if lineno < 1:
            print("Line must be >= 1")
        else:
            if lineno > len(program):
                program.extend([""] * (lineno - len(program)))
            if remainder.strip():
                program[lineno - 1] = remainder
                no_ready = True
            else:
                program[lineno - 1] = ""
                print("Line", lineno, "deleted.")

    # ---- Commands ----
    elif command.lower() == "list":
        if not any(program):
            print("(program is empty)")
        for i, ln in enumerate(program):
            if ln:
                print(i + 1, ln)

    elif command.lower() == "run":
        isolated = {}
        try:
            exec("\n".join(program), isolated, isolated)
        except Exception as e:
            print("Runtime error:", e)

    elif command.lower() == "new":
        program = []
        top     = {}
        print("Program cleared.")

    elif command.lower() == "save":
        filename = remainder.strip(' "')
        if not filename:
            print("Usage: save <filename>")
        else:
            try:
                with open(filename, "w") as f:
                    f.write("\n".join(ln for ln in program if ln))
                print("Saved:", filename)
            except Exception as e:
                print("Save error:", e)

    elif command.lower() == "load":
        filename = remainder.strip(' "')
        if not filename:
            print("Usage: load <filename>")
        else:
            try:
                with open(filename, "r") as f:
                    program = [ln.strip("\r\n") for ln in f.readlines()]
                print("Loaded:", filename, "-", len(program), "lines")
            except Exception as e:
                print("Load error:", e)

    elif command.lower() == "cat":
        filename = remainder.strip(' "')
        if not filename:
            print("Usage: cat <filename>")
        else:
            try:
                with open(filename, "r") as f:
                    print(f.read())
            except Exception as e:
                print("Error:", e)

    elif command.lower() == "dir":
        path = remainder.strip(' "') if remainder.strip() else "/"
        if not path.startswith("/"):
            path = "/" + path
        try:
            files = os.listdir(path)
            print("Directory:", path)
            print("-" * 32)
            dirs, ffiles = [], []
            for n in files:
                full = path.rstrip("/") + "/" + n
                sz   = _file_size(full)
                if sz == -1:
                    dirs.append(n)
                else:
                    ffiles.append((n, sz))
            for d in sorted(dirs):
                print("[" + d + "]")
            for name, sz in sorted(ffiles):
                print("{:<20} {:>8} B".format(name, sz))
            print("-" * 32)
            print(len(dirs), "dir(s),", len(ffiles), "file(s)")
        except Exception as e:
            print("Error:", e)

    elif command.lower() == "cd":
        path = remainder.strip(' "')
        if not path:
            print(os.getcwd())
        else:
            try:
                os.chdir(path)
                print(os.getcwd())
            except Exception as e:
                print("Error:", e)

    elif command.lower() == "mkdir":
        path = remainder.strip(' "')
        if not path:
            print("Usage: mkdir <dirname>")
        else:
            try:
                os.mkdir(path)
                print("Created:", path)
            except Exception as e:
                print("Error:", e)

    elif command.lower() == "rm":
        filename = remainder.strip(' "')
        if not filename:
            print("Usage: rm <filename>")
        else:
            try:
                os.remove(filename)
                print("Removed:", filename)
            except Exception as e:
                print("Error:", e)

    elif command.lower() == "cp":
        parts = remainder.split()
        if len(parts) != 2:
            print("Usage: cp <source> <dest>")
        else:
            try:
                _copy_file(parts[0], parts[1])
                print("Copied:", parts[0], "->", parts[1])
            except Exception as e:
                print("Error:", e)

    elif command.lower() == "mv":
        parts = remainder.split()
        if len(parts) != 2:
            print("Usage: mv <source> <dest>")
        else:
            try:
                os.rename(parts[0], parts[1])
                print("Moved:", parts[0], "->", parts[1])
            except Exception as e:
                print("Error:", e)

    elif command.lower() == "del":
        try:
            n = int(remainder.strip())
            if 1 <= n <= len(program):
                program[n - 1] = ""
                print("Line", n, "deleted.")
            else:
                print("Line out of range (1-" + str(len(program)) + ")")
        except Exception:
            print("Usage: del <line_number>")

    elif command.lower() == "renum":
        program = [ln for ln in program if ln.strip()]
        print("Compacted to", len(program), "lines:")
        for i, ln in enumerate(program):
            print(i + 1, ln)

    elif command.lower() == "mem":
        gc.collect()
        free  = gc.mem_free()
        alloc = gc.mem_alloc()
        print("Memory free :", free,        "B  (", free  // 1024, "KB)")
        print("Memory used :", alloc,       "B  (", alloc // 1024, "KB)")
        print("Total       :", free + alloc,"B  (", (free + alloc) // 1024, "KB)")

    elif command.lower() == "ver":
        print("CircuitPython:", sys.version)
        print("Platform     :", sys.platform)
        try:
            print("CPU freq     :", microcontroller.cpu.frequency // 1_000_000, "MHz")
            print("CPU temp     :", microcontroller.cpu.temperature, "C")
        except Exception:
            pass

    elif command.lower() == "cls":
        clear_screen()

    elif command.lower() == "reset":
        microcontroller.reset()

    elif command.lower() == "exit":
        break

    elif command.lower() == "!help":
        print("""
Commands:
  -- Program --
  list          list current program lines
  run           execute current program
  new           clear program and variables
  N <code>      set line N  (blank code = delete)
  del N         delete line N
  renum         compact program (remove blank lines)

  -- Files --
  load <file>   load .py file into program
  save <file>   save program to file
  cat  <file>   print file contents

  -- Filesystem --
  dir  [path]   list directory with file sizes
  cd   [path]   change directory (no arg = show cwd)
  mkdir <dir>   create directory
  rm   <file>   delete file
  cp   <s> <d>  copy file
  mv   <s> <d>  rename / move file

  -- System --
  mem           show RAM usage
  ver           board and CP version info
  cls           clear screen
  reset         reboot device
  exit          return to REPL

  Any other input is evaluated as Python.
""")

    elif command == "":
        pass

    else:
        try:
            exec(line, top, top)
        except Exception as e:
            print("Error:", e)
