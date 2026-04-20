# Linux Keyboard Layout

## Problem
Writing on a US keyboard is ideal for software development, but switching layouts to type German umlauts (ä, ö, ü, ß) is cumbersome.

## Solution
This layout is based on the standard US keyboard. German umlauts are accessible by holding the `Alt` key and pressing the corresponding key. `Shift+Alt` gives uppercase umlauts.

| Keys         | Result |
|--------------|--------|
| Alt + a      | ä      |
| Shift+Alt + a| Ä      |
| Alt + o      | ö      |
| Shift+Alt + o| Ö      |
| Alt + u      | ü      |
| Shift+Alt + u| Ü      |
| Alt + s      | ß      |

## Installation

### Quick install (recommended)

```bash
make prepare       # check and install dependencies
make check         # verify current status
sudo make install  # install layout system-wide
```

Then **log out and log back in** (or reboot). After that:

> Settings → Keyboard → Input Sources → `+` → search for **"German (US Mix)"**

### Manual installation steps

If you prefer to install manually:

1. Copy the layout file:
   ```bash
   sudo cp linux/de-en-mix /usr/share/X11/xkb/symbols/
   ```

2. Add the following entry under `<layoutList>` in **both** files:
   - `/usr/share/X11/xkb/rules/base.extras.xml`
   - `/usr/share/X11/xkb/rules/evdev.extras.xml`

   ```xml
   <layout>
     <configItem popularity="exotic">
       <name>de-en-mix</name>
       <shortDescription>de</shortDescription>
       <description>German (US Mix)</description>
       <languageList>
         <iso639Id>deu</iso639Id>
       </languageList>
     </configItem>
     <variantList/>
   </layout>
   ```

3. Log out and back in, then add the layout in Settings → Keyboard → Input Sources.

> **Note:** `evdev.extras.xml` is the relevant file for Ubuntu/GNOME (uses `evdev` rules).
> `base.extras.xml` is also updated for completeness.
> Do **not** edit `base.xml` or `evdev.xml` — those are system files overwritten on package updates.

## Makefile commands

| Command            | Description                                        |
|--------------------|----------------------------------------------------|
| `make prepare`     | Check dependencies, offer to install missing ones  |
| `make check`       | Show detailed installation status                  |
| `sudo make install`| Install layout system-wide (idempotent)            |
| `sudo make update` | Update only the symbol file (e.g. after changes)   |
| `sudo make uninstall` | Remove the layout completely                    |
| `make load`        | Temporarily activate for this session (no sudo, no reboot) |

### `make load` — what it does
Loads the layout via `setxkbmap` directly from the local source file. It is active immediately in the current X session. It does **not** appear in the GNOME layout menu and reverts after logout. Useful for quick testing before a full install.

## Technical details

- The installer is written in Python 3 and uses `lxml` for XML handling (falls back to `xml.etree.ElementTree` if `lxml` is not available).
- A Python venv is automatically created at `linux/.venv` on first run.
- All modifications to system XML files are backed up with a timestamp before changes are made (e.g. `evdev.extras.xml.backup_20250413_150000`).

## Troubleshooting

- **Layout not visible after install:** Log out and back in, or reboot. GNOME caches layout lists at session start.
- **Verify registration:** `localectl list-x11-keymap-layouts | grep de-en`
- **Test without install:** `make load`
- **Partial install detected by `make check`:** Run `sudo make install` again — it will complete any missing steps.

## License
MIT License (see `LICENSE` file).
