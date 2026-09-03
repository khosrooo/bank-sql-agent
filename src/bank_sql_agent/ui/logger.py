"""
لاگر Tee: چاپ هم‌زمان روی ترمینال (با رنگ) و در فایل لاگ (بدون کد رنگی، تمیز).
"""

import re

ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


class TeeLogger:
    """چاپ هم‌زمان روی ترمینال (با رنگ) و در فایل لاگ (بدون کد رنگی، تمیز)."""

    def __init__(self, terminal_stream, log_file):
        self._terminal = terminal_stream
        self._log_file = log_file

    def write(self, message: str) -> None:
        self._terminal.write(message)
        self._log_file.write(ANSI_PATTERN.sub("", message))
        self._log_file.flush()

    def flush(self) -> None:
        self._terminal.flush()
        self._log_file.flush()
