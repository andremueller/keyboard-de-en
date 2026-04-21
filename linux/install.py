#!/usr/bin/env python3
"""
Installer for the German (US Mix) keyboard layout on Ubuntu/Linux.

Commands:
  check     - Check installation status
  prepare   - Check and install missing dependencies
  install   - Install the layout system-wide (requires sudo)
  update    - Update only the layout file (requires sudo)
  uninstall - Remove the layout (requires sudo)
  load      - Temporarily load the layout for this session (no sudo needed)
"""

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from lxml import etree as ET
    LXML_AVAILABLE = True
except ImportError:
    import xml.etree.ElementTree as ET
    LXML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

LAYOUT_SRC = SCRIPT_DIR / "de-en-mix"
LAYOUT_DEST = Path("/usr/share/X11/xkb/symbols/de-en-mix")

XKB_RULES = Path("/usr/share/X11/xkb/rules")
BASE_EXTRAS = XKB_RULES / "base.extras.xml"
EVDEV_EXTRAS = XKB_RULES / "evdev.extras.xml"

LAYOUT_NAME = "de-en-mix"
LAYOUT_SHORT = "de"
LAYOUT_DESCRIPTION = "German (US Mix)"
LAYOUT_LANG = "deu"
LAYOUT_COUNTRY = "DE"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def info(msg: str) -> None:
    print(f"  [INFO]  {msg}")

def ok(msg: str) -> None:
    print(f"  [ OK ]  {msg}")

def warn(msg: str) -> None:
    print(f"  [WARN]  {msg}")

def error(msg: str) -> None:
    print(f" [ERROR]  {msg}", file=sys.stderr)

def header(msg: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")

def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=capture, text=True)

