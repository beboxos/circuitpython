#!/usr/bin/env python3
"""
Copy common/bebox_common/ into the lib/ folder of every project that uses it.

The reference copy is common/bebox_common/. The copies in each project's lib/
are generated: never edit them by hand, edit the reference and re-run this.

Usage:
    python3 tools/sync_common.py          # copy into every target
    python3 tools/sync_common.py --check  # fail if a copy is out of date (CI)
"""
import sys
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "common" / "bebox_common"

# Projects whose lib/ should receive bebox_common
TARGETS = [
    "pyportal titano/Circuitpyton launcher/lib",
    "pyportal titano/basicpython/lib",
    "MagTag/BootAppSelector/lib",
    "Keyboard_Featherwing/FeatherS2/lib",
    "WIO terminal/SmartTerminal/lib",
]


def files():
    return sorted(p for p in SOURCE.rglob("*.py"))


def copy():
    n = 0
    for target in TARGETS:
        dest = ROOT / target / "bebox_common"
        dest.mkdir(parents=True, exist_ok=True)
        for src in files():
            rel = src.relative_to(SOURCE)
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest / rel)
            n += 1
    print("Copied {} files into {} projects.".format(len(files()), len(TARGETS)))
    return n


def check():
    stale = []
    for target in TARGETS:
        dest = ROOT / target / "bebox_common"
        for src in files():
            rel = src.relative_to(SOURCE)
            copy_path = dest / rel
            if not copy_path.exists() or copy_path.read_bytes() != src.read_bytes():
                stale.append(str((pathlib.Path(target) / "bebox_common" / rel)))
    if stale:
        print("Out-of-date bebox_common copies:")
        for s in stale:
            print("  ", s)
        print("Run: python3 tools/sync_common.py")
        return 1
    print("All bebox_common copies are up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else (copy() and 0))
