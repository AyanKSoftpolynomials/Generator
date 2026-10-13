"""Readable errors for the video pipeline.

Scripts catch ``LMSError`` and print only its message (plus the suggested
fix), not a Python traceback.
"""


class LMSError(Exception):
    """A problem the user can fix. ``fix`` is an optional "do this" hint;
    ``line`` the line of animation.py the problem is on, when known."""

    def __init__(self, message: str, fix: str | None = None, line: int | None = None):
        super().__init__(message)
        self.message = message
        self.fix = fix
        self.line = line

    def __str__(self) -> str:
        return f"{self.message}\n\n{self.fix}" if self.fix else self.message