def backup_file(path: Path) -> Path:
    """Create a timestamped backup of a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".backup_{timestamp}")
    shutil.copy2(path, backup_path)
    ok(f"Backup created: {backup_path}")
    return backup_path

def require_sudo() -> None:
    if os.geteuid() != 0:
        error("This command requires root privileges. Please run with sudo.")
        error("  Example: sudo make install")
        sys.exit(1)

# ---------------------------------------------------------------------------
# XML helpers (works with both lxml and stdlib)
# ---------------------------------------------------------------------------

def _parse_xml(path: Path):
    """Parse XML preserving comments; returns (tree, root)."""
    if LXML_AVAILABLE:
        parser = ET.XMLParser(remove_comments=False)
        tree = ET.parse(str(path), parser)
        return tree, tree.getroot()
    else:
        tree = ET.parse(str(path))
        return tree, tree.getroot()

def _layout_entry_exists(root, name: str) -> bool:
    """Check if a layout with given name already exists in the XML."""
    for layout in root.iter("layout"):
        for ci in layout.findall("configItem"):
            n = ci.find("name")
            if n is not None and n.text == name:
                return True
    return False

def _build_layout_element(use_lxml: bool):
    """Build a <layout> XML element."""
    layout = ET.Element("layout")
    ci = ET.SubElement(layout, "configItem")
    ci.set("popularity", "exotic")
    name_el = ET.SubElement(ci, "name")
    name_el.text = LAYOUT_NAME
    short = ET.SubElement(ci, "shortDescription")
    short.text = LAYOUT_SHORT
    desc = ET.SubElement(ci, "description")
    desc.text = LAYOUT_DESCRIPTION
    country_list = ET.SubElement(ci, "countryList")
    country = ET.SubElement(country_list, "iso3166Id")
    country.text = LAYOUT_COUNTRY
    lang_list = ET.SubElement(ci, "languageList")
    lang = ET.SubElement(lang_list, "iso639Id")
    lang.text = LAYOUT_LANG
    ET.SubElement(layout, "variantList")
    return layout

def _indent_lxml(elem, level: int = 0) -> None:
    """Add pretty-print indentation (lxml)."""
    pad = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = pad + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = pad
        for child in elem:
            _indent_lxml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = pad
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = pad

def _write_xml(tree, path: Path) -> None:
    """Write XML tree back to file."""
    if LXML_AVAILABLE:
        tree.write(str(path), xml_declaration=True, encoding="utf-8", pretty_print=True)
    else:
        ET.indent(tree.getroot(), space="  ")
        tree.write(str(path), xml_declaration=True, encoding="unicode")

def add_layout_to_xml(xml_path: Path) -> bool:
    """
    Add the layout entry to an extras XML file.
    Returns True if entry was added, False if it already existed.
    """
    tree, root = _parse_xml(xml_path)

    if _layout_entry_exists(root, LAYOUT_NAME):
        return False  # already present

    layout_list = root.find("layoutList")
    if layout_list is None:
        error(f"  No <layoutList> found in {xml_path}")
        sys.exit(1)

    new_entry = _build_layout_element(LXML_AVAILABLE)

    # Insert as first child of <layoutList>
    layout_list.insert(0, new_entry)

    _write_xml(tree, xml_path)
    return True

def remove_layout_from_xml(xml_path: Path) -> bool:
    """
    Remove the layout entry from an extras XML file.
    Returns True if entry was removed, False if it was not present.
    """
    tree, root = _parse_xml(xml_path)
    layout_list = root.find("layoutList")
    if layout_list is None:
        return False

    to_remove = None
    for layout in layout_list.findall("layout"):
        for ci in layout.findall("configItem"):
            n = ci.find("name")
            if n is not None and n.text == LAYOUT_NAME:
                to_remove = layout
                break
        if to_remove is not None:
            break

    if to_remove is None:
        return False

    layout_list.remove(to_remove)
    _write_xml(tree, xml_path)
    return True

# ---------------------------------------------------------------------------
# Status checks
# ---------------------------------------------------------------------------

STATUS_OK = 0
STATUS_NOT_INSTALLED = 1
STATUS_PARTIAL = 2

def check_status() -> dict:
    symbol_ok = LAYOUT_DEST.exists()
    _, root_base = _parse_xml(BASE_EXTRAS)
    _, root_evdev = _parse_xml(EVDEV_EXTRAS)
    base_ok = _layout_entry_exists(root_base, LAYOUT_NAME)
    evdev_ok = _layout_entry_exists(root_evdev, LAYOUT_NAME)

    symbol_uptodate = (
        symbol_ok and LAYOUT_SRC.exists() and filecmp.cmp(LAYOUT_SRC, LAYOUT_DEST, shallow=False)
    )

    return {
        "symbol_file": symbol_ok,
        "symbol_uptodate": symbol_uptodate,
        "base_extras": base_ok,
        "evdev_extras": evdev_ok,
    }

def overall_status(s: dict) -> int:
    all_ok = s["symbol_file"] and s["base_extras"] and s["evdev_extras"]
    any_ok = s["symbol_file"] or s["base_extras"] or s["evdev_extras"]
    if all_ok:
        return STATUS_OK
    elif any_ok:
        return STATUS_PARTIAL
    return STATUS_NOT_INSTALLED

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_check() -> int:
    header("Checking installation status")

    info(f"Using lxml for XML handling: {LXML_AVAILABLE}")
    info(f"Layout source:    {LAYOUT_SRC}")
    info(f"Layout installed: {LAYOUT_DEST}")

    s = check_status()

    print()
    _print_check("Layout symbol file present", s["symbol_file"])
    _print_check("Layout symbol file up-to-date", s["symbol_uptodate"])
    _print_check(f"Registered in base.extras.xml", s["base_extras"])
    _print_check(f"Registered in evdev.extras.xml", s["evdev_extras"])
    print()

    status = overall_status(s)
    if status == STATUS_OK:
        if s["symbol_uptodate"]:
            ok("Layout is fully installed and up-to-date.")
        else:
            warn("Layout is installed but the symbol file differs from the source.")
            warn("Run 'make update' to apply changes.")
    elif status == STATUS_PARTIAL:
        warn("Layout is PARTIALLY installed. Run 'make install' to fix.")
    else:
        info("Layout is NOT installed. Run 'make install' to install.")

    return status

def _print_check(label: str, value: bool) -> None:
    mark = "✓" if value else "✗"
    color = "\033[32m" if value else "\033[31m"
    reset = "\033[0m"
    print(f"  {color}{mark}{reset}  {label}")

def cmd_prepare() -> int:
    header("Checking dependencies")

    deps = {
        "python3":      (["python3", "--version"],              "python3"),
        "python3-venv": (["python3", "-c", "import venv"],     "python3-venv"),
        "setxkbmap":    (["which", "setxkbmap"],               "x11-xkb-utils"),
        "localectl":    (["which", "localectl"],               "systemd"),
    }

    missing_pkgs = []
    for name, (check_cmd, pkg) in deps.items():
        result = subprocess.run(check_cmd, capture_output=True)
        if result.returncode == 0:
            ok(f"{name} is available")
        else:
            warn(f"{name} is NOT available (package: {pkg})")
            missing_pkgs.append(pkg)

    if not missing_pkgs:
        ok("\nAll dependencies are satisfied.")
        return 0

    print()
    warn(f"Missing packages: {', '.join(missing_pkgs)}")
    try:
        answer = input("  Do you want to install them now? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        info("Non-interactive mode — skipping installation.")
        info(f"Run manually: sudo apt-get install -y {' '.join(missing_pkgs)}")
        return 0
    if answer == "y":
        info(f"Running: sudo apt-get install -y {' '.join(missing_pkgs)}")
        run(["sudo", "apt-get", "install", "-y"] + missing_pkgs)
        ok("Dependencies installed.")
    else:
        info("Skipping installation. Some commands may not work.")

    return 0

def cmd_install() -> int:
    require_sudo()
    header("Installing German (US Mix) keyboard layout")

    s = check_status()
    status = overall_status(s)

    if status == STATUS_OK and s["symbol_uptodate"]:
        ok("Layout is already fully installed and up-to-date.")
        info("Use 'make update' to force re-installation of the symbol file.")
        return 0

    if status == STATUS_PARTIAL:
        warn("Partial installation detected. Completing installation...")

    # 1. Copy symbol file
    if not s["symbol_file"] or not s["symbol_uptodate"]:
        info(f"Copying symbol file to {LAYOUT_DEST} ...")
        if LAYOUT_DEST.exists():
            backup_file(LAYOUT_DEST)
        shutil.copy2(LAYOUT_SRC, LAYOUT_DEST)
        LAYOUT_DEST.chmod(0o644)
        ok(f"Symbol file installed: {LAYOUT_DEST}")
    else:
        ok("Symbol file already present and up-to-date.")

    # 2. Register in base.extras.xml
    if not s["base_extras"]:
        info(f"Adding layout entry to {BASE_EXTRAS} ...")
        backup_file(BASE_EXTRAS)
        added = add_layout_to_xml(BASE_EXTRAS)
        ok("Entry added to base.extras.xml.") if added else ok("Entry already present in base.extras.xml.")
    else:
        ok("Entry already present in base.extras.xml.")

    # 3. Register in evdev.extras.xml
    if not s["evdev_extras"]:
        info(f"Adding layout entry to {EVDEV_EXTRAS} ...")
        backup_file(EVDEV_EXTRAS)
        added = add_layout_to_xml(EVDEV_EXTRAS)
        ok("Entry added to evdev.extras.xml.") if added else ok("Entry already present in evdev.extras.xml.")
    else:
        ok("Entry already present in evdev.extras.xml.")

    print()
    ok("Installation complete!")
    info("Please log out and log back in (or reboot) for the layout to appear in GNOME.")
    info("Then go to: Settings → Keyboard → Input Sources → Add → Search for 'German (US Mix)'")
    return 0

def cmd_update() -> int:
    require_sudo()
    header("Updating German (US Mix) keyboard layout symbol file")

    if not LAYOUT_SRC.exists():
        error(f"Source file not found: {LAYOUT_SRC}")
        return 1

    if LAYOUT_DEST.exists():
        if filecmp.cmp(LAYOUT_SRC, LAYOUT_DEST, shallow=False):
            ok("Symbol file is already up-to-date. No changes needed.")
            return 0
        info(f"Updating symbol file at {LAYOUT_DEST} ...")
        backup_file(LAYOUT_DEST)
    else:
        warn("Symbol file not yet installed. Running full install instead.")
        return cmd_install()

    shutil.copy2(LAYOUT_SRC, LAYOUT_DEST)
    LAYOUT_DEST.chmod(0o644)
    ok("Symbol file updated.")
    info("Please log out and log back in for changes to take effect.")
    return 0

def cmd_uninstall() -> int:
    require_sudo()
    header("Uninstalling German (US Mix) keyboard layout")

    s = check_status()
    if overall_status(s) == STATUS_NOT_INSTALLED:
        info("Layout is not installed. Nothing to do.")
        return 0

    # 1. Remove symbol file
    if s["symbol_file"]:
        info(f"Removing symbol file: {LAYOUT_DEST} ...")
        backup_file(LAYOUT_DEST)
        LAYOUT_DEST.unlink()
        ok("Symbol file removed.")
    else:
        info("Symbol file not found (already removed).")

    # 2. Remove from base.extras.xml
    if s["base_extras"]:
        info(f"Removing entry from {BASE_EXTRAS} ...")
        backup_file(BASE_EXTRAS)
        removed = remove_layout_from_xml(BASE_EXTRAS)
        ok("Entry removed from base.extras.xml.") if removed else warn("Entry not found in base.extras.xml.")
    else:
        info("Entry not present in base.extras.xml.")

    # 3. Remove from evdev.extras.xml
    if s["evdev_extras"]:
        info(f"Removing entry from {EVDEV_EXTRAS} ...")
        backup_file(EVDEV_EXTRAS)
        removed = remove_layout_from_xml(EVDEV_EXTRAS)
        ok("Entry removed from evdev.extras.xml.") if removed else warn("Entry not found in evdev.extras.xml.")
    else:
        info("Entry not present in evdev.extras.xml.")

    print()
    ok("Uninstallation complete.")
    info("Please log out and log back in for changes to take effect.")
    return 0

def cmd_load() -> int:
    import tempfile
    header("Temporarily loading German (US Mix) keyboard layout")

    if not LAYOUT_SRC.exists():
        error(f"Source layout file not found: {LAYOUT_SRC}")
        return 1

    info("Note: This does NOT require sudo and is only active for the current session.")
    info("      After logout the layout will revert to default.")
    info("      This does NOT appear in the GNOME layout menu.")

    # xkbcomp always prefers the system symbols dir over -I paths for layout
    # includes resolved by setxkbmap. Work around this by copying the local
    # symbol file to a temp dir and building the keymap directly with xkbcomp.
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_symbols = Path(tmpdir) / "symbols"
        tmp_symbols.mkdir()
        shutil.copy2(LAYOUT_SRC, tmp_symbols / LAYOUT_NAME)

        info(f"Staging layout in temp dir: {tmpdir}")

        # Generate the keymap description
        result = run(
            ["setxkbmap", "-I", tmpdir, "-layout", LAYOUT_NAME, "-print"],
            check=False, capture=True
        )

        if result.returncode != 0:
            error("setxkbmap failed to generate keymap description:")
            error(result.stderr)
            return 1

        info("Keymap description generated. Compiling and loading...")

        # Compile and load directly into the X server
        xkbcomp_proc = subprocess.run(
            ["xkbcomp", f"-I{tmpdir}", "-", os.environ.get("DISPLAY", ":0")],
            input=result.stdout,
            capture_output=True,
            text=True,
        )

        errors = [l for l in xkbcomp_proc.stderr.splitlines() if "Error" in l]
        warnings = [l for l in xkbcomp_proc.stderr.splitlines()
                    if "Warning" in l and "XF86" not in l and "not found in" not in l]

        if warnings:
            for w in warnings:
                warn(w.strip())

        if xkbcomp_proc.returncode != 0 or errors:
            for e in errors:
                error(e.strip())
            error("Failed to load layout. Try 'sudo make install' first, then 'make load'.")
            return 1

    ok("Layout loaded successfully for this session.")
    info("Test: press Alt+a → ä, Alt+o → ö, Alt+u → ü, Alt+s → ß")
    info("      Shift+Alt+a → Ä, Shift+Alt+o → Ö, Shift+Alt+u → Ü")
    return 0

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Installer for German (US Mix) keyboard layout",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "command",
        choices=["check", "prepare", "install", "update", "uninstall", "load"],
        help="Command to execute",
    )
    args = parser.parse_args()

    commands = {
        "check": cmd_check,
        "prepare": cmd_prepare,
        "install": cmd_install,
        "update": cmd_update,
        "uninstall": cmd_uninstall,
        "load": cmd_load,
    }

    return commands[args.command]()

if __name__ == "__main__":
    sys.exit(main())
