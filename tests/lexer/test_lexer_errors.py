import pytest

from aisle.lexer.lexer import Lexer
from aisle.lexer.exceptions import (
    UnexpectedCharacterException,
    StringNotClosedException,
    IncompleteUnicodeQuadException
)


@pytest.mark.parametrize(
    "src",
    [
        "-",
        "<",
        '"\\_"',
    ]
)
def test_unexpected_character(src):
    lexer = Lexer(src)
    with pytest.raises(UnexpectedCharacterException):
        lexer.scan()


@pytest.mark.parametrize(
    "src",
    [
        '"'
    ]
)
def test_string_not_closed(src):
    lexer = Lexer(src)
    with pytest.raises(StringNotClosedException):
        lexer.scan()


@pytest.mark.parametrize(
    "src",
    [
        '"\\u_"',
        '"\\u2"',
        '"\\u',
    ]
)
def test_bad_unicode_u_quad(src):
    lexer = Lexer(src)
    with pytest.raises(IncompleteUnicodeQuadException):
        lexer.scan()
