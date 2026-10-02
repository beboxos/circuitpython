"""
bebox_common.launcher - find and start CircuitPython apps.

    from bebox_common.launcher import find_apps, launch
    apps = find_apps()          # .py files in / and /apps, minus the system ones
    launch(apps[0])             # runs it in a fresh interpreter, menu comes back

launch() uses supervisor.set_next_code_file() (CircuitPython 8+): the app runs
in a clean interpreter and, when it ends (normally or with an error), the
launcher's own code file is loaded again. On very old firmware it falls back to
exec().
"""
import os

APP_DIRS = ("/", "/apps")
DEFAULT_EXCLUDE = ("code.py", "main.py", "boot.py", "boot_out.txt",
                   "secrets.py", "settings.py", "settings.toml")


def find_apps(dirs=APP_DIRS, exclude=()):
    """Return a sorted list of launchable .py paths."""
    skip = set(DEFAULT_EXCLUDE)
    skip.update(exclude)
    extra = os.getenv("LAUNCHER_EXCLUDE") or ""
    skip.update(n.strip() for n in extra.split(",") if n.strip())
    apps = []
    for folder in dirs:
        try:
            names = os.listdir(folder)
        except OSError:
            continue
        for n in names:
            if n.endswith(".py") and not n.startswith(".") and n not in skip:
                apps.append(folder.rstrip("/") + "/" + n)
    return sorted(apps, key=lambda p: p.rsplit("/", 1)[-1].lower())


def launch(path, menu="code.py"):
    """Start the app at `path`; return to `menu` when it ends."""
    try:
        import supervisor
    except ImportError:
        supervisor = None
    if supervisor is not None and hasattr(supervisor, "set_next_code_file"):
        # the app runs next; when it ends, the menu (code.py) is loaded again
        supervisor.set_next_code_file(path, reload_on_success=True,
                                      reload_on_error=True)
        supervisor.reload()
    else:  # legacy firmware: run in place, best effort
        with open(path) as f:
            exec(f.read(), {"__name__": "__main__"})  # noqa: S102


def back_to_menu():
    """Call from inside an app to return to the launcher."""
    try:
        import supervisor
        supervisor.reload()
    except ImportError:
        pass
