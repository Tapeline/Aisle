"""Contains lexer exceptions."""


class LexerException(Exception):
    def __init__(self, message: str, source: str, line: int) -> None:
        self._msg = message
        self._src = source
        self._line = line

    @property
    def formatted_message(self):
        line_str = self._src.splitlines()[self._line - 1]
        line_str = f"{self._line} |  {line_str}"
        return (
            f"{self._msg}\n"
            f"At line {self._line}:\n"
            f"{line_str}"
        )

    def __str__(self):
        return self.formatted_message


class UnexpectedCharacterException(LexerException):
    def __init__(self, char: str, source: str, line: int) -> None:
        super().__init__(f"Unexpected character '{char}'", source, line)


class StringNotClosedException(LexerException):
    def __init__(self, source: str, line: int) -> None:
        super().__init__('String not closed with "', source, line)


class IncompleteUnicodeQuadException(LexerException):
    def __init__(self, source: str, line: int) -> None:
        super().__init__("\\u escape found, but code is incomplete", source, line)
