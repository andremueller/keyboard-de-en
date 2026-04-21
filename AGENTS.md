# AGENTS.md

## Repository Overview
- Custom keyboard layouts for macOS, Windows, and Linux for German software developers who prefer the US layout but need occasional German umlauts (ä, ö, ü, ß).

## Key Files
- `macos/EN_DE_Mix_Keylayout.keylayout`: macOS keyboard layout
- `windows/EN-DE-Accents.klc`: Windows keyboard layout
- `linux/de-en-mix`: XKB symbol file (Ubuntu/Linux)
- `linux/install.py`: Python installer (check/install/update/uninstall/load)
- `linux/install.sh`: Bash wrapper — sets up Python venv and calls `install.py`
- `linux/requirements.txt`: Python deps (`lxml`; falls back to stdlib if unavailable)
- `Makefile`: Convenience targets for the Linux installer

## Linux installer — critical facts

- **Ubuntu 24.04 / GNOME 46: `evdev.extras.xml` and `base.extras.xml` are NOT read** by libxkbcommon or GNOME. These files exist in the package but are never merged into the main XML. They are effectively dead on Ubuntu 24.04.
- **The layout must be registered directly in `evdev.xml` and `base.xml`** — these are the files actually read by libxkbcommon/GNOME/localectl. Yes, they are overwritten by `apt upgrade xkb-data`; re-run `sudo make install` after such an upgrade.
- The layout uses `include "level3(alt_switch)"` so the regular `Alt` key (not AltGr) activates umlauts.
- After installation a **logout/login or reboot** is required for GNOME to pick up the new layout.
- `make load` uses `setxkbmap -I linux/ de-en-mix` — loads the layout temporarily for the current X session without installing; does not appear in GNOME menu.
- The Python venv is created automatically at `linux/.venv` on first run of any `make` target.
- All system XML file modifications are backed up with a timestamp before being changed.

## Makefile targets (run from repo root)
```
make prepare     # check deps, offer apt install for missing ones
make check       # show installation status (exit 0=ok, 1=not installed, 2=partial)
sudo make install   # idempotent full install
sudo make update    # update only the symbol file
sudo make uninstall # full removal
make load        # temporary session load (no sudo)
```

## Installation paths (Linux)
- Symbol file: `/usr/share/X11/xkb/symbols/de-en-mix`
- Registered in: `/usr/share/X11/xkb/rules/base.xml`
- Registered in: `/usr/share/X11/xkb/rules/evdev.xml`

## Layout key mappings
- Alt+a/o/u/s → ä/ö/ü/ß
- Shift+Alt+a/o/u → Ä/Ö/Ü
- macOS/Linux use `Alt`; Windows uses `AltGr` / `Ctrl+Alt`
