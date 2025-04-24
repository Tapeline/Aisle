"""Contains parser tests."""

import pytest

from aisle.lexer.exceptions import (
    IncompleteUnicodeQuadError,
    StringNotClosedError,
    UnexpectedCharacterError,
)
from aisle.lexer.impl.lexer import Lexer


@pytest.mark.parametrize(
    "src",
    [
        "-",
        "<",
        '"\\_"',
    ],
)
def test_unexpected_character(src):
    """Test that unexpected characters raise an exception."""
    lexer = Lexer(src)
    with pytest.raises(UnexpectedCharacterError):
        lexer.scan()


@pytest.mark.parametrize(
    "src",
    [
        '"',
    ],
)
def test_string_not_closed(src):
    """Test that unclosed strings raise an exception."""
    lexer = Lexer(src)
    with pytest.raises(StringNotClosedError):
        lexer.scan()


@pytest.mark.parametrize(
    "src",
    [
        '"\\u_"',
        '"\\u2"',
        '"\\u',
    ],
)
def test_bad_unicode_u_quad(src):
    r"""Test that bad \u escapes raise an exception."""
    lexer = Lexer(src)
    with pytest.raises(IncompleteUnicodeQuadError):
        lexer.scan()
