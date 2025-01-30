"""Contains lexer exceptions."""


class LexerException(Exception):
    """Base class for lexer exceptions."""

    def __init__(self, message: str, source: str, line: int) -> None:
        """Create exception."""
        self._msg = message
        self._src = source
        self._line = line

    @property
    def formatted_message(self) -> str:
        """Create beautiful representation of exception."""
        line_str = self._src.splitlines()[self._line - 1]
        line_str = f"{self._line} |  {line_str}"
        return (
            f"{self._msg}\n"
            f"At line {self._line}:\n"
            f"{line_str}"
        )

    def __str__(self):
        """Convert to string repr."""
        return self.formatted_message


class UnexpectedCharacterException(LexerException):
    """Raised when encountered unexpected character."""

    def __init__(self, char: str, source: str, line: int) -> None:
        """Create exception and message."""
        super().__init__(f"Unexpected character '{char}'", source, line)


class StringNotClosedException(LexerException):
    """Raised when string not closed with a quote."""

    def __init__(self, source: str, line: int) -> None:
        """Create exception and message."""
        super().__init__('String not closed with "', source, line)


class IncompleteUnicodeQuadException(LexerException):
    r"""Raise when \u escape found, but the code is invalid."""

    def __init__(self, source: str, line: int) -> None:
        """Create exception and message."""
        super().__init__(
            r"\u escape found, but code is incomplete",
            source,
            line
        )
