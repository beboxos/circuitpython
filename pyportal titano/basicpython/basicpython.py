"""
based on the wonderful piece of code of Scott Shawcroft
original version from https://github.com/tannewt/basicpython
originally is an experiment to edit Python code like BASIC was edited.
The idea is imagining this as the default mode on a Raspberry Pi 400.

i ported it to Adafruit Pyportal Titano CircuitPython
(works on WIO terminal under CircuitPython too)

i added i2c m5stack keyboard CardKB but can work with any keyboard

Change log:
v0.03 - arrow keys: up/down history, left/right inline editing
v0.04 - Bug fixes + new commands: new, cat, mkdir, rmdir, cp, mv, del, renum, mem, df, ver
      - Fixed: cd command (was using getcwd instead of chdir)
      - Fixed: dir without argument no longer crashes
      - Fixed: backspace / inline insert rewritten cleanly
      - Fixed: numeric literal 1_000_000 -> 1000000 (CP <7.2 compat)
      - Fixed: temperature/voltage can return None on some boards
      - Improved: dir shows file sizes and separates dirs from files
      - Improved: ver uses os.uname() for accurate board/CP info
      - Improved: ANSI helpers extracted (no more duplicated escape strings)
      - Improved: all commands have proper error messages

more on twitter: https://twitter.com/beboxos
"""

import board
import os
import gc
import sys
import microcontroller
import busio

# --- I2C CardKB init ---
i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass
cardkb = i2c.scan()[0]  # should return 95
if cardkb != 95:
    print("!!! Check I2C config: " + str(i2c))
    print("!!! CardKB not found. I2C device", cardkb, "found instead.")
    sys.exit(1)

# --- Constants ---
NUL = '\x00'
LF  = "\n"
BS  = '\x08'

# --- Input history / cursor state ---
buffer  = []
bufidx  = 0
curseur = 0
b       = bytearray(1)


# ============================================================
# ANSI terminal helpers
# ============================================================

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


# ============================================================
# Keyboard input
# ============================================================

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
    """Erase current typed input on screen and replace with new."""
    n = max(len(old), len(new))
    cursor_left(len(old))
    print(' ' * n, end="")
    cursor_left(n)
    print(new, end="")


def InputFromKB(prompt):
    global bufidx, buffer, curseur
    buffer.append('')
    bufidx    = len(buffer) - 1
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

        elif key == b'\xb5':  # up arrow — history back
            if bufidx > 0:
                bufidx -= 1
            _replace_input(datainput, buffer[bufidx])
            datainput = buffer[bufidx]
            curseur   = len(datainput)

        elif key == b'\xb6':  # down arrow — history forward
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
                    # delete at end of line
                    print(BS + ' ' + BS, end="")
                    datainput = datainput[:-1]
                else:
                    # delete in the middle: redraw suffix
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
                # insert in the middle: redraw suffix
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


# ============================================================
# Filesystem helpers
# ============================================================

def _is_dir(path):
    """Return True if path is a directory (works on all CP versions)."""
    try:
        os.listdir(path)
        return True
    except Exception:
        return False


def _file_size(path):
    """Return file size in bytes. Returns 0 on error."""
    try:
        return os.stat(path)[6]
    except Exception:
        return 0


def _copy_file(src, dst):
    """Copy src to dst in 512-byte chunks (memory-friendly)."""
    with open(src, 'rb') as fin:
        with open(dst, 'wb') as fout:
            while True:
                chunk = fin.read(512)
                if not chunk:
                    break
                fout.write(chunk)


def _norm_path(raw, base="/"):
    """Strip quotes/spaces; prefix with / if needed."""
    p = raw.strip(' "\'')
    if not p:
        return base
    if not p.startswith("/"):
        p = "/" + p
    return p


# ============================================================
# Banner
# ============================================================

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


# ============================================================
# Main REPL loop
# ============================================================

