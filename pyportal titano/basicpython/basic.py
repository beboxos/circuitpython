"""
basic.py - a Tiny BASIC interpreter for BasicPython (BeBoX, 2026).

A small line-numbered BASIC, in the spirit of the 8-bit home computers.
It is used by basicpython.py when the BASIC engine is selected (`basic`
command), and it can be used on its own:

    import basic
    basic.run(["10 PRINT \"HELLO\"", "20 GOTO 10"])

Supported statements
    PRINT a; b, c      REM comment        LET A = expr    (LET optional)
    INPUT "p"; A       IF c THEN stmt     IF c THEN 100   (THEN line = GOTO)
    GOTO n             GOSUB n / RETURN   FOR A=1 TO 9 [STEP 2] ... NEXT [A]
    END / STOP         CLS                COLOR n
    PLOT x,y           LINE x1,y1,x2,y2   BEEP [freq[,ms]]
    WAIT ms (= pause)

Expressions use + - * / MOD, parentheses, the comparisons = <> < > <= >=,
AND OR NOT, and the functions ABS INT RND SGN SQR MOD LEN CHR ASC
MIN MAX. String variables end with $ (A$). Numbers are ints when possible.

Graphics and sound are optional: they need a `hooks` object (see run()).
Without one they just print a short notice, so a program still runs on any
board or on a PC.
"""
import math
import random


class BasicError(Exception):
    pass


# --- expression translation BASIC -> Python --------------------------------

def _translate_expr(expr, names):
    """Turn a BASIC expression into a Python one. `names` maps BASIC variable
    names (upper-case, $ kept) to safe Python identifiers."""
    out = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c == '"':  # string literal: copy verbatim up to the closing quote
            j = i + 1
            while j < n and expr[j] != '"':
                j += 1
            out.append(expr[i:j + 1])
            i = j + 1
            continue
        if c == "<" and i + 1 < n and expr[i + 1] == ">":
            out.append("!=")
            i += 2
            continue
        if c in "<>" and i + 1 < n and expr[i + 1] == "=":
            out.append(c + "=")
            i += 2
            continue
        if c == "=":  # single = is equality in an expression
            out.append("==")
            i += 1
            continue
        if c.isalpha() or c == "_":  # identifier / keyword / function
            j = i
            while j < n and (expr[j].isalnum() or expr[j] in "_$"):
                j += 1
            word = expr[i:j]
            up = word.upper()
            if up in _OPERATORS:
                out.append(_OPERATORS[up])
            elif up in _FUNCTIONS:
                out.append(_FUNCTIONS[up])
            else:
                out.append(names.setdefault(up, "_v_" + up.replace("$", "_s")))
            i = j
            continue
        out.append(c)
        i += 1
    return "".join(out)


_OPERATORS = {"AND": " and ", "OR": " or ", "NOT": " not ", "MOD": " % "}
_FUNCTIONS = {
    "ABS": "abs", "INT": "int", "LEN": "len", "STR": "str", "VAL": "float",
    "CHR": "chr", "ASC": "ord", "MIN": "min", "MAX": "max",
    "SQR": "math.sqrt", "SGN": "_sgn", "RND": "_rnd",
}


def _sgn(x):
    return (x > 0) - (x < 0)


def _rnd(n=1):
    """RND(n): integer 1..n if n>=1, else a float in [0,1) like old BASICs."""
    if n and n >= 1:
        return random.randint(1, int(n))
    return random.random()


# --- interpreter -----------------------------------------------------------

