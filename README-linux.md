# Linux Keyboard Layout

## Problem
Writing on a US keyboard is ideal for software development, but switching layouts to type German umlauts (ä, ö, ü, ß) is cumbersome.

## Solution
This layout is based on the standard US keyboard. German umlauts are accessible by holding the `ALT` key and pressing the corresponding keys where these characters would normally be on a German keyboard. Shift + ALT allows typing uppercase umlauts.

## Installation

### Ubuntu 22.04/24.04

1. Copy the layout file to the X11 keyboard layouts directory:
   ```bash
   sudo cp linux/de-en-mix /usr/share/X11/xkb/symbols/
   ```

2. Edit the `/usr/share/X11/xkb/rules/base.extras.xml` file to add the layout:
   - Open the file with sudo privileges:
     ```bash
     sudo nano /usr/share/X11/xkb/rules/base.extras.xml
     ```
   - Add the following entry under the `<layoutList>` section:
     ```xml
     <layout>
       <configItem>
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

3. Reconfigure the XKB data:
   ```bash
   sudo dpkg-reconfigure xkb-data
   ```

4. Restart your session or reboot.

5. Select the layout in your system settings:
   - Go to Settings > Keyboard > Input Sources
   - Add the "German (US Mix)" layout

## Usage
- Use the standard US keyboard layout.
- Press `ALT` + `[aeou]` to type ä, ö, ü.
- Press `ALT` + `s` to type ß.
- Press `SHIFT` + `ALT` + `[AEOU]` to type Ä, Ö, Ü.

## Development
- Edit the `linux/de-en-mix` file to modify the layout.
- Test changes by reloading the X11 configuration or restarting your session.

## License
- MIT License (see `LICENSE` file).