while True:
    prompt   = ">>>" if no_ready else "READY.\n>>>"
    line     = InputFromKB(prompt)
    no_ready = False

    # Split into command + remainder
    remainder = ''
    if " " in line:
        command, remainder = line.split(" ", 1)
    else:
        command = line

    # Detect a bare line number (BASIC style entry)
    lineno = None
    try:
        lineno = int(command, 10)
    except (ValueError, TypeError):
        pass

    # ---- BASIC line number entry ----
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

    # ---- list ----
    elif command.lower() == "list":
        if not any(program):
            print("(program is empty)")
        for i, ln in enumerate(program):
            if ln:
                print(i + 1, ln)

    # ---- run ----
    elif command.lower() == "run":
        isolated = {}
        try:
            exec("\n".join(program), isolated, isolated)
        except Exception as e:
            print("Runtime error:", e)

    # ---- new ----
    elif command.lower() == "new":
        program = []
        top     = {}
        print("Program cleared.")

    # ---- save ----
    elif command.lower() == "save":
        filename = remainder.strip(' "\'')
        if not filename:
            print("Usage: save <filename>")
        else:
            try:
                with open(filename, "w") as f:
                    f.write("\n".join(ln for ln in program if ln))
                print("Saved:", filename)
            except Exception as e:
                print("Save error:", e)

    # ---- load ----
    elif command.lower() == "load":
        filename = remainder.strip(' "\'')
        if not filename:
            print("Usage: load <filename>")
        else:
            try:
                with open(filename, "r") as f:
                    program = [ln.strip("\r\n") for ln in f.readlines()]
                print("Loaded:", filename, "-", len(program), "lines")
            except Exception as e:
                print("Load error:", e)

    # ---- cat ----
    elif command.lower() == "cat":
        filename = remainder.strip(' "\'')
        if not filename:
            print("Usage: cat <filename>")
        else:
            try:
                with open(filename, "r") as f:
                    print(f.read())
            except Exception as e:
                print("Error:", e)

    # ---- dir ----
    elif command.lower() == "dir":
        path = _norm_path(remainder) if remainder.strip() else "/"
        try:
            entries = os.listdir(path)
            print("Directory:", path)
            print("-" * 32)
            dirs, files = [], []
            for n in entries:
                full = path.rstrip("/") + "/" + n
                if _is_dir(full):
                    dirs.append(n)
                else:
                    files.append((n, _file_size(full)))
            for d in sorted(dirs):
                print("[" + d + "]")
            for name, sz in sorted(files):
                print("{:<20} {:>8} B".format(name, sz))
            print("-" * 32)
            print(len(dirs), "dir(s),", len(files), "file(s)")
        except Exception as e:
            print("Error:", e)

    # ---- cd ----
    elif command.lower() == "cd":
        path = remainder.strip(' "\'')
        if not path:
            print(os.getcwd())
        else:
            try:
                os.chdir(path)
                print(os.getcwd())
            except Exception as e:
                print("Error:", e)

    # ---- mkdir ----
    elif command.lower() == "mkdir":
        path = remainder.strip(' "\'')
        if not path:
            print("Usage: mkdir <dirname>")
        else:
            try:
                os.mkdir(path)
                print("Created:", path)
            except Exception as e:
                print("Error:", e)

    # ---- rmdir ----
    elif command.lower() == "rmdir":
        path = remainder.strip(' "\'')
        if not path:
            print("Usage: rmdir <dirname>")
        else:
            try:
                os.rmdir(path)
                print("Removed dir:", path)
            except Exception as e:
                print("Error:", e)

    # ---- rm ----
    elif command.lower() == "rm":
        filename = remainder.strip(' "\'')
        if not filename:
            print("Usage: rm <filename>")
        else:
            try:
                os.remove(filename)
                print("Removed:", filename)
            except Exception as e:
                print("Error:", e)

    # ---- cp ----
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

    # ---- mv ----
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

    # ---- del ----
    elif command.lower() == "del":
        try:
            n = int(remainder.strip())
            if 1 <= n <= len(program):
                program[n - 1] = ""
                print("Line", n, "deleted.")
            else:
                print("Line out of range (1 -", len(program), ")")
        except Exception:
            print("Usage: del <line_number>")

    # ---- renum ----
    elif command.lower() == "renum":
        program = [ln for ln in program if ln.strip()]
        print("Compacted to", len(program), "lines:")
        for i, ln in enumerate(program):
            print(i + 1, ln)

    # ---- mem ----
    elif command.lower() == "mem":
        gc.collect()
        free  = gc.mem_free()
        alloc = gc.mem_alloc()
        total = free + alloc
        print("RAM free :", free,  "B (", free  // 1024, "KB)")
        print("RAM used :", alloc, "B (", alloc // 1024, "KB)")
        print("RAM total:", total, "B (", total // 1024, "KB)")

    # ---- df ----
    elif command.lower() == "df":
        try:
            st   = os.statvfs("/")
            bsz  = st[0]                  # block size
            tot  = st[2] * bsz            # total bytes
            free = st[3] * bsz            # free bytes
            used = tot - free
            print("Disk total:", tot,  "B (", tot  // 1024, "KB)")
            print("Disk used :", used, "B (", used // 1024, "KB)")
            print("Disk free :", free, "B (", free // 1024, "KB)")
        except Exception as e:
            print("Error:", e)

    # ---- ver ----
    elif command.lower() == "ver":
        try:
            u = os.uname()
            print("System  :", u.sysname)
            print("Release :", u.release)
            print("Version :", u.version)
            print("Machine :", u.machine)
        except Exception as e:
            print("os.uname error:", e)
        try:
            freq = microcontroller.cpu.frequency
            print("CPU freq:", freq // 1000000, "MHz")
        except Exception:
            pass
        try:
            temp = microcontroller.cpu.temperature
            if temp is not None:
                print("CPU temp:", temp, "C")
        except Exception:
            pass

    # ---- cls ----
    elif command.lower() == "cls":
        clear_screen()

    # ---- reset ----
    elif command.lower() == "reset":
        microcontroller.reset()

    # ---- exit ----
    elif command.lower() == "exit":
        break

    # ---- !help ----
    elif command.lower() == "!help":
        print("""
=== BasicPython v0.04 command reference ===

  -- Program editing --
  list          list program lines (non-empty)
  run           execute current program
  new           clear program and variables
  N <code>      set line N to <code>
  N             (no code) delete line N
  del N         delete line N
  renum         compact: remove blank lines, renumber from 1

  -- File I/O --
  load <file>   load a .py file as program
  save <file>   save program to file
  cat  <file>   print file contents to screen

  -- Filesystem --
  dir  [path]   list directory (default: /)
  cd   [path]   change directory (no arg: show cwd)
  mkdir <dir>   create directory
  rmdir <dir>   remove empty directory
  rm   <file>   delete file
  cp   <s> <d>  copy file
  mv   <s> <d>  rename / move file

  -- System --
  mem           show RAM free / used
  df            show disk (flash) free / used
  ver           board info, CP version, CPU freq & temp
  cls           clear screen
  reset         reboot device
  exit          return to REPL

  Any other input is evaluated as Python directly.
""")

    elif command == "":
        pass

    else:
        try:
            exec(line, top, top)
        except Exception as e:
            print("Error:", e)
