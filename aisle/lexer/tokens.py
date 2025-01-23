"""Contains token definitions."""

import enum
from dataclasses import dataclass
from typing import Final


class TokenType(enum.Enum):
    """All possible token types."""

    KEYWORD = enum.auto()
    TEXT = enum.auto()
    COLON = enum.auto()
    ASSIGN = enum.auto()
    ARROW_R = enum.auto()
    ARROW_L = enum.auto()
    ARROW_BI_DIR = enum.auto()
    ARROW_NO_DIR = enum.auto()
    LPAR = enum.auto()
    RPAR = enum.auto()
    LBRACKET = enum.auto()
    RBRACKET = enum.auto()
    INDENT = enum.auto()
    NEWLINE = enum.auto()


@dataclass
class Token:
    """Represents a single token."""

    type: TokenType
    lexeme: str
    line: int

    def is_keyword(self, pattern: str) -> bool:
        """Check if this token is a specific keyword."""
        return self.type == TokenType.KEYWORD and self.lexeme == pattern

    def __repr__(self):
        """Convert to string repr."""
        return f"{self.type.name}{self.lexeme}"

    @property
    def human_readable_repr(self):
        """Get beautiful version of __repr__."""
        return f"{self.line}\t| {self.type.name: <10}    {self.lexeme}"


KEYWORDS: Final[frozenset[str]] = frozenset((
    "scope",
    "context",
    "system",
    "external",
    "links",
    "over",
    "tech",
    "containers",
    "service",
    "deployment",
    "deploy",
    "legend",
    "actor",
    "project",
))

RESERVED_STRINGS: Final[frozenset[str]] = frozenset((
    *KEYWORDS,
    "-->",
    "<--",
    "<->",
    "---",
    *set('()[]:="'),
))
