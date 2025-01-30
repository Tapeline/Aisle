"""Contains lexer implementation."""

from collections.abc import Sequence

from aisle.lexer.exceptions import (
    IncompleteUnicodeQuadException,
    StringNotClosedException,
    UnexpectedCharacterException,
)
from aisle.lexer.interfaces import AbstractLexer
from aisle.lexer.tokens import (
    KEYWORDS,
    RESERVED_STRINGS,
    Token,
    TokenType,
)


class Lexer(AbstractLexer):
    """Lexer implementation."""

    def __init__(
            self,
            source: str,
            tab_size: int = 4,
    ) -> None:
        """
        Create lexer.

        Args:
            source: source code
            tab_size: target tab size in spaces

        """
        self._src = _norm_newlines(source)
        self._lines = self._src.splitlines()
        self._i = 0
        self._start = 0
        self._line = 1
        self._line_start = 0
        self._tokens: list[Token] = []
        self._tab_size = tab_size

    @property
    def _at_end(self) -> bool:
        """Check if reached end of source."""
        return self._i >= len(self._src)

    def _next(self) -> str | None:
        """Get current and advance to next character."""
        if self._i >= len(self._src):
            return None
        self._i += 1
        return self._src[self._i - 1]

    @property
    def _current(self) -> str | None:
        """Current character."""
        return None if self._at_end else self._src[self._i]

    def _add_token(
            self,
            token_type: TokenType,
            lexeme: str | None = None,
    ) -> None:
        """Add token to token list."""
        token = Token(
            token_type,
            lexeme or self._src[self._start:self._i],
            self._line,
        )
        self._start = self._i
        self._tokens.append(token)

    def _match(self, pattern: str) -> str | None:
        """Consume string pattern if possible."""
        if self._at_end:
            return None
        src = self._src[self._i:]
        if src.startswith(pattern):
            self._i += len(pattern)
            return pattern
        return None

    def _error(self, exc_type, *args, **kwargs) -> None:
        """Raise exception at current position."""
        raise exc_type(
            *args,
            **kwargs,
            source=self._src,
            line=self._line,
        )

    def scan(self) -> Sequence[Token]:
        """Tokenize source code."""
        while not self._at_end:
            self._scan_token()
        return self._tokens

    def _scan_token(self) -> None:  # noqa: C901
        """Scan single token."""
        char = self._next()
        match char:
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
        """Continue scanning as string."""
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

    def _scan_escape_seq(self) -> str:  # type: ignore
        """Scan string escape sequence."""
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
        self._error(  # noqa: RET503 (no return -> exception is raised)
            UnexpectedCharacterException,
            char=control
        )

    def _scan_unicode_quad(self) -> str:
        r"""Scan \uXXXX escape sequence."""
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
        """
        Scan unquoted text.

        Text can be multiline. If the first line started ``n`` chars from
        line start, then all lines that are preceded by at least ``n``
        whitespaces will be treated as part of that text. Text is ended
        when line is preceded by less than ``n`` whitespaces or a keyword
        or other reserved character (``()[]=":``) encountered.

        Example:
            my_text_param = This is a very long
                            text that is wrapped:
                                that is also accepted.

        """
        subindent_level = self._i - self._line_start
        text = ""
        while not self._at_end:
            if self._current == "\\":
                text += self._scan_escape_seq()
            elif self._current == "\n":
                self._line += 1
                text += self._next()  # Consume newline
                if not self._next_line_on_same_level(subindent_level):
                    break
                text += " " * subindent_level  # Retain all indentation
                self._i += subindent_level
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
        text = _remove_indentation(text, subindent_level).strip()

        if text in KEYWORDS:
            # Handle edge case: 'deployment' being treated as 'deploy ment'
            keyword = _get_longest_keyword_prefix(
                self._src[self._i - len(text):]
            )
            self._i += len(keyword) - len(text)
            self._add_token(TokenType.KEYWORD, keyword)
        else:
            self._add_token(TokenType.TEXT, text)

    def _next_line_on_same_level(self, subindent_level: int) -> bool:
        """Check if current line is preceded by at least n whitespaces."""
        if self._line - 1 >= len(self._lines):
            return False
        return self._lines[self._line - 1].startswith(" " * subindent_level)


def _get_reserved_string_at_end(text: str) -> str | None:
    """Get (if possible) a trailing reserved character sequence."""
    if text in RESERVED_STRINGS:
        return text
    for string in RESERVED_STRINGS:
        if _should_be_split(text, string):
            return string
    return None


def _should_be_split(string: str, reserved: str) -> bool:
    """Check if reserved character sequence is not a part of word."""
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
    """Remove indentation of ``amount`` spaces on every line."""
    lines = text.splitlines()
    prefix = " " * amount
    for i, line in enumerate(lines):
        lines[i] = line.removeprefix(prefix)
    return "\n".join(lines)


def _get_longest_keyword_prefix(text: str) -> str | None:
    """Get the longest keyword starting that text."""
    keywords = sorted(KEYWORDS, key=len, reverse=True)
    for keyword in keywords:
        if text.startswith(keyword):
            return keyword
    return None  # pragma: no cover
