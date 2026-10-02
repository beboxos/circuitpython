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
v0.05 - Works without CardKB: falls back to the USB serial console
        (arrow keys through ANSI escape sequences, DEL as backspace)
      - Fixed: crash at boot when no I2C device is connected
      - New: edit N      edit an existing line in place
      - New: auto [N[,S]] automatic line numbering (empty line to stop)
      - New: ins N code  insert a line, following lines are shifted down
      - New: list N / list N-M   list a range of lines
      - New: find text   search the program
      - New: run file    run a .py file without loading it
      - New: vars, history, time, ls (alias of dir)
      - New: save without name re-uses the last loaded / saved file
      - New: confirmation before new / load when the program is not saved
      - New: Home / End keys, Ctrl+C breaks a running program
      - Improved: expressions are echoed like the Python REPL (2+2 -> 4)
      - Improved: input() inside programs reads from the active keyboard
      - Improved: runtime errors show the traceback with line numbers
      - Improved: dir without argument lists the current directory
      - Refactor: command dispatch table instead of a long if/elif chain

more on twitter: https://twitter.com/beboxos
"""

import os
import gc
import sys
import time
import microcontroller

VERSION = "0.05"

# ============================================================
# Keyboard backends
# ============================================================
# Every backend returns one "key" per call: a single printable
# character, one of the KEY_* tokens below, or None if nothing
# was pressed.

KEY_ENTER, KEY_BS, KEY_UP, KEY_DOWN = "ENTER", "BS", "UP", "DOWN"
KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END = "LEFT", "RIGHT", "HOME", "END"

CARDKB_ADDR = 0x5F  # 95
CARDKB_KEYS = {
    0x0D: KEY_ENTER, 0x0A: KEY_ENTER, 0x08: KEY_BS, 0x7F: KEY_BS,
    0xB5: KEY_UP, 0xB6: KEY_DOWN, 0xB4: KEY_LEFT, 0xB7: KEY_RIGHT,
    0x99: KEY_HOME, 0xA4: KEY_END,  # Fn + left / Fn + right on CardKB
}


class CardKB:
    """M5Stack CardKB on I2C (address 0x5F)."""
    name = "CardKB (I2C)"

    def __init__(self, i2c):
        self.i2c = i2c
        self.buf = bytearray(1)

    def read(self):
        while not self.i2c.try_lock():
            pass
        try:
            self.i2c.readfrom_into(CARDKB_ADDR, self.buf)
        except OSError:
            return None
        finally:
            self.i2c.unlock()
        c = self.buf[0]
        if c == 0:
            return None
        if c in CARDKB_KEYS:
            return CARDKB_KEYS[c]
        if 32 <= c < 127:
            return chr(c)
        return None


class SerialKB:
    """USB serial console (any terminal: Mu, Thonny, screen, tio...)."""
    name = "USB serial"
    ESC_KEYS = {"A": KEY_UP, "B": KEY_DOWN, "C": KEY_RIGHT, "D": KEY_LEFT,
                "H": KEY_HOME, "F": KEY_END, "1": KEY_HOME, "4": KEY_END}

    def __init__(self):
        import supervisor
        self.runtime = supervisor.runtime

    def _getc(self):
        while not self.runtime.serial_bytes_available:
            pass
        return sys.stdin.read(1)

    def read(self):
        if not self.runtime.serial_bytes_available:
            return None
        c = sys.stdin.read(1)
        if c in ("\r", "\n"):
            return KEY_ENTER
        if c in ("\x08", "\x7f"):
            return KEY_BS
        if c == "\x1b":
            if self._getc() not in "[O":
                return None
            k = self._getc()
            if k in "14":  # ESC [ 1 ~  /  ESC [ 4 ~
                self._getc()
            return self.ESC_KEYS.get(k)
        if " " <= c <= "~":
            return c
        return None


def find_keyboard():
    try:
        import board
        import busio
        i2c = busio.I2C(board.SCL, board.SDA)
        while not i2c.try_lock():
            pass
        found = i2c.scan()
        i2c.unlock()
        if CARDKB_ADDR in found:
            return CardKB(i2c)
        i2c.deinit()
    except Exception:  # no I2C pins, no pull-ups, ...
        pass
    return SerialKB()


kb = find_keyboard()

# ============================================================
# ANSI terminal helpers
# ============================================================


def ansi(seq):
    return "\x1b[" + seq


def clear_screen():
    print(ansi("2J") + ansi("H"), end="")


def cursor_left(n=1):
    if n > 0:
        print(ansi(str(n) + "D"), end="")


def cursor_right(n=1):
    if n > 0:
        print(ansi(str(n) + "C"), end="")


# ============================================================
# Line editor
# ============================================================

history = []


def read_line(prompt="", initial="", use_history=True):
    """Read a line with history (up/down) and inline editing."""
    print(prompt + initial, end="")
    text = initial
    cur = len(text)
    hist = history + [text]
    hidx = len(hist) - 1

    def replace(new):
        nonlocal text, cur
        cursor_left(cur)
        print(new + " " * max(0, len(text) - len(new)), end="")
        cursor_left(max(0, len(text) - len(new)))
        text, cur = new, len(new)

    while True:
        key = kb.read()
        if key is None:
            continue
        if key == KEY_ENTER:
            break
        if key in (KEY_UP, KEY_DOWN) and use_history:
            hist[hidx] = text
            hidx = max(0, hidx - 1) if key == KEY_UP else min(len(hist) - 1, hidx + 1)
            replace(hist[hidx])
        elif key == KEY_LEFT and cur > 0:
            cursor_left()
            cur -= 1
        elif key == KEY_RIGHT and cur < len(text):
            print(text[cur], end="")
            cur += 1
        elif key == KEY_HOME:
            cursor_left(cur)
            cur = 0
        elif key == KEY_END:
            print(text[cur:], end="")
            cur = len(text)
        elif key == KEY_BS and cur > 0:
            tail = text[cur:]
            cursor_left()
            print(tail + " ", end="")
            cursor_left(len(tail) + 1)
            text = text[:cur - 1] + tail
            cur -= 1
        elif len(key) == 1:
            tail = text[cur:]
            print(key + tail, end="")
            cursor_left(len(tail))
            text = text[:cur] + key + tail
            cur += 1
    print()
    if use_history and text and (not history or history[-1] != text):
        history.append(text)
        if len(history) > 30:
            history.pop(0)
    return text


def kb_input(prompt=""):
    """Replacement for input() inside user programs."""
    return read_line(str(prompt), use_history=False)


# ============================================================
# Filesystem helpers
# ============================================================


def _is_dir(path):
    try:
        return os.stat(path)[0] & 0x4000 != 0
    except OSError:
        return False


def _file_size(path):
    try:
        return os.stat(path)[6]
    except OSError:
        return 0


def _copy_file(src, dst):
    """Copy src to dst in 512-byte chunks (memory-friendly)."""
    with open(src, "rb") as fin:
        with open(dst, "wb") as fout:
            while True:
                chunk = fin.read(512)
                if not chunk:
                    break
                fout.write(chunk)


def _arg(raw):
    return raw.strip(" \"'")


def _confirm(question):
    return read_line(question + " (y/n) ", use_history=False).strip().lower() in ("y", "yes", "o", "oui")


# ============================================================
# Program state
# ============================================================

program = []      # program[n-1] is BASIC line n
top = {"input": kb_input}
state = {"file": None, "dirty": False, "auto": None}


def set_line(n, code):
    if n > len(program):
        program.extend([""] * (n - len(program)))
    program[n - 1] = code
    state["dirty"] = True


def check_unsaved():
    if state["dirty"] and any(program):
        return _confirm("Program not saved. Continue?")
    return True


def print_line(n):
    print("{:>4} {}".format(n, program[n - 1]))


def print_exc(e):
    try:
        import traceback
        traceback.print_exception(e)
    except Exception:  # pylint: disable=broad-except
        print(type(e).__name__ + ":", e)


def run_source(source):
    scope = {"__name__": "__main__", "input": kb_input}
    try:
        exec(source, scope, scope)
    except KeyboardInterrupt:
        print("\nBREAK")
    except SystemExit:
        pass
    except Exception as e:  # pylint: disable=broad-except
        print("Runtime error:")
        print_exc(e)
    gc.collect()


# ============================================================
# Commands  (each one receives the text after the command name)
# ============================================================


def cmd_list(arg):
    if not any(program):
        print("(program is empty)")
        return
    first, last = 1, len(program)
    arg = arg.strip()
    try:
        if "-" in arg:
            a, b = arg.split("-", 1)
            first = int(a) if a.strip() else 1
            last = int(b) if b.strip() else len(program)
        elif arg:
            first = last = int(arg)
    except ValueError:
        print("Usage: list [N] | [N-M]")
        return
    for n in range(max(1, first), min(last, len(program)) + 1):
        if program[n - 1]:
            print_line(n)


def cmd_run(arg):
    name = _arg(arg)
    if name:
        try:
            with open(name) as f:
                src = f.read()
        except OSError as e:
            print("Error:", e)
            return
        run_source(src)
    else:
        run_source("\n".join(program))


def cmd_new(arg):
    if check_unsaved():
        program.clear()
        top.clear()
        top["input"] = kb_input
        state.update(file=None, dirty=False)
        print("Program cleared.")


def cmd_save(arg):
    name = _arg(arg) or state["file"]
    if not name:
        print("Usage: save <filename>")
        return
    try:
        with open(name, "w") as f:
            f.write("\n".join(ln for ln in program if ln) + "\n")
        state.update(file=name, dirty=False)
        print("Saved:", name)
    except OSError as e:
        print("Save error:", e, "(is CIRCUITPY writable? see boot.py in the manual)")


def cmd_load(arg):
    name = _arg(arg)
    if not name:
        print("Usage: load <filename>")
        return
    if not check_unsaved():
        return
    try:
        with open(name) as f:
            lines = [ln.rstrip("\r\n") for ln in f]
    except OSError as e:
        print("Load error:", e)
        return
    program[:] = lines
    state.update(file=name, dirty=False)
    print("Loaded:", name, "-", len(program), "lines")


def cmd_cat(arg):
    name = _arg(arg)
    if not name:
        print("Usage: cat <filename>")
        return
    try:
        with open(name) as f:
            for ln in f:
                print(ln, end="")
        print()
    except OSError as e:
        print("Error:", e)


def cmd_dir(arg):
    path = _arg(arg) or os.getcwd()
    try:
        entries = os.listdir(path)
    except OSError as e:
        print("Error:", e)
        return
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
    total = 0
    for name, sz in sorted(files):
        print("{:<20} {:>8} B".format(name, sz))
        total += sz
    print("-" * 32)
    print(len(dirs), "dir(s),", len(files), "file(s),", total, "bytes")


def cmd_cd(arg):
    path = _arg(arg)
    try:
        if path:
            os.chdir(path)
        print(os.getcwd())
    except OSError as e:
        print("Error:", e)


def _fs_cmd(func, usage, done, nargs=1):
    def cmd(arg):
        parts = arg.split() if nargs > 1 else [_arg(arg)]
        if len(parts) != nargs or not all(parts):
            print("Usage:", usage)
            return
        try:
            func(*parts)
            print(done, " -> ".join(parts))
        except OSError as e:
            print("Error:", e)
    return cmd


def cmd_del(arg):
    try:
        n = int(arg)
    except ValueError:
        print("Usage: del <line_number>")
        return
    if 1 <= n <= len(program):
        program[n - 1] = ""
        state["dirty"] = True
        print("Line", n, "deleted.")
    else:
        print("Line out of range (1 -", len(program), ")")


def cmd_ins(arg):
    num, _, code = arg.strip().partition(" ")
    try:
        n = int(num)
    except ValueError:
        n = 0
    if n < 1:
        print("Usage: ins <line_number> <code>")
        return
    if n > len(program):
        set_line(n, code)
    else:
        program.insert(n - 1, code)
        state["dirty"] = True
    print("Inserted line", n)


def cmd_edit(arg):
    try:
        n = int(arg)
    except ValueError:
        print("Usage: edit <line_number>")
        return
    if not 1 <= n <= len(program):
        print("Line out of range (1 -", len(program), ")")
        return
    set_line(n, read_line("{:>4} ".format(n), program[n - 1], use_history=False))


def cmd_auto(arg):
    start, _, step = arg.replace(" ", "").partition(",")
    try:
        start = int(start) if start else len(program) + 1
        step = int(step) if step else 1
    except ValueError:
        print("Usage: auto [start[,step]]")
        return
    state["auto"] = (max(1, start), max(1, step))
    print("AUTO mode - empty line to stop")


def cmd_renum(arg):
    program[:] = [ln for ln in program if ln.strip()]
    state["dirty"] = True
    print("Compacted to", len(program), "lines:")
    cmd_list("")


def cmd_find(arg):
    text = arg.strip()
    if not text:
        print("Usage: find <text>")
        return
    hits = [n for n, ln in enumerate(program, 1) if text in ln]
    for n in hits:
        print_line(n)
    print(len(hits), "match(es)")


def cmd_vars(arg):
    names = sorted(k for k in top if not k.startswith("_") and k != "input")
    if not names:
        print("(no variables)")
    for k in names:
        print("{:<12} = {!r}".format(k, top[k])[:60])


def cmd_history(arg):
    for i, h in enumerate(history, 1):
        print("{:>3} {}".format(i, h))


def cmd_mem(arg):
    gc.collect()
    free, alloc = gc.mem_free(), gc.mem_alloc()
    total = free + alloc
    print("RAM free :", free, "B (", free // 1024, "KB)")
    print("RAM used :", alloc, "B (", alloc // 1024, "KB)")
    print("RAM total:", total, "B (", total // 1024, "KB)")


def cmd_df(arg):
    try:
        st = os.statvfs("/")
    except OSError as e:
        print("Error:", e)
        return
    tot, free = st[2] * st[0], st[3] * st[0]
    print("Disk total:", tot, "B (", tot // 1024, "KB)")
    print("Disk used :", tot - free, "B (", (tot - free) // 1024, "KB)")
    print("Disk free :", free, "B (", free // 1024, "KB)")


def cmd_ver(arg):
    print("BasicPython v" + VERSION, "- keyboard:", kb.name)
    try:
        u = os.uname()
        print("System  :", u.sysname)
        print("Release :", u.release)
        print("Version :", u.version)
        print("Machine :", u.machine)
    except Exception as e:  # pylint: disable=broad-except
        print("os.uname error:", e)
    try:
        print("CPU freq:", microcontroller.cpu.frequency // 1000000, "MHz")
        temp = microcontroller.cpu.temperature
        if temp is not None:
            print("CPU temp:", temp, "C")
    except Exception:  # pylint: disable=broad-except
        pass


def cmd_time(arg):
    t = time.localtime()
    print("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[:6]))
    print("Uptime  : {:.0f} s".format(time.monotonic()))


def cmd_cls(arg):
    clear_screen()


def cmd_reset(arg):
    microcontroller.reset()


def cmd_exit(arg):
    if check_unsaved():
        raise SystemExit


HELP = """
=== BasicPython v{} command reference ===

  -- Program editing --
  list [N|N-M]  list program lines
  run [file]    run the program (or a .py file)
  new           clear program and variables
  N <code>      set line N to <code>
  N             (no code) delete line N
  edit N        edit line N in place
  ins N <code>  insert a line, shift the following ones
  del N         delete line N
  auto [N[,S]]  automatic line numbers (empty line stops)
  renum         remove blank lines, renumber from 1
  find <text>   search the program

  -- File I/O --
  load <file>   load a .py file as program
  save [file]   save program (no name: last file)
  cat  <file>   print file contents

  -- Filesystem --
  dir / ls [p]  list directory (default: current)
  cd   [path]   change directory (no arg: show cwd)
  mkdir <dir>   create directory
  rmdir <dir>   remove empty directory
  rm   <file>   delete file
  cp   <s> <d>  copy file
  mv   <s> <d>  rename / move file

  -- System --
  vars          show variables
  history       show typed commands
  mem / df      RAM / flash usage
  ver / time    board info / clock and uptime
  cls           clear screen
  reset         reboot device
  exit          return to the CircuitPython REPL

  Anything else is executed as Python (expressions are printed).
