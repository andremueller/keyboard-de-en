# AGENTS.md

## Repository Overview
- This repository contains custom keyboard layouts for macOS, Windows, and Linux designed for German software developers who prefer the US keyboard layout but need occasional access to German umlauts (ä, ö, ü, ß).

## Key Files
- `macos/EN_DE_Mix_Keylayout.keylayout`: The custom keyboard layout file for macOS.
- `windows/EN-DE-Accents.klc`: The custom keyboard layout file for Windows.
- `linux/de-en-mix`: The custom keyboard layout file for Linux.

## Installation
- **macOS**: Use the [Ukulele software](https://software.sil.org/ukelele/) to open and install the `macos/EN_DE_Mix_Keylayout.keylayout` file.
- **Windows**: Use the [Microsoft Keyboard Layout Creator](https://www.microsoft.com/en-us/download/details.aspx?id=102134) to open and install the `windows/EN-DE-Accents.klc` file.
- **Linux**: Copy the `linux/de-en-mix` file to `/usr/share/X11/xkb/symbols/` and reconfigure the X11 keyboard data.

## Usage
- The layout is based on the US keyboard layout.
- Umlauts (ä, ö, ü, ß) can be typed by holding the `ALT` key (macOS/Linux) or `ALT-GR`/`CTRL-ALT` keys (Windows) and pressing the corresponding keys where these characters would normally be on a German keyboard.

## Development
- No build or test commands are required for this repository.
- Changes to the keyboard layout can be made using the respective software tools (Ukulele for macOS, Microsoft Keyboard Layout Creator for Windows, or editing the XKB file for Linux).

## License
- MIT License (see `LICENSE` file).