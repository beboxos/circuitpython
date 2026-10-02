#!/usr/bin/env python3
"""
Build one ready-to-copy .zip per project into dist/.

Each zip contains the files you drop onto CIRCUITPY (code.py, lib/, assets...).
It does NOT bundle the Adafruit libraries: install them with
`circup install -r requirements.txt` after copying, as each project's README
explains.

Usage:
    python3 tools/make_release_zips.py          # -> dist/*.zip
"""
import os
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# project name -> folder to zip
PROJECTS = {
    "basicpython": "pyportal titano/basicpython",
    "pyportal-launcher": "pyportal titano/Circuitpyton launcher",
    "tembed-timer": "T-embed/simple timer/CIRCUITPY",
    "tembed-multitool": "T-embed/multi tool/CIRCUITPY",
    "badger2040": "badger2040/CIRCUITPY",
    "magtag-bootselector": "MagTag/BootAppSelector",
    "keyboard-featherwing-feathers2": "Keyboard_Featherwing/FeatherS2",
    "keyboard-featherwing-m4": "Keyboard_Featherwing/M4_Express_Feather",
    "pico-duckypad": "pico RGB Keyboard/DuckyPad",
    "challenger2040wifi": "Challenger2040WiFi/CIRCUITPY",
    "atmegazero-bootmenu": "ATMegaZero S2/BootMenu",
    "seeed-xiao-uarttohid": "Seeed XIAO/UartToHID",
    "wio-smartterminal": "WIO terminal/SmartTerminal",
}

SKIP = {".DS_Store", "__pycache__", ".git"}


def build():
    DIST.mkdir(exist_ok=True)
    made = []
    for name, rel in PROJECTS.items():
        base = ROOT / rel
        if not base.is_dir():
            print("skip (missing):", rel)
            continue
        out = DIST / (name + ".zip")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for path in sorted(base.rglob("*")):
                if any(part in SKIP for part in path.parts):
                    continue
                if path.is_file():
                    z.write(path, path.relative_to(base))
        made.append((name, out.stat().st_size))
        print("built {}  ({} KB)".format(out.name, out.stat().st_size // 1024))
    print("\n{} zip(s) in {}".format(len(made), DIST))
    return made


if __name__ == "__main__":
    build()
