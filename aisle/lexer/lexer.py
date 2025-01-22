"""Contains lexer implementation."""

from collections.abc import Sequence

from aisle.lexer.exceptions import (
    UnexpectedCharacterException,
    StringNotClosedException,
    IncompleteUnicodeQuadException,
)
from aisle.lexer.tokens import (
    Token,
    TokenType,
    RESERVED_STRINGS,
    KEYWORDS,
)


class Lexer:
    def __init__(
            self,
            source: str,
            tab_size: int = 4,
    ) -> None:
        self._src = _norm_newlines(source)
        self._lines = self._src.splitlines()
        self._i = 0
        self._start = 0
        self._line = 1
        self._line_start = 0
        self._tokens = []
        self._tab_size = tab_size

    @property
    def _at_end(self):
        """Check if reached end of source."""
        return self._i >= len(self._src)

    def _next(self) -> str | None:
        if self._i >= len(self._src):
            return None
        self._i += 1
        return self._src[self._i - 1]

    @property
    def _current(self) -> str | None:
        return None if self._at_end else self._src[self._i]

    def _add_token(
            self,
            token_type: TokenType,
            lexeme: str | None = None
    ) -> None:
        token = Token(
            token_type,
            lexeme or self._src[self._start:self._i],
            self._line
        )
        self._start = self._i
        self._tokens.append(token)

    def _match(self, pattern: str) -> str | None:
        if self._at_end:
            return None
        src = self._src[self._i:]
        if src.startswith(pattern):
            self._i += len(pattern)
            return pattern
        return None

    def _error(self, exc_type, *args, **kwargs) -> None:
        raise exc_type(
            *args,
            **kwargs,
            source=self._src,
            line=self._line
        )

    def scan(self) -> Sequence[Token]:
        while not self._at_end:
            self._scan_token()
        return self._tokens

    def _scan_token(self) -> None:
        c = self._next()
        match c:
            case "=":
                self._add_token(TokenType.ASSIGN)
            case ":":
                self._add_token(TokenType.COLON)
            case "(":
                self._add_token(TokenType.LPAR)
            case ")":
                self._add_token(TokenType.RPAR)
            case "[":
                self._add_token(TokenType.LBRACKET)
            case "]":
                self._add_token(TokenType.RBRACKET)
            case "-":
                if self._match("->"):
                    self._add_token(TokenType.ARROW_R)
                elif self._match("--"):
                    self._add_token(TokenType.ARROW_NO_DIR)
                else:
                    self._error(UnexpectedCharacterException, self._current)
            case "<":
                if self._match("->"):
                    self._add_token(TokenType.ARROW_BI_DIR)
                elif self._match("--"):
                    self._add_token(TokenType.ARROW_L)
                else:
                    self._error(UnexpectedCharacterException, self._current)
            case "\n":
                self._add_token(TokenType.NEWLINE)
                self._line += 1
                self._line_start = self._i
            case " ":
                if self._match(" " * (self._tab_size - 1)):
                    self._add_token(TokenType.INDENT)
                else:
                    self._start = self._i
            case "\t":
                self._add_token(TokenType.INDENT)
            case '"':
                self._scan_string()
            case _:
                self._i -= 1
                self._scan_text()

    def _scan_string(self) -> None:
        text = ""
        while not self._at_end and self._current != '"':
            if self._current == "\\":
                text += self._scan_escape_seq()
            else:
                text += self._current
                self._i += 1
        if not (not self._at_end and self._current == '"'):
            self._error(StringNotClosedException)
        self._i += 1
        self._add_token(TokenType.TEXT, text)

    def _scan_escape_seq(self) -> str:
        self._next()
        control = self._next()
        match control:
            case "r":
                return "\r"
            case "f":
                return "\f"
            case "n":
                return "\n"
            case "t":
                return "\t"
            case '"':
                return '"'
            case "\\":
                return "\\"
            case "u":
                code = int(self._scan_unicode_quad(), 16)
                return chr(code)
        self._error(UnexpectedCharacterException, char=control)

    def _scan_unicode_quad(self) -> str:
        code = ""
        for _ in range(4):
            c = self._next()
            if c is None:
                self._error(IncompleteUnicodeQuadException)
            if c not in "0123456789abcdefABCDEF":
                self._error(IncompleteUnicodeQuadException)
            code += c
        return code

    def _scan_text(self) -> None:
        subindent_level = self._i - self._line_start
        text = ""
        while not self._at_end:
            if self._current == "\\":
                text += self._scan_escape_seq()
            elif self._current == "\n":
                self._line += 1
                if not self._next_line_on_same_level(subindent_level):
                    break
                text += self._current
                text += " "*subindent_level  # Retain all indentation
                self._i += subindent_level + 1
            else:
                text += self._current
                self._i += 1
            if _get_reserved_string_at_end(text):
                break
        reserved = _get_reserved_string_at_end(text)
        if reserved and len(reserved) != len(text):
            self._i -= len(reserved)
            text = text.removesuffix(reserved)

        # Return all extra indentation and newline symbols back
        stripped_text = text.strip()
        suffix_start = text.index(stripped_text) + len(stripped_text)
        suffix_length = len(text) - suffix_start
        self._i -= suffix_length
        # Update line count accordingly
        self._line -= text[suffix_start:].count("\n")
        # Remove unnecessary indentation
        text = _remove_indentation(text, subindent_level)

        if text in KEYWORDS:
            self._add_token(TokenType.KEYWORD, text.strip())
        else:
            self._add_token(TokenType.TEXT, text.strip())

    def _next_line_on_same_level(self, subindent_level: int) -> bool:
        return self._lines[self._line - 1].startswith(" " * subindent_level)


def _get_reserved_string_at_end(text: str) -> str | None:
    if text in RESERVED_STRINGS:
        return text
    for string in RESERVED_STRINGS:
        if _should_be_split(text, string):
            return string
    return None


def _should_be_split(string: str, reserved: str) -> bool:
    if not string.endswith(reserved):
        return False
    trunk = string.removesuffix(reserved)
    if not reserved.isalnum():
        return True
    return trunk[-1] in "\n\r\t "


def _norm_newlines(text: str) -> str:
    """Replace all CRLF with LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _remove_indentation(text: str, amount: int) -> str:
    lines = text.splitlines()
    prefix = " "*amount
    for i, line in enumerate(lines):
        lines[i] = line.removeprefix(prefix)
    return "\n".join(lines)

"""
tech = fdffd

"""