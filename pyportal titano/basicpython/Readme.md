```
 ╔══════════════════════════════════════════════════════════════╗
 ║                                                              ║
 ║        ██████╗  █████╗ ███████╗██╗ ██████╗                  ║
 ║        ██╔══██╗██╔══██╗██╔════╝██║██╔════╝                  ║
 ║        ██████╔╝███████║███████╗██║██║                        ║
 ║        ██╔══██╗██╔══██║╚════██║██║██║                        ║
 ║        ██████╔╝██║  ██║███████║██║╚██████╗                  ║
 ║        ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝                  ║
 ║                                                              ║
 ║          ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗    ║
 ║          ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗   ║
 ║          ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗  ║
 ║          ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗ ║
 ║          ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚██╗║
 ║          ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝║
 ║                                                              ║
 ║                  U S E R ' S   M A N U A L                   ║
 ║                        Version 0.04                          ║
 ║                                                              ║
 ║          For Adafruit PyPortal Titano — CircuitPython        ║
 ║                  with M5Stack CardKB keyboard                ║
 ║                                                              ║
 ║                   by @beboxos  (2021-2026)                   ║
 ╚══════════════════════════════════════════════════════════════╝
```

---

## TABLE OF CONTENTS

```
  1. INTRODUCTION ................................................ 3
  2. HARDWARE SETUP .............................................. 4
  3. GETTING STARTED ............................................. 5
  4. THE KEYBOARD ................................................ 6
  5. COMMAND REFERENCE
       5.1  Program Commands (LIST, RUN, NEW) ..................  8
       5.2  Line Editing (N, DEL, RENUM) .......................  10
       5.3  File Commands (SAVE, LOAD, CAT) ....................  12
       5.4  Filesystem Commands (DIR, CD, MKDIR, RMDIR) ........  14
       5.5  File Operations (RM, CP, MV) .......................  16
       5.6  System Commands (MEM, DF, VER, CLS, RESET, EXIT) ..  18
       5.7  Direct Python Execution ............................  20
  6. SAMPLE PROGRAMS ............................................ 21
  7. ERROR MESSAGES ............................................. 24
  8. APPENDIX — CIRCUITPYTHON COMPATIBILITY .................... 25
```

---

# 1. INTRODUCTION

```
  ┌─────────────────────────────────────────────────────────────┐
  │  WELCOME TO BASICPYTHON !                                   │
  │                                                             │
  │  BasicPython brings back the joy of direct, immediate       │
  │  programming — right on your device, without a computer.   │
  │                                                             │
  │  Type a command. See the result. Write a program line by    │
  │  line. Run it. Save it. Come back to it later.              │
  │                                                             │
  │  This is the spirit of the home computers of the 1980s,    │
  │  reborn on a CircuitPython device you can hold in your      │
  │  hand.                                                      │
  └─────────────────────────────────────────────────────────────┘
```

BasicPython is an interactive Python shell for CircuitPython devices, designed to work entirely without a computer. It was originally inspired by Scott Shawcroft's `basicpython` experiment, and ported / extended for the Adafruit PyPortal Titano by @beboxos.

You can:
- Write and run Python programs line by line (BASIC style)
- Manage files and directories on your device's flash storage
- Evaluate Python expressions directly
- Check memory and disk usage
- All of this from a tiny I2C keyboard, with no USB cable needed.

---

# 2. HARDWARE SETUP

```
  Required hardware:
  ┌──────────────────────────────────────────────────────────┐
  │  ● Adafruit PyPortal Titano                              │
  │    (also compatible: Seeed WIO Terminal)                 │
  │                                                          │
  │  ● M5Stack CardKB — I2C keyboard (address 0x5F = 95)    │
  │                                                          │
  │  ● CircuitPython 7.x or 8.x                             │
  └──────────────────────────────────────────────────────────┘

  Wiring:
  ┌──────────────┬──────────────┐
  │  CardKB pin  │  PyPortal    │
  ├──────────────┼──────────────┤
  │  SDA         │  board.SDA   │
  │  SCL         │  board.SCL   │
  │  GND         │  GND         │
  │  VCC         │  3.3V        │
  └──────────────┴──────────────┘

  ! NOTE: The CardKB MUST be detected at I2C address 95 (0x5F).
          If it is not found, BasicPython will print an error
          and stop. Check your wiring if this happens.
```

