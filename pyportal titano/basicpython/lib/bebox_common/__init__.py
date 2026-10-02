"""
bebox_common - shared helpers for BeBoX CircuitPython projects.

- bebox_common.keyboard : one API for M5Stack CardKB, BlackBerry Q10
  (Keyboard FeatherWing) and the USB serial console.
- bebox_common.launcher : find and start apps with
  supervisor.set_next_code_file() (NVM + exec fallback for old firmware).

The reference copy lives in common/bebox_common/ in the repository.
tools/sync_common.py copies it into the lib/ folder of every project that
uses it; never edit the copies.
"""
__version__ = "1.0.0"
