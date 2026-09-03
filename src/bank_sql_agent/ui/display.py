"""
توابع نمایش مرحله‌به‌مرحله (آیکون/رنگ) و جلوه‌ی تایپ.
"""

import time

from .colors import C

TYPE_DELAY = 0.012


def stage(icon: str, text: str, color: str = C.CYAN) -> None:
    print(f"{color}{icon}  {text}{C.RESET}")


def print_code_block(text: str, color: str = C.DIM) -> None:
    print(f"{color}   {text}{C.RESET}")


def typewriter_print(text: str, color: str = "", delay: float = TYPE_DELAY) -> None:
    if color:
        print(color, end="")
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    if color:
        print(C.RESET, end="")
    print()