class Interpreter:
    def __init__(self, hooks=None, printer=print, reader=input):
        self.hooks = hooks            # optional graphics/sound backend
        self.printer = printer        # output function
        self.reader = reader          # input() replacement
        self.vars = {}                # safe-name -> value
        self.names = {}               # BASIC name -> safe name
        self.order = []               # sorted line numbers
        self.index = {}               # line number -> position in order
        self.lines = {}               # line number -> raw statement text
        self.stack = []               # GOSUB return addresses (positions)
        self.for_stack = []           # (safe_name, limit, step, position)

    # -- expression / value helpers --
    def _eval(self, expr):
        py = _translate_expr(expr, self.names)
        env = {"math": math, "_sgn": _sgn, "_rnd": _rnd,
               "abs": abs, "int": int, "len": len, "str": str, "float": float,
               "chr": chr, "ord": ord, "min": min, "max": max}
        env.update(self.vars)
        try:
            val = eval(py, {"__builtins__": {}}, env)  # noqa: S307
        except Exception as e:
            raise BasicError(str(e))
        if isinstance(val, float) and val == int(val):
            val = int(val)
        return val

    def _safe(self, basic_name):
        up = basic_name.upper()
        return self.names.setdefault(up, "_v_" + up.replace("$", "_s"))

    # -- program loading --
    def load(self, source_lines):
        self.lines.clear()
        for raw in source_lines:
            raw = raw.strip()
            if not raw:
                continue
            num, _, rest = raw.partition(" ")
            try:
                ln = int(num)
            except ValueError:
                raise BasicError("Missing line number: " + raw)
            self.lines[ln] = rest.strip()
        self.order = sorted(self.lines)
        self.index = {ln: i for i, ln in enumerate(self.order)}

    # -- run --
    def run(self):
        self.vars.clear()
        self.stack = []
        self.for_stack = []
        pc = 0
        while pc < len(self.order):
            ln = self.order[pc]
            jump = self._exec(self.lines[ln], ln)
            if jump is None:
                pc += 1
            elif jump == "END":
                break
            else:
                if jump not in self.index:
                    raise BasicError("No line {} (from {})".format(jump, ln))
                pc = self.index[jump]

    # -- a single statement; returns None, a target line number, or "END" --
    def _exec(self, stmt, ln):
        if not stmt:
            return None
        head, _, rest = stmt.partition(" ")
        kw = head.upper()
        rest = rest.strip()

        if kw == "REM":
            return None
        if kw == "PRINT" or kw == "?":
            return self._print(rest)
        if kw == "LET":
            return self._assign(rest)
        if kw == "INPUT":
            return self._input(rest)
        if kw == "GOTO":
            return int(self._eval(rest))
        if kw == "GOSUB":
            self.stack.append(self.index[ln])  # remember where we called from
            return int(self._eval(rest))
        if kw == "RETURN":
            if not self.stack:
                raise BasicError("RETURN without GOSUB")
            pos = self.stack.pop()
            if pos + 1 >= len(self.order):
                return "END"
            return self.order[pos + 1]  # line after the GOSUB
        if kw == "IF":
            return self._if(rest, ln)
        if kw == "FOR":
            return self._for(rest, ln)
        if kw == "NEXT":
            return self._next(rest)
        if kw in ("END", "STOP"):
            return "END"
        if kw == "CLS":
            return self._hook("cls")
        if kw == "COLOR":
            return self._hook("color", int(self._eval(rest)))
        if kw == "PLOT":
            a = [int(self._eval(x)) for x in rest.split(",")]
            return self._hook("plot", *a)
        if kw == "LINE":
            a = [int(self._eval(x)) for x in rest.split(",")]
            return self._hook("line", *a)
        if kw == "BEEP":
            a = [int(self._eval(x)) for x in rest.split(",")] if rest else []
            return self._hook("beep", *a)
        if kw in ("WAIT", "PAUSE"):
            import time
            time.sleep(self._eval(rest) / 1000.0)
            return None
        # implicit assignment:  A = expr
        if "=" in stmt:
            return self._assign(stmt)
        raise BasicError("Syntax error: " + stmt)

    # -- statement handlers --
    def _print(self, rest):
        if not rest:
            self.printer("")
            return None
        # split on top-level ; and , keeping the separators
        parts = []
        buf = ""
        depth = 0
        instr = False
        for c in rest:
            if c == '"':
                instr = not instr
            elif not instr and c == "(":
                depth += 1
            elif not instr and c == ")":
                depth -= 1
            if c in ";," and depth == 0 and not instr:
                parts.append((buf, c))
                buf = ""
            else:
                buf += c
        parts.append((buf, ""))
        out = ""
        for expr, sep in parts:
            expr = expr.strip()
            if expr:
                out += self._fmt(self._eval(expr))
            if sep == ",":
                out += "\t"
        # a trailing ; or , suppresses the newline
        end = "" if rest.rstrip()[-1:] in ";," else "\n"
        self.printer(out, end=end)
        return None

    def _fmt(self, val):
        if isinstance(val, float) and val == int(val):
            val = int(val)
        return str(val)

    def _assign(self, rest):
        name, _, expr = rest.partition("=")
        name = name.strip()
        if not name or not expr.strip():
            raise BasicError("Bad assignment: " + rest)
        self.vars[self._safe(name)] = self._eval(expr)
        return None

    def _input(self, rest):
        prompt = "? "
        target = rest
        if '"' in rest:
            close = rest.index('"', 1)
            prompt = rest[1:close]
            target = rest[close + 1:].lstrip(" ;,")
        name = target.strip()
        raw = self.reader(prompt)
        if name.endswith("$"):
            self.vars[self._safe(name)] = raw
        else:
            try:
                num = float(raw)
                self.vars[self._safe(name)] = int(num) if num == int(num) else num
            except ValueError:
                self.vars[self._safe(name)] = 0
        return None

    def _if(self, rest, ln):
        up = rest.upper()
        pos = up.find(" THEN ")
        if pos < 0:
            if up.endswith(" THEN"):
                raise BasicError("IF ... THEN needs a statement")
            raise BasicError("IF without THEN")
        cond = rest[:pos]
        then = rest[pos + 6:].strip()
        if not self._eval(cond):
            return None
        try:  # THEN <line number> is a GOTO
            return int(then)
        except ValueError:
            return self._exec(then, ln)

    def _for(self, rest, ln):
        head, _, rng = rest.partition("=")
        var = self._safe(head.strip())
        up = rng.upper()
        to = up.find(" TO ")
        if to < 0:
            raise BasicError("FOR without TO")
        start = rng[:to]
        after = rng[to + 4:]
        step_pos = after.upper().find(" STEP ")
        if step_pos >= 0:
            limit_expr = after[:step_pos]
            step = self._eval(after[step_pos + 6:])
        else:
            limit_expr = after
            step = 1
        self.vars[var] = self._eval(start)
        self.for_stack.append((var, self._eval(limit_expr), step, self.index[ln]))
        return None

    def _next(self, rest):
        if not self.for_stack:
            raise BasicError("NEXT without FOR")
        var, limit, step, pos = self.for_stack[-1]
        self.vars[var] += step
        if (step >= 0 and self.vars[var] <= limit) or \
           (step < 0 and self.vars[var] >= limit):
            return self.order[pos + 1]  # loop back to the line after FOR
        self.for_stack.pop()
        return None

    def _hook(self, name, *args):
        if self.hooks and hasattr(self.hooks, name):
            getattr(self.hooks, name)(*args)
        else:
            self.printer("[{} {}]".format(name.upper(),
                                          " ".join(str(a) for a in args)))
        return None


def run(source_lines, hooks=None, printer=print, reader=input):
    """Convenience: load and run a list of BASIC source lines."""
    interp = Interpreter(hooks=hooks, printer=printer, reader=reader)
    interp.load(source_lines)
    interp.run()
    return interp