**Installation:**

1. Copy `basicpython.py` to the root of your CIRCUITPY drive.
2. To run at boot, rename it `code.py`.
3. To run manually from the REPL:
   ```
   >>> import basicpython
   ```

---

# 3. GETTING STARTED

When BasicPython starts, you will see:

```
  ***********************************************************
  *  ___            _      ___  _  _  _    _                *
  * | _ ) __ _  ___(_) __ | _ \| || || |_ | |_   ___  _ _   *
  * | _ \/ _` |(_-/| |/ _||  _/ \_.  ||  _||   \ / _ \| ' \  *
  * |___/\__/_|/__/|_|\__||_|   |__/  \__||_||_|\___/|_||_| *
  ***********************************************************
  v0.04 for CircuitPython devices with CardKB i2c

  Enter !help for command list

  READY.
  >>>
```

The `READY.` prompt means the system is waiting for your input.  
The `>>>` prompt (without READY.) appears when you are entering program lines.

**Your first command — try this:**

```
  READY.
  >>> print("Hello, World!")
  Hello, World!

  READY.
  >>>
```

**To get help at any time, type:**

```
  READY.
  >>> !help
```

---

# 4. THE KEYBOARD

BasicPython uses the **M5Stack CardKB** keyboard over I2C.

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Key            Action                                      │
  ├─────────────────────────────────────────────────────────────┤
  │  ENTER          Validate current input                      │
  │  BACKSPACE      Delete character before cursor              │
  │  ← (left)       Move cursor one character to the left       │
  │  → (right)      Move cursor one character to the right      │
  │  ↑ (up)         Recall previous command from history        │
  │  ↓ (down)       Recall next command from history            │
  └─────────────────────────────────────────────────────────────┘
```

**Command history:** Every line you type is saved. Use the UP and DOWN arrows to navigate through your previous inputs. This works across commands AND program lines.

**Inline editing:** LEFT and RIGHT arrows let you move within the current line to correct a typo without retyping everything.

---

# 5. COMMAND REFERENCE

---

## 5.1 — PROGRAM COMMANDS

---

### LIST

**Syntax:** `LIST`

Displays all non-empty lines of the current program, with their line numbers.

```
  READY.
  >>> LIST
  10 for i in range(3):
  20   print(i)

  READY.
  >>>
```

If the program is empty:

```
  READY.
  >>> LIST
  (program is empty)
```

**See also:** RUN, NEW

---

### RUN

**Syntax:** `RUN`

Executes the current program. All lines are joined in order and passed to Python's `exec()` function.

```
  READY.
  >>> RUN
  0
  1
  2

  READY.
  >>>
```

If an error occurs during execution, the error message is printed and the program stops:

```
  READY.
  >>> RUN
  Runtime error: ZeroDivisionError: division by zero
```

> **NOTE:** Variables created during `RUN` are isolated from the direct-execution namespace. Use direct evaluation for quick tests, or write a program with `RUN` for structured code.

**See also:** LIST, NEW

---

### NEW

**Syntax:** `NEW`

Clears the current program AND resets all variables from the direct-execution namespace.

```
  READY.
  >>> NEW
  Program cleared.

  READY.
  >>>
```

> **WARNING:** There is no confirmation prompt. Make sure you have saved your program with `SAVE` before using `NEW`.

**See also:** SAVE, LIST

---

## 5.2 — LINE EDITING

---

### Entering a program line

**Syntax:** `N <Python code>`

Where `N` is a line number (integer >= 1).

Assigns `<Python code>` to line N. If lines between the last line and N do not exist, they are created as empty.

```
  >>> 10 x = 42
  >>> 20 print("The answer is", x)
  >>> LIST
  10 x = 42
  20 print("The answer is", x)
```

Lines can be overwritten by re-entering the same number:

```
  >>> 10 x = 100
  >>> LIST
  10 x = 100
  20 print("The answer is", x)
```

> **TIP:** Use multiples of 10 for line numbers (10, 20, 30...) so you can insert lines between them later (e.g. line 15).

---

### Deleting a line (BASIC style)

**Syntax:** `N`

Type a line number with NO code after it. The line is deleted.

```
  >>> 20
  Line 20 deleted.
  >>> LIST
  10 x = 100
```

---

### DEL

**Syntax:** `DEL N`

Deletes line number N. Equivalent to typing `N` alone.

```
  READY.
  >>> DEL 10
  Line 10 deleted.
```

If the line number is out of range:

```
  READY.
  >>> DEL 99
  Line out of range (1 - 20)
```

**See also:** RENUM

---

### RENUM

**Syntax:** `RENUM`

Removes all blank/deleted lines from the program and renumbers remaining lines starting from 1. The program is then listed.

```
  READY.
  >>> RENUM
  Compacted to 3 lines:
  1 x = 42
  2 y = x * 2
  3 print(x, y)
```

> **NOTE:** After RENUM, all your line numbers change. Any reference to old line numbers is now incorrect. Use RENUM before a final SAVE.

**See also:** DEL, LIST

---

## 5.3 — FILE COMMANDS

---

### SAVE

**Syntax:** `SAVE <filename>`

Saves the current program (non-empty lines only) to a file on the flash storage.

```
  READY.
  >>> SAVE /myprog.py
  Saved: /myprog.py
```

If the filename is missing:

```
  Usage: save <filename>
```

> **NOTE:** If the file already exists, it will be overwritten without warning.

**See also:** LOAD, NEW

---

### LOAD

**Syntax:** `LOAD <filename>`

Loads a Python file from flash storage into the program buffer. The previous program is replaced.

```
  READY.
  >>> LOAD /myprog.py
  Loaded: /myprog.py - 3 lines
```

After loading, use `LIST` to see the program and `RUN` to execute it.

> **NOTE:** LOAD does NOT run the program automatically.

**See also:** SAVE, LIST, RUN

---

### CAT

**Syntax:** `CAT <filename>`

Prints the contents of any file to the screen. Works with Python files, text files, and configuration files.

```
  READY.
  >>> CAT /boot_out.txt
  Adafruit CircuitPython 8.0.5 on 2023-03-31;
  Adafruit PyPortal Titano with samd51j20
  Board ID: pyportal_titano
```

**See also:** DIR, LOAD

---

## 5.4 — FILESYSTEM COMMANDS

---

### DIR

**Syntax:** `DIR [path]`

Lists the contents of a directory. If no path is given, lists `/` (root).  
Directories are shown in `[brackets]`. Files are shown with their size in bytes.

```
  READY.
  >>> DIR
  Directory: /
  --------------------------------
  [lib]
  [sd]
  boot_out.txt              312 B
  code.py                  8192 B
  myprog.py                 128 B
  settings.toml              64 B
  --------------------------------
  2 dir(s), 4 file(s)
```

Listing a subdirectory:

```
  READY.
  >>> DIR /lib
  Directory: /lib
  --------------------------------
  [adafruit_bus_device]
  adafruit_display_text      4096 B
  --------------------------------
  1 dir(s), 1 file(s)
```

**See also:** CD, MKDIR, RM

---

### CD

**Syntax:** `CD [path]`

Changes the current working directory. With no argument, shows the current directory.

```
  READY.
  >>> CD /projects
  /projects

  READY.
  >>> CD
  /projects
```

Return to root:

```
  READY.
  >>> CD /
  /
```

**See also:** DIR, MKDIR

---

### MKDIR

**Syntax:** `MKDIR <dirname>`

Creates a new directory.

```
  READY.
  >>> MKDIR /projects
  Created: /projects

  READY.
  >>> MKDIR /projects/demos
  Created: /projects/demos
```

**See also:** RMDIR, DIR, CD

---

### RMDIR

**Syntax:** `RMDIR <dirname>`

Removes an **empty** directory. The directory must contain no files.

```
  READY.
  >>> RMDIR /projects/demos
  Removed dir: /projects/demos
```

If the directory is not empty:

```
  Error: [Errno 39] Directory not empty
```

**See also:** MKDIR, RM

---

## 5.5 — FILE OPERATIONS

---

### RM

**Syntax:** `RM <filename>`

Permanently deletes a file from flash storage.

```
  READY.
  >>> RM /old_test.py
  Removed: /old_test.py
```

> **WARNING:** Deletion is immediate and permanent. There is no recycle bin.

**See also:** CP, MV, DIR

---

### CP

**Syntax:** `CP <source> <destination>`

Copies a file. The copy is done in 512-byte chunks to preserve RAM.

```
  READY.
  >>> CP /myprog.py /backup/myprog_bak.py
  Copied: /myprog.py -> /backup/myprog_bak.py
```

> **NOTE:** The destination directory must already exist.

**See also:** MV, RM, MKDIR

---

### MV

**Syntax:** `MV <source> <destination>`

Renames or moves a file.

```
  READY.
  >>> MV /test.py /projects/test_v2.py
  Moved: /test.py -> /projects/test_v2.py
```

> **NOTE:** MV can move a file to a different directory as long as both are on the same filesystem (flash). It cannot move files across filesystems (e.g. flash → SD card). Use `CP` + `RM` for that.

**See also:** CP, RM

---

## 5.6 — SYSTEM COMMANDS

---

### MEM

**Syntax:** `MEM`

Runs garbage collection and displays RAM usage.

```
  READY.
  >>> MEM
  RAM free :  163840 B ( 160 KB)
  RAM used :   28672 B (  28 KB)
  RAM total: 192512 B ( 188 KB)
```

> **TIP:** Run `MEM` before loading a large library or running a memory-intensive program to check if you have enough RAM.

**See also:** DF, VER

---

### DF

**Syntax:** `DF`

Displays flash disk space (total, used, free).

```
  READY.
  >>> DF
  Disk total: 8126464 B ( 7936 KB)
  Disk used :  524288 B (  512 KB)
  Disk free : 7602176 B ( 7424 KB)
```

> **NOTE:** Uses `os.statvfs("/")` internally.

**See also:** MEM, DIR

---

### VER

**Syntax:** `VER`

Displays CircuitPython version, board name, CPU frequency and temperature.

```
  READY.
  >>> VER
  System  : samd51
  Release : 8.0.5
  Version : 8.0.5 on 2023-03-31
  Machine : Adafruit PyPortal Titano with samd51j20
  CPU freq: 120 MHz
  CPU temp: 43.7 C
```

> **NOTE:** CPU temperature returns `None` on some boards. In that case, the line is simply not shown.

**See also:** MEM

---

### CLS

**Syntax:** `CLS`

Clears the screen.

```
  READY.
  >>> CLS
```

The screen is erased and the cursor returns to the top-left corner (ANSI escape sequence).

---

### RESET

**Syntax:** `RESET`

Reboots the device. Equivalent to pressing the hardware reset button.

```
  READY.
  >>> RESET
```

> **WARNING:** If the device is connected to a computer via USB at the moment of reset, filesystem corruption may occur. Disconnect USB or eject the drive first.

---

### EXIT

**Syntax:** `EXIT`

Exits BasicPython and returns to the CircuitPython REPL.

```
  READY.
  >>> EXIT
  >>>
```

---

## 5.7 — DIRECT PYTHON EXECUTION

Any input that is not a recognized command, and does not begin with a line number, is evaluated directly as Python code.

```
  READY.
  >>> 2 + 2
  4

  READY.
  >>> import math
  READY.
  >>> math.sqrt(144)
  12.0

  READY.
  >>> [x**2 for x in range(6)]
  [0, 1, 4, 9, 16, 25]
```

Variables and imports are preserved throughout the session in a shared namespace. Use `NEW` to reset them.

```
  READY.
  >>> name = "PyPortal"
  READY.
  >>> print("Hello from", name)
  Hello from PyPortal
```

---

# 6. SAMPLE PROGRAMS

---

## Program 1 — Hello, World!

```
  10 print("*" * 30)
  20 print("*  Hello from BasicPython  *")
  30 print("*" * 30)
```

**To try it:**
```
  >>> 10 print("*" * 30)
  >>> 20 print("*  Hello from BasicPython  *")
  >>> 30 print("*" * 30)
  >>> RUN
  ******************************
  *  Hello from BasicPython  *
  ******************************
```

---

## Program 2 — Countdown

```
  10 import time
  20 for i in range(10, 0, -1):
  30   print(i)
  40   time.sleep(1)
  50 print("LAUNCH !")
```

**To try it:**
```
  >>> NEW
  >>> 10 import time
  >>> 20 for i in range(10, 0, -1):
  >>> 30   print(i)
  >>> 40   time.sleep(1)
  >>> 50 print("LAUNCH !")
  >>> RUN
  10
  9
  8
  ...
  1
  LAUNCH !
```

---

## Program 3 — Check system status

```
  10 import os, gc
  20 gc.collect()
  30 st = os.statvfs("/")
  40 free_kb = (st[3] * st[0]) // 1024
  50 ram_kb  = gc.mem_free() // 1024
  60 print("Flash free:", free_kb, "KB")
  70 print("RAM free  :", ram_kb,  "KB")
```

---

## Program 4 — Blink the built-in LED

```
  10 import board, digitalio, time
  20 led = digitalio.DigitalInOut(board.LED)
  30 led.direction = digitalio.Direction.OUTPUT
  40 for i in range(10):
  50   led.value = True
  60   time.sleep(0.5)
  70   led.value = False
  80   time.sleep(0.5)
  90 print("Done!")
```

---

## Program 5 — Save a note to flash

```
  10 note = "Remember to update the firmware!"
  20 with open("/note.txt", "w") as f:
  30   f.write(note)
  40 print("Note saved.")
```

After running, you can read it back with:
```
  READY.
  >>> CAT /note.txt
  Remember to update the firmware!
```

---

# 7. ERROR MESSAGES

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  Error message                   Cause                          │
  ├─────────────────────────────────────────────────────────────────┤
  │  Runtime error: <msg>            Exception during RUN           │
  │  Error: <msg>                    Exception during a command      │
  │  Save error: <msg>               Cannot write file (disk full?) │
  │  Load error: <msg>               File not found or unreadable   │
  │  Line must be >= 1               Line number < 1 entered        │
  │  Line out of range (1 - N)       DEL with invalid line number   │
  │  Usage: <command> <args>         Wrong syntax for a command     │
  │  !!! CardKB not found            CardKB not at I2C address 95   │
  └─────────────────────────────────────────────────────────────────┘
```

---

# 8. APPENDIX — CIRCUITPYTHON COMPATIBILITY

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  Module          Function used          Available in CP         │
  ├─────────────────────────────────────────────────────────────────┤
  │  os              chdir, getcwd          7.x, 8.x ✓              │
  │  os              mkdir, rmdir           7.x, 8.x ✓              │
  │  os              remove, rename         7.x, 8.x ✓              │
  │  os              stat, listdir          7.x, 8.x ✓              │
  │  os              statvfs                7.x, 8.x ✓              │
  │  os              uname                  7.x, 8.x ✓              │
  │  gc              collect, mem_free      7.x, 8.x ✓              │
  │  gc              mem_alloc              7.x, 8.x ✓              │
  │  microcontroller cpu.frequency          7.x, 8.x ✓              │
  │  microcontroller cpu.temperature        7.x, 8.x ✓ (may be None)│
  │  microcontroller reset()               7.x, 8.x ✓              │
  │  busio           I2C                    7.x, 8.x ✓              │
  └─────────────────────────────────────────────────────────────────┘
```

> Numeric literals with underscores (e.g. `1_000_000`) are supported only  
> from CircuitPython 7.2. BasicPython v0.04 uses `1000000` for compatibility  
> with all CircuitPython 7.x versions.

---

## CHANGE LOG

```
  v0.01  2021-10   Initial port to PyPortal Titano
  v0.02  2021-10   WIO Terminal compatibility
  v0.03  2021-10   Arrow keys: ↑↓ history, ←→ inline editing
  v0.04  2026-05   Bug fixes:
                     - cd: os.chdir() instead of os.getcwd(path)
                     - dir: no crash when called without argument
                     - backspace / inline insert rewritten
                     - _is_dir() uses os.listdir() (more robust)
                     - ver: uses os.uname() for accurate board info
                     - cpu.temperature: handles None return value
                   New commands:
                     new, cat, mkdir, rmdir, cp, mv, del, renum,
                     mem, df, ver
                   ANSI helpers extracted
                   Full user manual (EN + FR)
```

---

```
  ┌───────────────────────────────────────────────────────────┐
  │  BasicPython v0.04 — (c) 2021-2026 @beboxos              │
  │  Based on original work by Scott Shawcroft               │
  │  https://github.com/tannewt/basicpython                  │
  │  https://twitter.com/beboxos                             │
  └───────────────────────────────────────────────────────────┘
```
