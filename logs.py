import argparse
import colorsys
import random
import re

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

BOLD = "\033[1m"
DIM = "\033[2m"

BOLD_RED = "\033[1;91m"
BOLD_GREEN = "\033[1;92m"
BOLD_YELLOW = "\033[1;93m"
BOLD_BLUE = "\033[1;94m"
BOLD_MAGENTA = "\033[1;95m"
BOLD_CYAN = "\033[1;96m"
BOLD_WHITE = "\033[1;97m"

def color_from_hex(hex_code, bold=False, italic=False, underline=False, strike=False, invert=False):
    hex_code = hex_code.lstrip('#')
    r, g, b = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
    codes = []
    if bold:      codes.append("1")
    if italic:    codes.append("3")
    if underline: codes.append("4")
    if invert:    codes.append("7")
    if strike:    codes.append("9")
    codes.append(f"38;2;{r};{g};{b}")
    return f"\033[{';'.join(codes)}m"


def random_color():
    h = random.random()
    s = random.uniform(0.6, 1.0)
    v = random.uniform(0.8, 1.0)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    hex_code = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    return color_from_hex(hex_code, bold=True)


class Logger:
    def __init__(self, script, color=None):
        self.script = script
        self.color = color or random_color()

    def _highlight(self, message, highlight_color, base_color=""):
        def replacer(match):
            text = match.group(0)
            return f"{highlight_color}{text}{RESET}{base_color}"

        return re.sub(r"(`[^`]+`|'[^']+')", replacer, message)

    def log(self, message, script=None):
        message = self._highlight(message, CYAN)
        print(f"{self.color}[{script or self.script}]{RESET} {message}{RESET}")
        
    def success(self, message, script=None):
        message = self._highlight(message, CYAN, GREEN)
        print(f"{self.color}[{script or self.script}]{RESET}{GREEN} {message}{RESET}")

    def warn(self, message, script=None):
        message = self._highlight(message, RESET, YELLOW)
        print(f"{self.color}[{script or self.script}]{RESET}{YELLOW} {message}{RESET}")

    def error(self, message):
        message = self._highlight(message, YELLOW, RED)
        print(f"{BOLD_RED}[ERROR]{RESET}{RED} An error has occured in {self.script}:\n    {message}{RESET}")