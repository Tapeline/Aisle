import pytest

from aisle.lexer.exceptions import (
    UnexpectedCharacterException,
    IncompleteUnicodeQuadException,
    StringNotClosedException,
)


@pytest.mark.parametrize(
    "err,expected",
    [
        (
            UnexpectedCharacterException("X", "abc\nX\nabc", 2),
            "Unexpected character 'X'\n"
            "At line 2:\n"
            "2 |  X"
        ),
        (
            IncompleteUnicodeQuadException("abc\n\\uAB\nabc", 2),
            "\\u escape found, but code is incomplete\n"
            "At line 2:\n"
            "2 |  \\uAB"
        ),
        (
            StringNotClosedException('abc\n"\nabc', 2),
            'String not closed with "\n'
            'At line 2:\n'
            '2 |  "'
        ),
    ]
)
def test_error_format(err, expected):
    assert str(err) == expected
