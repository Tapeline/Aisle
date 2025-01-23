"""Parser tests."""

import pytest

from aisle.lexer.tokens import Token, TokenType
from aisle.parser.exceptions import (
    UnexpectedEndException,
    UnexpectedKeywordTokenException,
)


@pytest.mark.parametrize(
    ("err", "expected"),
    [
        (
            UnexpectedKeywordTokenException(
                ["kw_a", "kw_b", "kw_c"],
                Token(TokenType.KEYWORD, "kw_d", 2),
                "...\nkw_d\n...",
                2,
            ),
            "Parser: Expected one of ['kw_a', 'kw_b', 'kw_c'] "
            "keywords, but got 'kw_d'\n"
            "At line 2:\n"
            "2 |  kw_d",
        ),
        (
            UnexpectedEndException(
                "kw_a",
                "abc\n\n...",
                3,
            ),
            "Parser: Expected kw_a, but got end of file\n"
            "At line 3:\n"
            "3 |  ...",
        ),
    ],
)
def test_error_format(err, expected):
    """Test that parser exceptions are formatted correctly."""
    assert str(err) == expected
