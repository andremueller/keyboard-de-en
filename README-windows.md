# Keyboard Layouts

## Problem

Writing on an US keyboard is nice for software development. All special characters are easily reachable. However, if we need to write sometimes German accents/umlauts like `öäüß` it is quite difficult to switch forth and back between different keyboard layouts.

Therefore a keyboard layouts was created rooted from a standard US keyboard with no dead keys. Only the umlauts are at their original position of the keyboard when pressing the ALT-GR (right), or CTRL-ALT (left) keys. In addition the dead keys for French accents were added to their original DE keyboard position (one key left of the backspace). These are reached as well with the ALT-GR key.

## Installation

### Windows

1. Install the **Microsoft Keyboard Layout Creator** tool directly from the home page. See <https://www.microsoft.com/en-us/download/details.aspx?id=102134>
2. Open the tool and load the given `.klc` file from the `windows` directory of this repository.
3. Press Project/Build DLL and Setup Package.
4. Install the created setup package.
5. Reboot your system.
6. Go to your Time & language/Language & region/Options. Set to US and choose in "Keyboards" the "US - German Accents".