""".format(VERSION)


COMMANDS = {
    "list": cmd_list, "run": cmd_run, "new": cmd_new,
    "save": cmd_save, "load": cmd_load, "cat": cmd_cat,
    "dir": cmd_dir, "ls": cmd_dir, "cd": cmd_cd,
    "mkdir": _fs_cmd(os.mkdir, "mkdir <dirname>", "Created:"),
    "rmdir": _fs_cmd(os.rmdir, "rmdir <dirname>", "Removed dir:"),
    "rm": _fs_cmd(os.remove, "rm <filename>", "Removed:"),
    "cp": _fs_cmd(_copy_file, "cp <source> <dest>", "Copied:", 2),
    "mv": _fs_cmd(os.rename, "mv <source> <dest>", "Moved:", 2),
    "del": cmd_del, "ins": cmd_ins, "edit": cmd_edit, "auto": cmd_auto,
    "renum": cmd_renum, "find": cmd_find, "vars": cmd_vars,
    "history": cmd_history, "mem": cmd_mem, "df": cmd_df, "ver": cmd_ver,
    "time": cmd_time, "cls": cmd_cls, "reset": cmd_reset, "exit": cmd_exit,
    "!help": lambda arg: print(HELP), "help": lambda arg: print(HELP),
}


def execute_python(line):
    """Evaluate like the REPL: print expression results, exec statements."""
    try:
        try:
            result = eval(line, top, top)
        except SyntaxError:  # a statement, not an expression
            exec(line, top, top)
        else:
            if result is not None:
                print(repr(result))
                top["_"] = result
    except KeyboardInterrupt:
        print("\nBREAK")
    except Exception as e:  # pylint: disable=broad-except
        print("Error:", type(e).__name__ + ":", e)


def handle(line):
    command, _, remainder = line.strip().partition(" ")
    try:
        lineno = int(command, 10)
    except ValueError:
        lineno = None

    if lineno is not None:
        if lineno < 1:
            print("Line must be >= 1")
        elif remainder.strip():
            set_line(lineno, remainder)
            return True  # no READY. after a program line
        elif lineno <= len(program):
            program[lineno - 1] = ""
            state["dirty"] = True
            print("Line", lineno, "deleted.")
        return False

    func = COMMANDS.get(command.lower())
    if func:
        func(remainder)
    elif command:
        execute_python(line)
    return False


# ============================================================
# Main loop
# ============================================================

clear_screen()
print("""
***********************************************************
*  ___            _      ___  _  _  _    _                *
* | _ ) __ _  ___(_) __ | _ \\| || || |_ | |_   ___  _ _   *
* | _ \\/ _` |(_-/| |/ _||  _/ \\_.  ||  _||   \\ / _ \\| ' \\  *
* |___/\\__/_|/__/|_|\\__||_|   |__/  \\__||_||_|\\___/|_||_| *
***********************************************************""")
print("v{} for CircuitPython - keyboard: {}".format(VERSION, kb.name))
print("Enter help for command list\n")

quiet = False
while True:
    try:
        if state["auto"]:
            n, step = state["auto"]
            code = read_line("{:>4} ".format(n), use_history=False)
            if code.strip():
                set_line(n, code)
                state["auto"] = (n + step, step)
            else:
                state["auto"] = None
            continue
        line = read_line(">>>" if quiet else "READY.\n>>>")
        quiet = handle(line)
    except KeyboardInterrupt:
        state["auto"] = None
        print("\nBREAK")
    except SystemExit:
        break
