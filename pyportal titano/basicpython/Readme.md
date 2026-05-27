# BasicPython for PyPortal Titano (CircuitPython)

![hardware](https://pbs.twimg.com/media/FBaB0n4X0AIhNZ8?format=jpg&name=large)

A BASIC-style interactive Python shell for CircuitPython devices with a CardKB I2C keyboard.  
Based on the original work of [Scott Shawcroft](https://github.com/tannewt/basicpython) — ported and extended by [@beboxos](https://twitter.com/beboxos).

---

## Hardware requirements

| Component | Details |
|---|---|
| Board | Adafruit PyPortal Titano (also works on Seeed WIO Terminal) |
| CircuitPython | 7.x or 8.x recommended |
| Keyboard | M5Stack CardKB (I2C, address 0x5F = 95) |
| Connection | CardKB → SCL / SDA pins of the board |

---

## Installation

1. Copy `basicpython.py` to the root of your CircuitPython drive (CIRCUITPY).
2. Either rename it `code.py` so it runs at boot, or import it from the REPL:
   ```python
   import basicpython
   ```

---

## Usage

Once running, you get a `READY.` prompt. You can:

- **Type a Python expression** directly to evaluate it: `print("hello")`, `1+2`, etc.
- **Enter a numbered line** to build a program (BASIC style): `10 x = 5`
- **Run commands** from the list below.

### Keyboard shortcuts (CardKB)

| Key | Action |
|---|---|
| `↑` | Previous command in history |
| `↓` | Next command in history |
| `←` | Move cursor left in current line |
| `→` | Move cursor right in current line |
| `Backspace` | Delete character before cursor |
| `Enter` | Validate input |

---

## Command reference

### Program editing

| Command | Description |
|---|---|
| `list` | Display all non-empty program lines with their numbers |
| `run` | Execute the current program |
| `new` | Clear the program and all variables |
| `N <code>` | Set line number N to `<code>` (e.g. `10 print("hi")`) |
| `N` | Type just a line number with no code → deletes that line |
| `del N` | Delete line N |
| `renum` | Remove blank lines and renumber from 1 |

**Example — writing a small program:**
```
>>> 10 for i in range(5):
>>> 20   print(i)
>>> list
10 for i in range(5):
20   print(i)
>>> run
0
1
2
3
4
```

---

### File I/O

| Command | Description |
|---|---|
| `save <file>` | Save the current program to a file |
| `load <file>` | Load a `.py` file into the program buffer |
| `cat <file>` | Print the contents of any file to the screen |

**Examples:**
```
>>> save /myprogram.py
Saved: /myprogram.py

>>> load /myprogram.py
Loaded: /myprogram.py - 2 lines

>>> cat /boot_out.txt
```

---

### Filesystem

| Command | Description |
|---|---|
| `dir [path]` | List directory contents with file sizes (default: `/`) |
| `cd [path]` | Change directory. No argument = show current path |
| `mkdir <dir>` | Create a new directory |
| `rmdir <dir>` | Remove an empty directory |
| `rm <file>` | Delete a file |
| `cp <src> <dst>` | Copy a file |
| `mv <src> <dst>` | Rename or move a file |

**Examples:**
```
>>> dir
Directory: /
--------------------------------
[lib]
[sd]
boot_out.txt            256 B
code.py                4096 B
--------------------------------
2 dir(s), 2 file(s)

>>> mkdir /projects
Created: /projects

>>> cp /myprogram.py /projects/myprogram.py
Copied: /myprogram.py -> /projects/myprogram.py

>>> cd /projects
/projects

>>> mv myprogram.py demo.py
Moved: myprogram.py -> demo.py
```

---

### System

| Command | Description |
|---|---|
| `mem` | Show RAM free / used (runs gc.collect() first) |
| `df` | Show flash disk total / used / free |
| `ver` | Show CircuitPython version, board name, CPU frequency and temperature |
| `cls` | Clear the screen |
| `reset` | Reboot the device (`microcontroller.reset()`) |
| `exit` | Exit BasicPython and return to the CircuitPython REPL |
| `!help` | Show the full command reference |

**Example output of `ver`:**
```
>>> ver
System  : samd51
Release : 8.0.5
Version : 8.0.5 on 2023-03-31
Machine : Adafruit PyPortal Titano with samd51j20
CPU freq: 120 MHz
CPU temp: 42.3 C
```

**Example output of `mem`:**
```
>>> mem
RAM free : 163840 B ( 160 KB)
RAM used :  28672 B ( 28 KB)
RAM total: 192512 B ( 188 KB)
```

**Example output of `df`:**
```
>>> df
Disk total: 8126464 B ( 7936 KB)
Disk used :  524288 B (  512 KB)
Disk free : 7602176 B ( 7424 KB)
```

---

## Evaluating Python directly

Any input that is not a recognized command is passed to `exec()`:

```
>>> import math
>>> math.sqrt(2)
1.4142135623730951
>>> [x*x for x in range(6)]
[0, 1, 4, 9, 16, 25]
```

Variables persist between evaluations during the session. Use `new` to reset them along with the program.

---

## Change log

| Version | Date | Changes |
|---|---|---|
| v0.01 | 2021-10 | Initial port to PyPortal Titano |
| v0.02 | 2021-10 | WIO Terminal support |
| v0.03 | 2021-10 | Arrow keys: history (↑↓) and inline editing (←→) |
| v0.04 | 2026-05 | Bug fixes + new commands: `new`, `cat`, `mkdir`, `rmdir`, `cp`, `mv`, `del`, `renum`, `mem`, `df`, `ver` — ANSI helpers extracted, compatibility fixes |

---

## Known limitations

- The `reset` command may cause filesystem corruption if the board is connected to a host computer (CircuitPython warning).
- `exec()` shares a single namespace (`top`) across all direct evaluations; use `new` to start fresh.
- Long lines may wrap oddly on small screens due to terminal width.
- `cp` reads files in 512-byte chunks — copying large files is slow but safe for RAM.

---

more: [@beboxos on Twitter](https://twitter.com/beboxos)
