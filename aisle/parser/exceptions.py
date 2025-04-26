"""Contains all parser exceptions."""

from collections.abc import Collection
from typing import Final

from aisle.exceptions import AisleError
from aisle.lexer.tokens import Token, TokenType


class ParserError(AisleError):
    """Base for all parser exceptions."""

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
            f"Parser: {self._msg}\n"
            f"At line {self._line}:\n"
            f"{line_str}"
        )

    def __str__(self) -> str:
        """Convert to string repr."""
        return self.formatted_message


class UnexpectedTokenError(ParserError):
    """Raised when an unexpected token is encountered."""

    default_message: Final[str] = (
        "Expected one of {expected} tokens, but got '{got.lexeme}'"
    )

    def __init__(
            self,
            source: str,
            line: int,
            expected: Collection[TokenType] | None = None,
            got: Token | None = None,
            message: str | None = None,
    ) -> None:
        """Create exception and format message."""
        super().__init__(
            (message or self.default_message).format(
                expected=expected,
                got=got,
            ),
            source,
            line,
        )


class UnexpectedKeywordTokenError(ParserError):
    """Raised when expected a keyword, but found something other."""

    default_message: Final[str] = (
        "Expected one of {expected} keywords, but got '{got.lexeme}'"
    )

    def __init__(
            self,
            expected: Collection[str] | None,
            got: Token | None,
            source: str,
            line: int,
            message: str | None = None,
    ) -> None:
        """Create exception."""
        super().__init__(
            (message or self.default_message).format(
                expected=expected,
                got=got,
            ),
            source,
            line,
        )


class UnexpectedEndError(ParserError):
    """Raised when expected some token, but got end of file."""

    default_message: Final[str] = "Expected {expected}, but got end of file"

    def __init__(
            self,
            expected: str,
            source: str,
            line: int,
            message: str | None = None,
    ) -> None:
        """Create exception."""
        super().__init__(
            (message or self.default_message).format(
                expected=expected,
            ),
            source,
            line,
        )
