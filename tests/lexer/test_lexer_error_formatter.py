"""Contains lexer tests."""

import pytest

from aisle.lexer.exceptions import (
    IncompleteUnicodeQuadError,
    StringNotClosedError,
    UnexpectedCharacterError,
)


@pytest.mark.parametrize(
    ("err", "expected"),
    [
        (
            UnexpectedCharacterError("X", "abc\nX\nabc", 2),
            "Unexpected character 'X'\n"
            "At line 2:\n"
            "2 |  X",
        ),
        (
            IncompleteUnicodeQuadError("abc\n\\uAB\nabc", 2),
            "\\u escape found, but code is incomplete\n"
            "At line 2:\n"
            "2 |  \\uAB",
        ),
        (
            StringNotClosedError('abc\n"\nabc', 2),
            'String not closed with "\n'
            'At line 2:\n'
            '2 |  "',
        ),
    ],
)
def test_error_format(err, expected):
    """Test that lexer errors are formatted correctly."""
    assert str(err) == expected
