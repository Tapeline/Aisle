"""Parser tests."""

import pytest

from aisle.lexer.impl.lexer import Lexer
from aisle.parser.exceptions import (
    UnexpectedEndError,
    UnexpectedKeywordTokenError,
    UnexpectedTokenError,
)
from aisle.parser.impl.parser import Parser


@pytest.mark.parametrize(
    "src",
    [
        "scope context test\n"
        "system test:\n"
        "    links:\n"
        "        NOT AN ARROW",

        "(",

        "scope legend test\n"
        "-->",

        "scope legend test\n"
        "[bad selector]",

        "scope context test\n"
        "actor test:\n"
        "    deployment",

        "scope context test\n"
        "system test:\n"
        "    system = invalid state",

        "scope context test\n"
        "system test:\n"
        "    (",

        "scope containers test\n"
        "service test:\n"
        "    tech (",

        "scope deployment test\n"
        "deployment test:\n"
        "    (",

        "scope legend test\n"
        "[= selector]:\n"
        "    (",
    ],
)
def test_unexpected_token(src):
    """Test that unexpected tokens raise an exception."""
    lexer = Lexer(src)
    tokens = lexer.scan()
    parser = Parser(src, tokens)
    with pytest.raises(UnexpectedTokenError):
        parser.parse()


@pytest.mark.parametrize(
    "src",
    [
        "scope invalid-scope",

        "scope containers test\n"
        "deployment",
    ],
)
def test_unexpected_keyword(src):
    """Test that unexpected keywords raise an exception."""
    lexer = Lexer(src)
    tokens = lexer.scan()
    parser = Parser(src, tokens)
    with pytest.raises(UnexpectedKeywordTokenError):
        parser.parse()


@pytest.mark.parametrize(
    "src",
    [
        "scope legend test\n"
        "[",
    ],
)
def test_unexpected_end(src):
    """Test that unexpected EOF raises an exception."""
    lexer = Lexer(src)
    tokens = lexer.scan()
    parser = Parser(src, tokens)
    with pytest.raises(UnexpectedEndError):
        parser.parse()
